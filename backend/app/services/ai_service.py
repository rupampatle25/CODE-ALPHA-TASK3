import os
import uuid
import time
from typing import Dict, Any, Tuple
from app.core.config import settings
from ai.generation.generator import MusicGenerator
from app.services.audio_synth import AudioSynthesizer

class AIService:
    _generator_instance: MusicGenerator | None = None

    @classmethod
    def get_generator(cls) -> MusicGenerator:
        if cls._generator_instance is None:
            cls._generator_instance = MusicGenerator(str(settings.CHECKPOINTS_DIR))
        return cls._generator_instance

    @classmethod
    def run_generation_pipeline(
        cls,
        genre: str,
        mood: str,
        tempo: int,
        instrument: str,
        duration_seconds: int,
        temperature: float = 1.0,
        prompt: str | None = None,
        job_id: str | None = None,
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Executes the full AI Music Generation Pipeline:
        1. AI sequence generation via trained LSTM
        2. MIDI file serialization
        3. Audio synthesis to 44.1kHz stereo WAV
        Returns: (midi_path, wav_path, metadata)
        """
        if not job_id:
            job_id = str(uuid.uuid4())

        midi_filename = f"{job_id}.mid"
        wav_filename = f"{job_id}.wav"

        midi_path = str(settings.MIDI_STORAGE_DIR / midi_filename)
        wav_path = str(settings.AUDIO_STORAGE_DIR / wav_filename)

        generator = cls.get_generator()

        # 1. Model inference -> MIDI
        gen_start = time.time()
        metadata = generator.generate(
            genre=genre,
            mood=mood,
            tempo=tempo,
            instrument=instrument,
            duration_seconds=duration_seconds,
            temperature=temperature,
            output_midi_path=midi_path,
            prompt=prompt,
        )
        gen_time = time.time() - gen_start

        # 2. MIDI -> High-fidelity WAV
        synth_start = time.time()
        AudioSynthesizer.midi_to_audio(
            midi_path=midi_path,
            output_wav_path=wav_path,
        )
        synth_time = time.time() - synth_start

        metadata["generation_time_sec"] = round(gen_time, 2)
        metadata["synthesis_time_sec"] = round(synth_time, 2)
        metadata["total_time_sec"] = round(gen_time + synth_time, 2)
        metadata["midi_size_bytes"] = os.path.getsize(midi_path) if os.path.exists(midi_path) else 0
        metadata["wav_size_bytes"] = os.path.getsize(wav_path) if os.path.exists(wav_path) else 0

        return midi_path, wav_path, metadata
