import os
import random
import torch
from typing import List, Optional, Dict, Any
from ai.models.lstm_composer import LSTMComposer
from ai.preprocessing.sequence_encoder import MusicSequenceEncoder, START_TOKEN, END_TOKEN
from ai.preprocessing.midi_parser import MidiNoteEvent, MidiParser

# General MIDI Instrument Map
INSTRUMENT_PROGRAM_MAP: Dict[str, int] = {
    "piano": 0,         # Acoustic Grand Piano
    "acoustic piano": 0,
    "electric piano": 4,# Rhodes / Electric Piano
    "lo-fi": 4,
    "rhodes": 4,
    "guitar": 24,       # Acoustic Guitar (nylon)
    "strings": 48,      # String Ensemble 1
    "violin": 40,
    "synth": 81,        # Lead 2 (sawtooth)
    "pad": 88,          # Pad 1 (new age)
    "ambient": 89,      # Pad 2 (warm)
    "electronic": 80,   # Lead 1 (square)
    "bass": 33,         # Electric Bass (finger)
    "jazz": 0,          # Grand Piano for Jazz
    "cinematic": 48,    # Strings for Cinematic
}

# Scale/Mode definitions for harmonic guidance
SCALES: Dict[str, List[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],       # Happy, inspirational
    "minor": [0, 2, 3, 5, 7, 8, 10],       # Sad, mysterious, cinematic
    "dorian": [0, 2, 3, 5, 7, 9, 10],      # Lo-fi, jazz
    "pentatonic": [0, 2, 4, 7, 9],          # Calm, ambient
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11] # Dramatic cinematic
}

MOOD_SCALE_MAP: Dict[str, str] = {
    "calm": "pentatonic",
    "happy": "major",
    "sad": "minor",
    "energetic": "major",
    "mysterious": "harmonic_minor",
    "inspirational": "major",
}

