# Sargam AI: Dataset Documentation & Licensing

## 1. Dataset Origin & Sources
Sargam AI uses a curated corpus of musical sequence data composed of:
1. **Public Domain Classical Masterpieces**:
   * J.S. Bach - Inventions & Well-Tempered Clavier (Public Domain)
   * L.v. Beethoven - Piano Sonatas (Public Domain)
   * F. Chopin - Nocturnes & Preludes (Public Domain)
   * W.A. Mozart - Piano Sonatas (Public Domain)
2. **Algorithmic Genre Motif Seed Corpus**:
   * Lo-fi hip-hop chord progressions (ii-V-I / vi-IV-I-V in mellow keys)
   * Ambient atmospheric modal sequence motifs
   * Electronic synth arpeggios and rhythmic sequences
   * Jazz melodic cadences and Dorian/Mixolydian modal patterns

## 2. Licensing Status
* **Classical Compositions**: The underlying compositions are in the public domain worldwide (lifetime of author + 70/100 years expired).
* **MIDI Encodings**: Sourced from verified public domain archives (such as Mutopia Project and Kunstderfuge Public Domain collections) and CC0 1.0 Universal algorithmic motifs.
* **Commercial Use**: Permitted under CC0 / Public Domain guidelines. No copyrighted commercial multi-track recordings or proprietary sample packs are utilized.

## 3. Preprocessing Specifications
* MIDI format: Standard Type 0 / Type 1
* Timing quantization: 16th note grid (0.25 quarter note resolution)
* Pitch range: Standard MIDI 0 to 127
* Polyphony: Time-ordered token streams with note duration and step-offset encodings
