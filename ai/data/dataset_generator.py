import os
from typing import List, Tuple
from ai.preprocessing.midi_parser import MidiNoteEvent, MidiParser

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")

def generate_sample_compositions():
    """
    Populates ai/data/raw/ with varied musical compositions and motifs across multiple genres:
    Classical, Lo-Fi, Ambient, Cinematic, Jazz, and Electronic.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    compositions = {
        # 1. Classical - Bach Invention style (Counterpoint in D Minor / C Major)
        "classical_bach_invention_c_maj.mid": {
            "bpm": 112,
            "program": 0, # Piano
            "notes": [
                # Bar 1: Ascending C Major motive
                (60, 0.0, 0.5), (62, 0.5, 0.5), (64, 1.0, 0.5), (65, 1.5, 0.5),
                (67, 2.0, 1.0), (64, 3.0, 1.0),
                # Bar 2: Sequence on G
                (67, 4.0, 0.5), (69, 4.5, 0.5), (71, 5.0, 0.5), (72, 5.5, 0.5),
                (74, 6.0, 1.0), (71, 7.0, 1.0),
                # Bar 3: Cadential descent
                (72, 8.0, 0.5), (71, 8.5, 0.5), (69, 9.0, 0.5), (67, 9.5, 0.5),
                (65, 10.0, 0.5), (64, 10.5, 0.5), (62, 11.0, 0.5), (60, 11.5, 0.5),
                # Bar 4: Tonic cadence
                (60, 12.0, 2.0), (64, 12.0, 2.0), (67, 12.0, 2.0), (72, 12.0, 2.0),
            ]
        },
        # 2. Classical - Chopin Nocturne style (E Flat Major / C Minor lyricism)
        "classical_chopin_nocturne_theme.mid": {
            "bpm": 68,
            "program": 0, # Piano
            "notes": [
                # Bar 1: Expressive arch
                (67, 0.0, 1.5), (70, 1.5, 0.5), (72, 2.0, 1.0), (70, 3.0, 1.0),
                (68, 4.0, 1.5), (67, 5.5, 0.5), (65, 6.0, 2.0),
                # Bar 2: Chromatic inflections
                (65, 8.0, 1.0), (66, 9.0, 1.0), (67, 10.0, 1.5), (65, 11.5, 0.5),
                (63, 12.0, 3.0),
                # Bar 3: Resolution
                (60, 16.0, 2.0), (63, 16.0, 2.0), (67, 16.0, 2.0), (72, 16.0, 4.0),
            ]
        },
        # 3. Lo-Fi - Chill Rhodes Progression (Dm9 - G13 - Cmaj7 - Am7)
        "lofi_chill_rhodes_chords.mid": {
            "bpm": 80,
            "program": 4, # Electric Piano (Rhodes)
            "notes": [
                # Bar 1: Dm9 chord
                (50, 0.0, 3.5), (57, 0.0, 3.5), (60, 0.0, 3.5), (64, 0.0, 3.5), (65, 0.0, 3.5),
                (69, 1.5, 1.0), (67, 2.5, 1.0),
                # Bar 2: G13 chord
                (43, 4.0, 3.5), (53, 4.0, 3.5), (59, 4.0, 3.5), (64, 4.0, 3.5), (67, 4.0, 3.5),
                (65, 5.5, 1.0), (64, 6.5, 1.0),
                # Bar 3: Cmaj9 chord
                (48, 8.0, 3.5), (55, 8.0, 3.5), (59, 8.0, 3.5), (62, 8.0, 3.5), (64, 8.0, 3.5),
                (67, 9.5, 1.0), (71, 10.5, 1.0),
                # Bar 4: Am9 chord
                (45, 12.0, 3.5), (52, 12.0, 3.5), (55, 12.0, 3.5), (60, 12.0, 3.5), (64, 12.0, 3.5),
            ]
        },
        # 4. Ambient - Ethereal Pad Progression
        "ambient_ethereal_pad.mid": {
            "bpm": 60,
            "program": 88, # Pad (Synth Warm)
            "notes": [
                (48, 0.0, 6.0), (55, 0.0, 6.0), (62, 0.0, 6.0), (67, 1.0, 5.0), (71, 2.0, 4.0),
                (45, 6.0, 6.0), (52, 6.0, 6.0), (59, 6.0, 6.0), (64, 7.0, 5.0), (69, 8.0, 4.0),
                (41, 12.0, 6.0), (48, 12.0, 6.0), (55, 12.0, 6.0), (60, 13.0, 5.0), (67, 14.0, 4.0),
                (43, 18.0, 6.0), (50, 18.0, 6.0), (57, 18.0, 6.0), (62, 19.0, 5.0), (65, 20.0, 4.0),
            ]
        },
        # 5. Cinematic - Dramatic Strings & Heroic Arpeggio
        "cinematic_strings_theme.mid": {
            "bpm": 100,
            "program": 48, # String Ensemble
            "notes": [
                # Minor ostinato
                (45, 0.0, 1.0), (57, 0.0, 0.5), (60, 0.5, 0.5), (64, 1.0, 0.5), (69, 1.5, 0.5),
                (45, 2.0, 1.0), (64, 2.0, 0.5), (60, 2.5, 0.5), (57, 3.0, 1.0),
                # Climax
                (41, 4.0, 1.0), (53, 4.0, 0.5), (57, 4.5, 0.5), (60, 5.0, 0.5), (65, 5.5, 0.5),
                (43, 6.0, 1.0), (55, 6.0, 0.5), (59, 6.5, 0.5), (62, 7.0, 0.5), (67, 7.5, 0.5),
                (45, 8.0, 4.0), (57, 8.0, 4.0), (64, 8.0, 4.0), (69, 8.0, 4.0),
            ]
        },
        # 6. Electronic - Synthwave Arpeggio
        "electronic_synthwave_arp.mid": {
            "bpm": 128,
            "program": 81, # Lead Synth
            "notes": [
                # 16th note rolling arpeggio
                (48, 0.0, 0.25), (60, 0.25, 0.25), (63, 0.5, 0.25), (67, 0.75, 0.25),
                (72, 1.0, 0.25), (67, 1.25, 0.25), (63, 1.5, 0.25), (60, 1.75, 0.25),
                (46, 2.0, 0.25), (58, 2.25, 0.25), (62, 2.5, 0.25), (65, 2.75, 0.25),
                (70, 3.0, 0.25), (65, 3.25, 0.25), (62, 3.5, 0.25), (58, 3.75, 0.25),
                (44, 4.0, 0.25), (56, 4.25, 0.25), (60, 4.5, 0.25), (63, 4.75, 0.25),
                (68, 5.0, 0.25), (63, 5.25, 0.25), (60, 5.5, 0.25), (56, 5.75, 0.25),
                (43, 6.0, 0.25), (55, 6.25, 0.25), (59, 6.5, 0.25), (62, 6.75, 0.25),
                (67, 7.0, 0.25), (62, 7.25, 0.25), (59, 7.5, 0.25), (55, 7.75, 0.25),
            ]
        },
    }

    created_paths = []
    for filename, data in compositions.items():
        out_path = os.path.join(RAW_DATA_DIR, filename)
        events = [
            MidiNoteEvent(pitch=p, start_time=s, duration=d, velocity=80)
            for (p, s, d) in data["notes"]
        ]
        MidiParser.events_to_midi(
            notes=events,
            output_path=out_path,
            tempo_bpm=data["bpm"],
            program=data["program"],
            track_name=filename.replace(".mid", "").replace("_", " ").title()
        )
        created_paths.append(out_path)
        print(f"Generated sample dataset composition: {out_path}")

    return created_paths

if __name__ == "__main__":
    generate_sample_compositions()
