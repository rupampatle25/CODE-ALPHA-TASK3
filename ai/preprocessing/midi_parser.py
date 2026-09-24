import os
from typing import List, Dict, Any, Optional
import mido

class MidiNoteEvent:
    def __init__(self, pitch: int, start_time: float, duration: float, velocity: int = 64, channel: int = 0):
        self.pitch = pitch          # MIDI note number (0 - 127)
        self.start_time = start_time  # in beats or seconds
        self.duration = duration    # in beats or seconds
        self.velocity = velocity    # MIDI velocity (0 - 127)
        self.channel = channel

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitch": self.pitch,
            "start_time": round(self.start_time, 4),
            "duration": round(self.duration, 4),
            "velocity": self.velocity,
            "channel": self.channel,
        }

    def __repr__(self) -> str:
        return f"Note(p={self.pitch}, start={self.start_time:.2f}, dur={self.duration:.2f}, vel={self.velocity})"

class MidiParser:
    """
    Parses Standard MIDI Files (Type 0 and Type 1) into clean, time-ordered note event lists.
    Quantizes timing to a 16th-note grid for consistent neural network representation.
    """

    @staticmethod
    def parse_file(file_path: str, quantize_grid: float = 0.25) -> List[MidiNoteEvent]:
        """
        Parses a MIDI file and returns a list of MidiNoteEvents sorted by start_time.
        quantize_grid: 0.25 corresponds to 16th-notes (quarter note = 1.0).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"MIDI file not found: {file_path}")

        try:
            mid = mido.MidiFile(file_path)
        except Exception as e:
            raise ValueError(f"Failed to parse MIDI file {file_path}: {str(e)}")

        ticks_per_beat = mid.ticks_per_beat
        notes: List[MidiNoteEvent] = []

        for track_idx, track in enumerate(mid.tracks):
            current_tick = 0
            active_notes: Dict[int, Dict[str, Any]] = {}

            for msg in track:
                current_tick += msg.time
                current_beat = current_tick / ticks_per_beat

                if msg.type == "note_on" and msg.velocity > 0:
                    # Note start
                    active_notes[msg.note] = {
                        "start_beat": current_beat,
                        "velocity": msg.velocity,
                        "channel": getattr(msg, "channel", 0),
                    }
                elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    # Note end
                    if msg.note in active_notes:
                        note_info = active_notes.pop(msg.note)
                        duration = current_beat - note_info["start_beat"]
                        if duration > 0:
                            # Quantize start and duration to grid
                            q_start = round(note_info["start_beat"] / quantize_grid) * quantize_grid
                            q_dur = max(quantize_grid, round(duration / quantize_grid) * quantize_grid)
                            notes.append(MidiNoteEvent(
                                pitch=msg.note,
                                start_time=q_start,
                                duration=q_dur,
                                velocity=note_info["velocity"],
                                channel=note_info["channel"],
                            ))

            # Close any lingering active notes at the end of track
            for pitch, note_info in active_notes.items():
                duration = (current_tick / ticks_per_beat) - note_info["start_beat"]
                if duration > 0:
                    q_start = round(note_info["start_beat"] / quantize_grid) * quantize_grid
                    q_dur = max(quantize_grid, round(duration / quantize_grid) * quantize_grid)
                    notes.append(MidiNoteEvent(
                        pitch=pitch,
                        start_time=q_start,
                        duration=q_dur,
                        velocity=note_info["velocity"],
                        channel=note_info["channel"],
                    ))

        # Sort all notes chronologically by start_time, then pitch
        notes.sort(key=lambda n: (n.start_time, n.pitch))
        return notes

    @staticmethod
    def events_to_midi(
        notes: List[MidiNoteEvent],
        output_path: str,
        tempo_bpm: int = 120,
        program: int = 0, # 0 = Acoustic Grand Piano
        track_name: str = "Sargam AI Track"
    ) -> str:
        """
        Converts a list of MidiNoteEvents back into a playable Standard MIDI file.
        """
        mid = mido.MidiFile(type=0)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        ticks_per_beat = 480
        mid.ticks_per_beat = ticks_per_beat

        # Add Track Name and Tempo
        track.append(mido.MetaMessage("track_name", name=track_name, time=0))
        tempo_microseconds = mido.bpm2tempo(tempo_bpm)
        track.append(mido.MetaMessage("set_tempo", tempo=tempo_microseconds, time=0))

        # Add Program Change (Instrument)
        track.append(mido.Message("program_change", program=min(max(0, program), 127), time=0))

        # Build raw events: (tick, type, note, velocity)
        raw_events = []
        for n in notes:
            start_tick = int(round(n.start_time * ticks_per_beat))
            end_tick = int(round((n.start_time + n.duration) * ticks_per_beat))
            raw_events.append((start_tick, "note_on", n.pitch, n.velocity))
            raw_events.append((end_tick, "note_off", n.pitch, 0))

        # Sort raw events primarily by tick, note_off before note_on at same tick
        raw_events.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1))

        # Convert absolute ticks to delta times
        last_tick = 0
        for tick, event_type, pitch, velocity in raw_events:
            delta = max(0, tick - last_tick)
            track.append(mido.Message(event_type, note=pitch, velocity=velocity, time=delta))
            last_tick = tick

        track.append(mido.MetaMessage("end_of_track", time=0))

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        mid.save(output_path)
        return output_path
