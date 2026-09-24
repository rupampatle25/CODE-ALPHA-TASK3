import os
import glob
from typing import List
from ai.preprocessing.midi_parser import MidiParser, MidiNoteEvent
from ai.preprocessing.sequence_encoder import MusicSequenceEncoder

BASE_AI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_AI_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_AI_DIR, "data", "processed")
CHECKPOINTS_DIR = os.path.join(BASE_AI_DIR, "checkpoints")

def transpose_notes(notes: List[MidiNoteEvent], semitones: int) -> List[MidiNoteEvent]:
    transposed = []
    for n in notes:
        new_pitch = min(108, max(21, n.pitch + semitones))
        transposed.append(MidiNoteEvent(
            pitch=new_pitch,
            start_time=n.start_time,
            duration=n.duration,
            velocity=n.velocity,
            channel=n.channel
        ))
    return transposed

def preprocess_dataset(sequence_length: int = 8):
    """
    Parses all MIDI files in RAW_DIR, performs musical data augmentation (pitch transposition),
    builds token vocabulary, creates (X, y) sliding window training sequences, and saves processed artifacts.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)

    midi_files = glob.glob(os.path.join(RAW_DIR, "*.mid"))
    if not midi_files:
        raise ValueError(f"No MIDI files found in {RAW_DIR}. Run ai/data/dataset_generator.py first.")

    print(f"Found {len(midi_files)} MIDI files for preprocessing...")

    encoder = MusicSequenceEncoder(step_size=0.25)
    all_token_sequences: List[List[str]] = []

    # Musical data augmentation: Transpose each piece across keys (-3 to +3 semitones)
    transposition_shifts = [-3, -2, -1, 0, 1, 2, 3]

    for midi_file in midi_files:
        try:
            base_notes = MidiParser.parse_file(midi_file)
            if not base_notes:
                continue

            for shift in transposition_shifts:
                augmented_notes = transpose_notes(base_notes, shift)
                tokens = encoder.notes_to_tokens(augmented_notes)
                all_token_sequences.append(tokens)

        except Exception as e:
            print(f"Error parsing {midi_file}: {e}")

    # Build vocabulary across all original & augmented sequences
    encoder.build_vocab(all_token_sequences)
    print(f"Total sequences after transposition: {len(all_token_sequences)}")
    print(f"Total vocabulary size: {encoder.vocab_size} tokens")

    # Save vocabulary
    vocab_path_processed = os.path.join(PROCESSED_DIR, "vocab.json")
    vocab_path_checkpoint = os.path.join(CHECKPOINTS_DIR, "vocab.json")
    encoder.save_vocab(vocab_path_processed)
    encoder.save_vocab(vocab_path_checkpoint)
    print(f"Saved vocabulary to {vocab_path_checkpoint}")

    # Create training pairs (X, y) with sliding window of length 8
    all_inputs = []
    all_targets = []

    for tokens in all_token_sequences:
        token_ids = encoder.encode(tokens)
        X, y = encoder.create_training_pairs(token_ids, sequence_length=sequence_length)
        if len(X) > 0:
            all_inputs.append(X)
            all_targets.append(y)

    import numpy as np
    final_X = np.concatenate(all_inputs, axis=0)
    final_y = np.concatenate(all_targets, axis=0)

    print(f"Created {len(final_X)} training sequences (sequence length = {sequence_length})")

    # Save numpy arrays
    np.save(os.path.join(PROCESSED_DIR, "X.npy"), final_X)
    np.save(os.path.join(PROCESSED_DIR, "y.npy"), final_y)
    print(f"Saved training tensors to {PROCESSED_DIR}")

    return final_X, final_y, encoder

if __name__ == "__main__":
    preprocess_dataset()
