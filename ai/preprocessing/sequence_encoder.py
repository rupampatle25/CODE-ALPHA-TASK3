import json
import os
from typing import List, Dict, Tuple, Optional
import numpy as np
from ai.preprocessing.midi_parser import MidiNoteEvent

PAD_TOKEN = "<PAD>"
START_TOKEN = "<START>"
END_TOKEN = "<END>"

class MusicSequenceEncoder:
    """
    Encodes MidiNoteEvent sequences into discrete vocabulary tokens and training samples (X, y).
    """

    def __init__(self, step_size: float = 0.25):
        self.step_size = step_size  # 16th note grid
        self.token_to_id: Dict[str, int] = {
            PAD_TOKEN: 0,
            START_TOKEN: 1,
            END_TOKEN: 2,
        }
        self.id_to_token: Dict[int, str] = {
            0: PAD_TOKEN,
            1: START_TOKEN,
            2: END_TOKEN,
        }

    @property
    def vocab_size(self) -> int:
        return len(self.token_to_id)

    def notes_to_tokens(self, notes: List[MidiNoteEvent]) -> List[str]:
        """
        Converts a chronologically sorted list of MidiNoteEvents into token strings.
        Includes REST tokens when there is a gap between notes.
        """
        tokens: List[str] = [START_TOKEN]
        if not notes:
            tokens.append(END_TOKEN)
            return tokens

        current_time = 0.0

        for note in notes:
            # Check for rest gap
            gap = note.start_time - current_time
            if gap >= self.step_size:
                rest_steps = int(round(gap / self.step_size))
                tokens.append(f"REST_{rest_steps}")

            # Note token with pitch and quantized duration steps
            dur_steps = max(1, int(round(note.duration / self.step_size)))
            tokens.append(f"NOTE_{note.pitch}_{dur_steps}")

            current_time = max(current_time, note.start_time + note.duration)

        tokens.append(END_TOKEN)
        return tokens

    def tokens_to_notes(self, tokens: List[str]) -> List[MidiNoteEvent]:
        """
        Converts a list of token strings back into MidiNoteEvents.
        """
        notes: List[MidiNoteEvent] = []
        current_time = 0.0

        for token in tokens:
            if token in (PAD_TOKEN, START_TOKEN, END_TOKEN):
                continue
            elif token.startswith("REST_"):
                parts = token.split("_")
                steps = int(parts[1]) if len(parts) > 1 else 1
                current_time += steps * self.step_size
            elif token.startswith("NOTE_"):
                parts = token.split("_")
                if len(parts) >= 3:
                    pitch = int(parts[1])
                    dur_steps = int(parts[2])
                    duration = dur_steps * self.step_size
                    notes.append(MidiNoteEvent(
                        pitch=pitch,
                        start_time=current_time,
                        duration=duration,
                        velocity=75,
                    ))
                    current_time += duration

        return notes

    def build_vocab(self, all_token_sequences: List[List[str]]) -> None:
        """
        Builds the token_to_id and id_to_token mapping from training sequences.
        """
        for seq in all_token_sequences:
            for token in seq:
                if token not in self.token_to_id:
                    idx = len(self.token_to_id)
                    self.token_to_id[token] = idx
                    self.id_to_token[idx] = token

    def encode(self, tokens: List[str]) -> List[int]:
        return [self.token_to_id.get(t, 0) for t in tokens]

    def decode(self, ids: List[int]) -> List[str]:
        return [self.id_to_token.get(i, PAD_TOKEN) for i in ids]

    def create_training_pairs(
        self,
        token_ids: List[int],
        sequence_length: int = 32
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates sliding window input (X) and target (y) arrays.
        """
        inputs = []
        targets = []

        if len(token_ids) <= sequence_length:
            # Pad sequence if shorter
            padded = token_ids + [0] * (sequence_length + 1 - len(token_ids))
            inputs.append(padded[:sequence_length])
            targets.append(padded[sequence_length])
        else:
            for i in range(len(token_ids) - sequence_length):
                inputs.append(token_ids[i : i + sequence_length])
                targets.append(token_ids[i + sequence_length])

        return np.array(inputs, dtype=np.int64), np.array(targets, dtype=np.int64)

    def save_vocab(self, file_path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({
                "token_to_id": self.token_to_id,
                "id_to_token": {str(k): v for k, v in self.id_to_token.items()},
                "step_size": self.step_size,
            }, f, indent=2)

    def load_vocab(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.token_to_id = data["token_to_id"]
            self.id_to_token = {int(k): v for k, v in data["id_to_token"].items()}
            self.step_size = data.get("step_size", 0.25)
