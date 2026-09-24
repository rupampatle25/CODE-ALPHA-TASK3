import os
import math
import shutil
import subprocess
import numpy as np
from typing import List, Optional
import scipy.io.wavfile as wavfile
import mido

class AudioSynthesizer:
    """
    High-fidelity MIDI-to-WAV audio synthesis engine.
    Includes:
    1. Built-in multi-timbral physical & additive synthesis engine (100% pure Python/NumPy, zero external DLL dependencies).
    2. FluidSynth SoundFont rendering adapter when system SoundFonts (.sf2) are available.
    """

    SAMPLE_RATE = 44100

    @classmethod
    def midi_to_audio(
        cls,
        midi_path: str,
        output_wav_path: str,
        soundfont_path: Optional[str] = None,
    ) -> str:
        """
        Renders a MIDI file to a 44.1 kHz 16-bit stereo WAV file.
        Attempts FluidSynth first if available and soundfont provided, otherwise uses
        built-in high-fidelity synthesizer.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)

        # 1. Check for FluidSynth availability
        if soundfont_path and os.path.exists(soundfont_path) and shutil.which("fluidsynth"):
            try:
                cmd = [
                    "fluidsynth",
                    "-ni",
                    "-F", output_wav_path,
                    "-r", str(cls.SAMPLE_RATE),
                    soundfont_path,
                    midi_path
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 1000:
                    return output_wav_path
            except Exception:
                pass  # Fall back to native synthesizer

        # 2. Native Multi-Timbral Synthesis
        return cls._render_native(midi_path, output_wav_path)

    @classmethod
    def _render_native(cls, midi_path: str, output_wav_path: str) -> str:
        mid = mido.MidiFile(midi_path)
        ticks_per_beat = mid.ticks_per_beat

        # Determine tempo and total duration
        tempo_bpm = 120
        program = 0  # Default Piano

        for track in mid.tracks:
            for msg in track:
                if msg.type == "set_tempo":
                    tempo_bpm = mido.tempo2bpm(msg.tempo)
                elif msg.type == "program_change":
                    program = msg.program

        seconds_per_tick = (60.0 / tempo_bpm) / ticks_per_beat

        # Collect note events
        notes = []
        for track in mid.tracks:
            current_tick = 0
            active = {}
            for msg in track:
                current_tick += msg.time
                if msg.type == "note_on" and msg.velocity > 0:
                    active[msg.note] = (current_tick, msg.velocity)
                elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    if msg.note in active:
                        start_tick, vel = active.pop(msg.note)
                        dur_ticks = current_tick - start_tick
                        notes.append({
                            "pitch": msg.note,
                            "start_sec": start_tick * seconds_per_tick,
                            "dur_sec": max(0.1, dur_ticks * seconds_per_tick),
                            "velocity": vel,
                        })

        if not notes:
            # Generate 2 seconds of silence
            silence = np.zeros((cls.SAMPLE_RATE * 2, 2), dtype=np.int16)
            wavfile.write(output_wav_path, cls.SAMPLE_RATE, silence)
            return output_wav_path

        # Determine total audio length
        total_duration = max(n["start_sec"] + n["dur_sec"] for n in notes) + 2.0  # +2s reverb tail
        total_samples = int(total_duration * cls.SAMPLE_RATE)

        # Left and Right stereo channels
        left_channel = np.zeros(total_samples, dtype=np.float32)
        right_channel = np.zeros(total_samples, dtype=np.float32)

        # Synthesize notes based on instrument program
        for note in notes:
            freq = 440.0 * (2.0 ** ((note["pitch"] - 69.0) / 12.0))
            start_sample = int(note["start_sec"] * cls.SAMPLE_RATE)
            dur_samples = int(note["dur_sec"] * cls.SAMPLE_RATE)
            vel_gain = (note["velocity"] / 127.0) * 0.45

            if start_sample >= total_samples:
                continue

            tone_l, tone_r = cls._synthesize_voice(freq, dur_samples, program, vel_gain)

            end_sample = min(start_sample + len(tone_l), total_samples)
            actual_len = end_sample - start_sample

            left_channel[start_sample:end_sample] += tone_l[:actual_len]
            right_channel[start_sample:end_sample] += tone_r[:actual_len]

        # Apply subtle studio reverb/chorus diffusion
        left_channel, right_channel = cls._apply_reverb(left_channel, right_channel)

        # Peak normalization to prevent clipping (-0.5 dB ceiling)
        peak = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel)))
        if peak > 0.001:
            gain = 0.94 / peak
            left_channel *= gain
            right_channel *= gain

        # Convert to 16-bit PCM stereo
        left_pcm = np.int16(np.clip(left_channel, -1.0, 1.0) * 32767)
        right_pcm = np.int16(np.clip(right_channel, -1.0, 1.0) * 32767)
        stereo_audio = np.column_stack((left_pcm, right_pcm))

        wavfile.write(output_wav_path, cls.SAMPLE_RATE, stereo_audio)
        return output_wav_path

    @classmethod
    def _synthesize_voice(
        cls,
        freq: float,
        dur_samples: int,
        program: int,
        gain: float
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Synthesizes an expressive instrument voice using multi-harmonic wavetables & envelope shaping.
        """
        t = np.arange(dur_samples) / cls.SAMPLE_RATE

        # Classify instrument category:
        # Piano: 0-7, Rhodes: 4-5, Guitar: 24-31, Strings: 40-51, Synth: 80-87, Pad/Ambient: 88-95
        if 88 <= program <= 95:
            # Ambient / Pad: Soft sinusoidal warm harmonics with chorus
            envelope = np.minimum(t / 0.5, 1.0) * np.exp(-t / 4.0)
            wave = (
                0.6 * np.sin(2 * np.pi * freq * t) +
                0.25 * np.sin(2 * np.pi * (freq * 2.001) * t) +
                0.15 * np.sin(2 * np.pi * (freq * 3.0) * t)
            )
            # Stereo detune
            wave_r = (
                0.6 * np.sin(2 * np.pi * (freq * 1.002) * t) +
                0.25 * np.sin(2 * np.pi * (freq * 1.998) * t) +
                0.15 * np.sin(2 * np.pi * (freq * 3.003) * t)
            )
            out_l = wave * envelope * gain
            out_r = wave_r * envelope * gain
            return out_l, out_r

        elif 40 <= program <= 51:
            # Strings: Sawtooth-like unison with slow attack & warmth
            envelope = np.minimum(t / 0.25, 1.0) * np.exp(-t / 3.5)
            wave_l = (
                0.45 * np.sin(2 * np.pi * freq * t) +
                0.25 * np.sin(2 * np.pi * freq * 2 * t) +
                0.15 * np.sin(2 * np.pi * freq * 3 * t) +
                0.10 * np.sin(2 * np.pi * (freq * 1.003) * t)
            )
            wave_r = (
                0.45 * np.sin(2 * np.pi * (freq * 0.997) * t) +
                0.25 * np.sin(2 * np.pi * freq * 2 * t) +
                0.15 * np.sin(2 * np.pi * (freq * 3.004) * t) +
                0.10 * np.sin(2 * np.pi * freq * t)
            )
            return wave_l * envelope * gain, wave_r * envelope * gain

        elif 4 <= program <= 5:
            # Lo-Fi / Electric Piano (Rhodes): Warm sine fundamental + bell-like tine attack
            tine_env = np.exp(-t / 0.15)
            body_env = np.exp(-t / 1.8)
            tremolo = 1.0 + 0.15 * np.sin(2 * np.pi * 4.5 * t) # 4.5 Hz tremolo
            wave = (
                0.65 * np.sin(2 * np.pi * freq * t) * body_env +
                0.25 * np.sin(2 * np.pi * (freq * 2) * t) * body_env +
                0.30 * np.sin(2 * np.pi * (freq * 7) * t) * tine_env
            ) * tremolo
            out = wave * gain
            return out, out

        elif 80 <= program <= 87:
            # Synth Lead: Resonant filtered saw/square
            envelope = np.minimum(t / 0.02, 1.0) * np.exp(-t / 1.2)
            wave = (
                0.5 * np.sin(2 * np.pi * freq * t) +
                0.25 * np.sin(2 * np.pi * freq * 2 * t) +
                0.20 * np.sin(2 * np.pi * freq * 3 * t) +
                0.15 * np.sin(2 * np.pi * freq * 4 * t)
            )
            out = wave * envelope * gain
            return out, out

        else:
            # Acoustic Piano (Default): Fast attack, multi-harmonic decay, hammer transient
            attack_samples = int(0.008 * cls.SAMPLE_RATE)
            attack = np.ones_like(t)
            if attack_samples > 0 and len(attack) > attack_samples:
                attack[:attack_samples] = np.linspace(0, 1, attack_samples)

            decay = np.exp(-t / (1.2 + 80.0 / max(1.0, freq)))
            envelope = attack * decay

            wave = (
                0.60 * np.sin(2 * np.pi * freq * t) +
                0.25 * np.sin(2 * np.pi * freq * 2 * t) +
                0.12 * np.sin(2 * np.pi * freq * 3 * t) +
                0.06 * np.sin(2 * np.pi * freq * 4 * t) +
                0.03 * np.sin(2 * np.pi * freq * 5 * t)
            )
            # Hammer click transient
            hammer = 0.1 * np.exp(-t / 0.005) * np.sin(2 * np.pi * 3200 * t)
            out = (wave + hammer) * envelope * gain
            return out, out

    @classmethod
    def _apply_reverb(cls, left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Adds high-quality comb/allpass Schroeder-style studio reverb reflections.
        """
        delay_times = [0.031, 0.037, 0.041, 0.043] # Seconds
        decays = [0.35, 0.30, 0.25, 0.20]

        reverb_l = np.copy(left)
        reverb_r = np.copy(right)

        for d_time, decay in zip(delay_times, decays):
            d_samples = int(d_time * cls.SAMPLE_RATE)
            if d_samples < len(left):
                reverb_l[d_samples:] += left[:-d_samples] * decay
                reverb_r[d_samples:] += right[:-d_samples] * decay

        out_l = 0.75 * left + 0.25 * reverb_l
        out_r = 0.75 * right + 0.25 * reverb_r
        return out_l, out_r