class MusicGenerator:
    """
    Inference engine that uses the trained LSTMComposer neural network to generate
    coherent musical sequences based on conditioning parameters (genre, mood, tempo, instrument).
    """

    def __init__(self, checkpoints_dir: Optional[str] = None):
        if checkpoints_dir is None:
            checkpoints_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checkpoints")

        self.checkpoints_dir = checkpoints_dir
        sargam_pt = os.path.join(checkpoints_dir, "sargam_lstm_v1.pt")
        self.model_path = sargam_pt if os.path.exists(sargam_pt) else os.path.join(checkpoints_dir, "melodia_lstm_v1.pt")

        self.encoder: Optional[MusicSequenceEncoder] = None
        self.model: Optional[LSTMComposer] = None
        self.device = torch.device("cpu")

        self._load_resources()

    def _load_resources(self):
        if not (os.path.exists(self.vocab_path) and os.path.exists(self.model_path)):
            return  # Will be loaded on demand once trained

        self.encoder = MusicSequenceEncoder()
        self.encoder.load_vocab(self.vocab_path)

        checkpoint = torch.load(self.model_path, map_location=self.device)
        self.model = LSTMComposer(
            vocab_size=checkpoint["vocab_size"],
            embedding_dim=checkpoint.get("embedding_dim", 128),
            hidden_dim=checkpoint.get("hidden_dim", 256),
            num_layers=checkpoint.get("num_layers", 2),
        ).to(self.device)

        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

    @property
    def is_ready(self) -> bool:
        if self.model is None or self.encoder is None:
            self._load_resources()
        return self.model is not None and self.encoder is not None

    def _get_seed_tokens(self, genre: str, mood: str) -> List[int]:
        """
        Provides musical seed tokens corresponding to the requested genre & mood.
        """
        genre = genre.lower()
        # Seed pitch motifs
        base_motifs = {
            "classical": [60, 64, 67, 72, 71, 69, 67], # C Major arpeggio & turn
            "lo-fi": [57, 60, 64, 67, 69],              # Am7 / Dm9 color
            "ambient": [48, 55, 62, 67, 72],            # Open fifths and octaves
            "electronic": [60, 60, 63, 67, 70],         # Ostinato pulse
            "cinematic": [57, 60, 65, 64, 62],          # Dramatic minor ascent
            "jazz": [60, 63, 65, 66, 67, 70],           # Blues / Dorian run
        }
        pitches = base_motifs.get(genre, [60, 64, 67, 72])
        seed_tokens = [START_TOKEN]

        for p in pitches:
            token = f"NOTE_{p}_2" # quarter or eighth note
            if token in self.encoder.token_to_id:
                seed_tokens.append(token)

        if len(seed_tokens) == 1:
            # Fallback to any valid note tokens from vocab
            valid_notes = [t for t in self.encoder.token_to_id.keys() if t.startswith("NOTE_")]
            if valid_notes:
                seed_tokens.extend(random.sample(valid_notes, min(3, len(valid_notes))))

        return self.encoder.encode(seed_tokens)

    def _harmonize_pitch(self, pitch: int, scale_type: str, root_pitch: int = 60) -> int:
        """
        Nudges non-scale pitches towards the nearest scale degree to guarantee melodic harmony.
        """
        scale_intervals = SCALES.get(scale_type, SCALES["major"])
        octave = pitch // 12
        interval = pitch % 12
        root_interval = root_pitch % 12

        relative_interval = (interval - root_interval) % 12
        if relative_interval in scale_intervals:
            return pitch

        # Find closest scale degree
        closest_interval = min(scale_intervals, key=lambda s: abs(s - relative_interval))
        adjusted_pitch = (octave * 12) + ((root_interval + closest_interval) % 12)
        return min(108, max(36, adjusted_pitch))

    def generate(
        self,
        genre: str = "classical",
        mood: str = "calm",
        tempo: int = 120,
        instrument: str = "piano",
        duration_seconds: int = 30,
        temperature: float = 1.0,
        output_midi_path: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes sequence generation through the trained LSTM model.
        Returns generated note events and saves standard MIDI file.
        """
        if not self.is_ready:
            raise RuntimeError("Model checkpoint or vocabulary not loaded. Train the model first.")

        # Calculate target number of note events from duration and tempo
        beats = (duration_seconds / 60.0) * tempo
        # Roughly 2 to 4 events per beat on average
        target_events = int(round(beats * 2.5))
        target_events = max(16, min(target_events, 200))

        # 1. Get seed sequence
        current_seq = self._get_seed_tokens(genre, mood)
        scale_name = MOOD_SCALE_MAP.get(mood.lower(), "major")

        generated_token_ids: List[int] = list(current_seq)

        # 2. Sequential Inference Loop
        seq_len_cap = 32
        with torch.no_grad():
            for _ in range(target_events):
                # Context window: last up to seq_len_cap tokens
                input_tokens = generated_token_ids[-seq_len_cap:]
                if len(input_tokens) < seq_len_cap:
                    input_tokens = [0] * (seq_len_cap - len(input_tokens)) + input_tokens

                x = torch.tensor([input_tokens], dtype=torch.long).to(self.device)
                logits, _ = self.model(x)

                next_logits = logits[0, -1, :].clone()
                # Suppress PAD and START token generation
                next_logits[0] = float("-inf")
                next_logits[1] = float("-inf")

                next_token_id = self.model.sample_next_token(next_logits, temperature=temperature, top_k=6)

                token_str = self.encoder.id_to_token.get(next_token_id, "")
                if token_str == END_TOKEN:
                    break

                generated_token_ids.append(next_token_id)

        # 3. Decode into Note Events
        token_strings = self.encoder.decode(generated_token_ids)
        raw_notes = self.encoder.tokens_to_notes(token_strings)

        # 4. Harmonize and apply musical dynamics
        final_notes: List[MidiNoteEvent] = []
        for note in raw_notes:
            harmonized_pitch = self._harmonize_pitch(note.pitch, scale_name, root_pitch=60)
            note.pitch = harmonized_pitch
            # Add expressive velocity nuance
            note.velocity = random.randint(65, 88)
            final_notes.append(note)

        # 5. Export MIDI file
        program = INSTRUMENT_PROGRAM_MAP.get(instrument.lower(), 0)
        track_name = f"Sargam AI - {genre.title()} {mood.title()}"

        if output_midi_path:
            MidiParser.events_to_midi(
                notes=final_notes,
                output_path=output_midi_path,
                tempo_bpm=tempo,
                program=program,
                track_name=track_name,
            )

        return {
            "notes": [n.to_dict() for n in final_notes],
            "total_notes": len(final_notes),
            "genre": genre,
            "mood": mood,
            "tempo": tempo,
            "instrument": instrument,
            "program": program,
            "duration_seconds": duration_seconds,
            "midi_path": output_midi_path,
        }
