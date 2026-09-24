import os
import pytest
import torch
from ai.preprocessing.midi_parser import MidiNoteEvent, MidiParser
from ai.preprocessing.sequence_encoder import MusicSequenceEncoder
from ai.models.lstm_composer import LSTMComposer
from app.services.audio_synth import AudioSynthesizer

def test_midi_parser_and_export(tmp_path):
    events = [
        MidiNoteEvent(pitch=60, start_time=0.0, duration=0.5, velocity=80),
        MidiNoteEvent(pitch=64, start_time=0.5, duration=0.5, velocity=80),
        MidiNoteEvent(pitch=67, start_time=1.0, duration=1.0, velocity=80),
    ]
    out_midi = str(tmp_path / "test.mid")
    MidiParser.events_to_midi(events, out_midi, tempo_bpm=120, program=0)

    assert os.path.exists(out_midi)
    assert os.path.getsize(out_midi) > 0

    parsed = MidiParser.parse_file(out_midi)
    assert len(parsed) == 3
    assert parsed[0].pitch == 60
    assert parsed[1].pitch == 64
    assert parsed[2].pitch == 67

def test_sequence_encoder():
    encoder = MusicSequenceEncoder(step_size=0.25)
    notes = [
        MidiNoteEvent(pitch=60, start_time=0.0, duration=0.5),
        MidiNoteEvent(pitch=62, start_time=0.5, duration=0.5),
    ]
    tokens = encoder.notes_to_tokens(notes)
    assert len(tokens) >= 3 # START, NOTE, NOTE, END
    assert "NOTE_60_2" in tokens
    assert "NOTE_62_2" in tokens

    encoder.build_vocab([tokens])
    assert encoder.vocab_size > 3

    decoded_notes = encoder.tokens_to_notes(tokens)
    assert len(decoded_notes) == 2
    assert decoded_notes[0].pitch == 60
    assert decoded_notes[1].pitch == 62

def test_lstm_model_dimensions():
    vocab_size = 50
    model = LSTMComposer(vocab_size=vocab_size, embedding_dim=32, hidden_dim=64, num_layers=2)
    dummy_input = torch.randint(0, vocab_size, (2, 8)) # batch=2, seq=8
    logits, (hn, cn) = model(dummy_input)

    assert logits.shape == (2, 8, vocab_size)
    assert hn.shape == (2, 2, 64)

    sampled = model.sample_next_token(logits[0, -1, :], temperature=1.0, top_k=5)
    assert 0 <= sampled < vocab_size

def test_audio_synthesis(tmp_path):
    # Create simple MIDI
    events = [MidiNoteEvent(pitch=60, start_time=0.0, duration=0.5)]
    out_midi = str(tmp_path / "simple.mid")
    MidiParser.events_to_midi(events, out_midi, tempo_bpm=120)

    out_wav = str(tmp_path / "simple.wav")
    AudioSynthesizer.midi_to_audio(out_midi, out_wav)

    assert os.path.exists(out_wav)
    assert os.path.getsize(out_wav) > 1000
