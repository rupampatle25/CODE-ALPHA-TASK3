import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Wand2,
  Sparkles,
  Cpu,
  Layers,
  Sliders,
  CheckCircle2,
  FileAudio,
  Headphones,
} from 'lucide-react';
import { AudioPlayer } from '../components/AudioPlayer';

export const LandingPage: React.FC = () => {
  // Curated demo tracks
  const demoTracks = [
    {
      title: "Chopin-Inspired Classical Nocturne",
      genre: "Classical",
      mood: "Calm",
      instrument: "Acoustic Grand Piano",
      audioUrl: "/storage/audio/5fd25d42-850e-4a8b-a8ae-8e31c8c1e1c6.wav",
      midiUrl: "/storage/midi/5fd25d42-850e-4a8b-a8ae-8e31c8c1e1c6.mid",
    },
    {
      title: "Late Night Lo-Fi Study Progression",
      genre: "Lo-Fi",
      mood: "Relaxed",
      instrument: "Electric Piano (Rhodes)",
      audioUrl: "/storage/audio/5fd25d42-850e-4a8b-a8ae-8e31c8c1e1c6.wav",
      midiUrl: "/storage/midi/5fd25d42-850e-4a8b-a8ae-8e31c8c1e1c6.mid",
    },
  ];

  const [activeDemoIndex, setActiveDemoIndex] = useState(0);

  return (
    <div className="space-y-24 pb-20">
      {/* 1. Hero Section */}
      <section className="relative pt-16 sm:pt-24 pb-12 overflow-hidden">
        {/* Ambient background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-600/15 blur-[120px] rounded-full pointer-events-none -z-10" />
        <div className="absolute top-1/3 left-1/3 w-[300px] h-[300px] bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none -z-10" />

        <div className="max-w-5xl mx-auto px-4 text-center space-y-6">
          <div className="flex justify-center mb-1">
            <div className="relative group">
              <div className="absolute -inset-1.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400 rounded-3xl blur-lg opacity-40 group-hover:opacity-70 transition duration-500"></div>
              <img
                src="/sargam-logo.jpg"
                alt="Sargam AI"
                className="relative w-28 h-28 sm:w-36 sm:h-36 rounded-2xl object-contain shadow-2xl border border-[#2b3045] bg-[#0c0e14] mx-auto"
              />
            </div>
          </div>

          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181b26] border border-[#2b3045] text-indigo-300 text-xs font-medium shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Trained Deep Learning LSTM Music Engine</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.15]">
            Turn Your Ideas Into Music With <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-cyan-400 bg-clip-text text-transparent">AI</span>.
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Create musical compositions, experiment with melodies, and bring your ideas to life with Sargam AI. From prompt to playable 44.1kHz audio in seconds.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to="/studio"
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-lg shadow-indigo-600/30 transition-all hover:scale-[1.02]"
            >
              <Wand2 className="w-4 h-4" />
              <span>Start Creating</span>
            </Link>

            <a
              href="#demo"
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-[#141722] hover:bg-[#1a1e2d] border border-[#232738] text-slate-200 font-medium transition-colors"
            >
              <Headphones className="w-4 h-4 text-cyan-400" />
              <span>Try Demo Player</span>
            </a>
          </div>

          {/* Value Badges */}
          <div className="flex flex-wrap items-center justify-center gap-6 pt-6 text-xs text-slate-400">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Standard MIDI Export</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Lossless 44.1kHz WAV</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>10 Free Monthly Credits</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Audio Demonstration Section */}
      <section id="demo" className="max-w-4xl mx-auto px-4">
        <div className="rounded-2xl border border-[#232738] bg-[#0d0f17] p-6 sm:p-8 shadow-2xl relative">
          <div className="flex items-center justify-between gap-4 mb-6">
            <div>
              <span className="text-xs font-mono uppercase tracking-wider text-indigo-400 font-semibold">
                Studio Demonstration
              </span>
              <h2 className="text-xl sm:text-2xl font-bold text-white mt-1">
                Listen To What Sargam AI Composes
              </h2>
            </div>
            <div className="flex gap-2">
              {demoTracks.map((track, i) => (
                <button
                  key={i}
                  onClick={() => setActiveDemoIndex(i)}
                  className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors ${
                    activeDemoIndex === i
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-800/80 text-slate-400 hover:text-white'
                  }`}
                >
                  {track.genre}
                </button>
              ))}
            </div>
          </div>

          <AudioPlayer
            title={demoTracks[activeDemoIndex].title}
            genre={demoTracks[activeDemoIndex].genre}
            instrument={demoTracks[activeDemoIndex].instrument}
            audioUrl={demoTracks[activeDemoIndex].audioUrl}
            midiUrl={demoTracks[activeDemoIndex].midiUrl}
          />
        </div>
      </section>

      {/* 3. How AI Music Generation Works */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="text-center space-y-3 mb-12">
          <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold">
            Technical Architecture
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">
            How The Neural Composition Pipeline Operates
          </h2>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            A genuine deep learning workflow designed for symbolic musical generation and multi-harmonic synthesis.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              step: "01",
              title: "Parameter Conditioning",
              desc: "Select genre, mood, tempo BPM, scale mode, and instrumentation to shape the sequence constraint vector.",
              icon: Sliders,
            },
            {
              step: "02",
              title: "LSTM Deep Learning",
              desc: "A 2-layer Recurrent Neural Network predicts polyphonic note tokens via temperature-scaled probability distributions.",
              icon: Cpu,
            },
            {
              step: "03",
              title: "Harmonic Quantization",
              desc: "The sequence is aligned to a 16th-note rhythmic grid and key-harmonized into standard MIDI format.",
              icon: Layers,
            },
            {
              step: "04",
              title: "Wavetable Synthesis",
              desc: "The synthesized audio engine renders physical acoustic envelopes and studio reverb reflections into 44.1kHz stereo audio.",
              icon: FileAudio,
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className="rounded-xl border border-[#1f2434] bg-[#10121a] p-6 space-y-4 hover:border-indigo-500/40 transition-colors group"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-2xl font-bold text-slate-600 group-hover:text-indigo-400 transition-colors">
                  {item.step}
                </span>
                <item.icon className="w-5 h-5 text-indigo-400" />
              </div>
              <h3 className="font-semibold text-base text-white">{item.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Supported Musical Styles */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="rounded-2xl border border-[#232738] bg-gradient-to-br from-[#10131d] to-[#0a0c12] p-8 sm:p-12 space-y-8">
          <div className="max-w-2xl space-y-2">
            <h2 className="text-2xl font-bold text-white">Diverse Genre & Instrument Models</h2>
            <p className="text-sm text-slate-400">
              Each style is backed by specialized musical tokens and timbre synthesis algorithms.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { name: "Classical", desc: "Bach & Chopin motifs", icon: "🎹" },
              { name: "Lo-Fi Beats", desc: "Mellow Rhodes chords", icon: "☕" },
              { name: "Ambient", desc: "Ethereal space pads", icon: "🌌" },
              { name: "Cinematic", desc: "Dramatic string sections", icon: "🎻" },
              { name: "Electronic", desc: "Synthwave arpeggios", icon: "⚡" },
              { name: "Jazz Moods", desc: "Dorian runs & 7th chords", icon: "🎷" },
            ].map((genre, i) => (
              <div
                key={i}
                className="rounded-xl border border-[#212638] bg-[#141724]/60 p-4 text-center space-y-2 hover:border-cyan-500/40 transition-colors"
              >
                <div className="text-2xl">{genre.icon}</div>
                <h4 className="text-sm font-semibold text-white">{genre.name}</h4>
                <p className="text-[11px] text-slate-400">{genre.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>


      {/* 6. FAQ Section */}
      <section className="max-w-4xl mx-auto px-4">
        <div className="text-center space-y-2 mb-10">
          <h2 className="text-2xl font-bold text-white">Frequently Asked Questions</h2>
          <p className="text-xs text-slate-400">Everything you need to know about Sargam AI</p>
        </div>

        <div className="space-y-4">
          {[
            {
              q: "Can I use generated music in commercial videos or games?",
              a: "Yes. Sargam AI generates original note sequence arrangements trained on public domain scores and algorithmic motifs. You receive commercial-use licensing for your generated tracks.",
            },
            {
              q: "What file formats can I download?",
              a: "You can download both the standard Type 0 MIDI file (.mid) containing note pitch, timing, and velocity events, and the synthesized 44.1kHz 16-bit stereo audio file (.wav).",
            },
            {
              q: "How does the deep learning model work?",
              a: "Sargam AI uses a multi-layer PyTorch LSTM (Long Short-Term Memory) sequence model trained on tokenized note events. The model predicts musical continuations based on prompt conditioning, tempo constraints, and genre scales.",
            },
            {
              q: "Can I import generated MIDI into DAWs like Ableton, FL Studio, or Logic Pro?",
              a: "Absolutely. The exported .mid files adhere strictly to the Standard MIDI specification and can be dragged directly into any Digital Audio Workstation to trigger your favorite virtual instruments and synths.",
            },
          ].map((faq, i) => (
            <div key={i} className="rounded-xl border border-[#212638] bg-[#11131c] p-5 space-y-2">
              <h4 className="text-sm font-semibold text-white">{faq.q}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 7. Footer */}
      <footer className="border-t border-[#1d2130] pt-12 text-xs text-slate-500 max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <img
            src="/sargam-logo.jpg"
            alt="Sargam AI"
            className="w-6 h-6 rounded-md object-contain border border-[#232738] bg-[#0c0e14]"
          />
          <span className="text-slate-300 font-semibold">Sargam AI</span>
          <span>© 2026. Built with PyTorch, FastAPI, and React.</span>
        </div>
        <div className="flex gap-6">
          <Link to="/studio" className="hover:text-slate-300">Studio</Link>
          <Link to="/projects" className="hover:text-slate-300">Projects</Link>
        </div>
      </footer>
    </div>
  );
};
