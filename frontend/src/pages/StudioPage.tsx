import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import type { GenerationJob } from '../services/api';
import { AudioPlayer } from '../components/AudioPlayer';
import {
  Wand2,
  Sparkles,
  Music,
  Sliders,
  Clock,
  Gauge,
  CheckCircle,
  AlertCircle,
  RotateCw,
} from 'lucide-react';

export const StudioPage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();

  // Generator State
  const [prompt, setPrompt] = useState<string>('Peaceful classical piano nocturne with gentle chords');
  const [genre, setGenre] = useState<string>('classical');
  const [mood, setMood] = useState<string>('calm');
  const [tempo, setTempo] = useState<number>(115);
  const [instrument, setInstrument] = useState<string>('piano');
  const [duration, setDuration] = useState<number>(30);
  const [temperature, setTemperature] = useState<number>(1.0);

  // Job & Polling State
  const [activeJob, setActiveJob] = useState<GenerationJob | null>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const samplePrompts = [
    { label: "Classical Nocturne", prompt: "Peaceful classical piano nocturne with gentle chords", genre: "classical", mood: "calm", inst: "piano", bpm: 80 },
    { label: "Chill Lo-Fi Beat", prompt: "Late night chill lo-fi chords on vintage Rhodes electric piano", genre: "lo-fi", mood: "calm", inst: "lo-fi", bpm: 78 },
    { label: "Cinematic Strings", prompt: "Heroic dramatic string ensemble crescendo with minor cadences", genre: "cinematic", mood: "mysterious", inst: "strings", bpm: 105 },
    { label: "Ambient Space", prompt: "Floating ethereal warm synthesizer pad with slow resonant evolution", genre: "ambient", mood: "calm", inst: "ambient", bpm: 60 },
    { label: "Electronic Synth", prompt: "High energy retro synthwave arpeggio rolling bassline", genre: "electronic", mood: "energetic", inst: "synth", bpm: 128 },
  ];

  // Poll status while job is active
  useEffect(() => {
    if (!activeJob || activeJob.status === 'completed' || activeJob.status === 'failed') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const res = await api.getGenerationStatus(activeJob.id);
        setActiveJob(res.data);
        if (res.data.status === 'completed') {
          setIsGenerating(false);
          refreshUser();
        } else if (res.data.status === 'failed') {
          setIsGenerating(false);
          setErrorMsg(res.data.error_message || "Music generation failed.");
        }
      } catch {
        setIsGenerating(false);
        setErrorMsg("Failed to check generation progress.");
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [activeJob]);

  const handleStartGeneration = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (user.credits_balance <= 0) {
      setErrorMsg("You have 0 credits remaining. Please contact support or request additional credits.");
      return;
    }

    setErrorMsg(null);
    setIsGenerating(true);

    try {
      const res = await api.createGeneration({
        prompt,
        genre,
        mood,
        tempo,
        instrument,
        duration_seconds: duration,
        temperature,
      });
      setActiveJob(res.data);
    } catch (err: any) {
      setIsGenerating(false);
      setErrorMsg(err.response?.data?.detail || "Generation request failed.");
    }
  };

  const getAudioUrl = () => {
    if (!activeJob || !activeJob.assets) return '';
    const wavAsset = activeJob.assets.find(a => a.asset_type === 'audio_wav');
    return wavAsset ? wavAsset.download_url : '';
  };

  const getMidiUrl = () => {
    if (!activeJob || !activeJob.assets) return '';
    const midiAsset = activeJob.assets.find(a => a.asset_type === 'midi');
    return midiAsset ? midiAsset.download_url : '';
  };

  const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#1f2434] pb-6">
        <div className="flex items-center gap-3.5">
          <img
            src="/sargam-logo.jpg"
            alt="Sargam AI"
            className="w-12 h-12 rounded-xl object-contain border border-[#232738] bg-[#0c0e14] shadow-md shadow-indigo-600/20 shrink-0"
          />
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center gap-2">
              <span>Sargam AI Studio</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
              Condition musical parameters and trigger neural LSTM sequence generation.
            </p>
          </div>
        </div>

        {user && (
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#141722] border border-[#232738] text-xs">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="text-slate-300">Balance:</span>
            <span className="font-bold text-white">{user.credits_balance} Credits</span>
          </div>
        )}
      </div>

      {errorMsg && (
        <div className="flex items-center gap-2.5 p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Parameter Controls (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* 1. Prompt Input & Chips */}
          <div className="rounded-xl border border-[#212638] bg-[#0f1118] p-5 space-y-3">
            <label className="block text-xs font-semibold text-slate-300 tracking-wide uppercase">
              1. Composition Idea or Prompt
            </label>
            <textarea
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Peaceful classical piano melody with a cinematic atmosphere..."
              className="w-full bg-[#151824] border border-[#24293d] rounded-lg p-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />

            {/* Inspiration chips */}
            <div className="space-y-1.5 pt-1">
              <span className="text-[11px] font-mono text-slate-500">Preset Inspirations:</span>
              <div className="flex flex-wrap gap-1.5">
                {samplePrompts.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setPrompt(s.prompt);
                      setGenre(s.genre);
                      setMood(s.mood);
                      setInstrument(s.inst);
                      setTempo(s.bpm);
                    }}
                    className="px-2.5 py-1 rounded-md bg-[#191d2c] hover:bg-indigo-600/30 text-slate-300 hover:text-white text-xs border border-[#252a3f] transition-colors"
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 2. Musical Attributes */}
          <div className="rounded-xl border border-[#212638] bg-[#0f1118] p-5 space-y-5">
            <span className="block text-xs font-semibold text-slate-300 tracking-wide uppercase">
              2. Musical Attributes & Timbres
            </span>

            {/* Genre & Mood Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-slate-400 mb-1.5">Genre</label>
                <select
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  className="w-full bg-[#151824] border border-[#24293d] rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="classical">Classical</option>
                  <option value="lo-fi">Lo-Fi Chill</option>
                  <option value="ambient">Ambient Atmospheric</option>
                  <option value="cinematic">Cinematic</option>
                  <option value="electronic">Electronic Synthwave</option>
                  <option value="jazz">Jazz / Blues</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-400 mb-1.5">Mood & Harmonic Mode</label>
                <select
                  value={mood}
                  onChange={(e) => setMood(e.target.value)}
                  className="w-full bg-[#151824] border border-[#24293d] rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="calm">Calm (Pentatonic)</option>
                  <option value="happy">Happy (Major)</option>
                  <option value="sad">Sad (Minor)</option>
                  <option value="energetic">Energetic (Bright Major)</option>
                  <option value="mysterious">Mysterious (Harmonic Minor)</option>
                  <option value="inspirational">Inspirational (Epic Major)</option>
                </select>
              </div>
            </div>

            {/* Instrument Selection */}
            <div>
              <label className="block text-xs text-slate-400 mb-2">Primary Instrument Timbre</label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {[
                  { id: 'piano', label: 'Grand Piano', icon: '🎹' },
                  { id: 'strings', label: 'Strings', icon: '🎻' },
                  { id: 'lo-fi', label: 'Rhodes Piano', icon: '☕' },
                  { id: 'synth', label: 'Lead Synth', icon: '⚡' },
                ].map((inst) => (
                  <button
                    key={inst.id}
                    onClick={() => setInstrument(inst.id)}
                    className={`p-3 rounded-lg border text-left flex items-center gap-2.5 transition-all ${
                      instrument === inst.id
                        ? 'border-indigo-500 bg-indigo-600/15 text-white'
                        : 'border-[#24293d] bg-[#151824] text-slate-300 hover:text-white'
                    }`}
                  >
                    <span className="text-xl">{inst.icon}</span>
                    <span className="text-xs font-medium">{inst.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Tempo (BPM) Slider */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Gauge className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Tempo (BPM)</span>
                </span>
                <span className="font-mono font-bold text-white">{tempo} BPM</span>
              </div>
              <input
                type="range"
                min="50"
                max="160"
                step="2"
                value={tempo}
                onChange={(e) => setTempo(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                <span>Slow (60)</span>
                <span>Andante (100)</span>
                <span>Allegro (140+)</span>
              </div>
            </div>

            {/* Duration Slider */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Target Composition Duration</span>
                </span>
                <span className="font-mono font-bold text-white">{duration} Seconds</span>
              </div>
              <input
                type="range"
                min="15"
                max="60"
                step="5"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>

            {/* Creativity (Temperature) Slider */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Creativity & Sampling Temperature</span>
                </span>
                <span className="font-mono font-bold text-white">{temperature.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="0.4"
                max="1.6"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                <span>Strict Structure (0.5)</span>
                <span>Balanced (1.0)</span>
                <span>Experimental (1.5)</span>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleStartGeneration}
            disabled={isGenerating}
            className={`w-full py-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2.5 transition-all shadow-xl ${
              isGenerating
                ? 'bg-indigo-900/50 text-indigo-300 border border-indigo-700/50 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/30 hover:scale-[1.01]'
            }`}
          >
            {isGenerating ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin text-indigo-300" />
                <span>Neural Engine Composing...</span>
              </>
            ) : (
              <>
                <Wand2 className="w-4 h-4" />
                <span>Generate Composition (1 Credit)</span>
              </>
            )}
          </button>
        </div>

        {/* Right Column: Generation Status & Result Player (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="rounded-xl border border-[#212638] bg-[#0f1118] p-6 space-y-6">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Music className="w-4 h-4 text-indigo-400" />
              <span>Studio Output</span>
            </h3>

            {/* State 1: Active Job Progress */}
            {isGenerating && activeJob && (
              <div className="rounded-xl border border-indigo-500/30 bg-[#121522] p-5 space-y-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-indigo-300 capitalize flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                    {activeJob.status === 'generating' && 'LSTM predicting note sequences...'}
                    {activeJob.status === 'rendering' && 'Synthesizing 44.1kHz audio wavetable...'}
                    {activeJob.status === 'queued' && 'Queued in processing worker...'}
                  </span>
                  <span className="font-mono text-indigo-400">{activeJob.progress}%</span>
                </div>

                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-300 rounded-full"
                    style={{ width: `${Math.max(10, activeJob.progress)}%` }}
                  />
                </div>

                <p className="text-[11px] text-slate-400">
                  Model checkpoint inference executing on CPU worker.
                </p>
              </div>
            )}

            {/* State 2: Completed Result Player */}
            {activeJob && activeJob.status === 'completed' && (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
                  <CheckCircle className="w-4 h-4" />
                  <span>Composition Rendered Successfully!</span>
                </div>

                <AudioPlayer
                  title={prompt || `${capitalize(genre)} Composition`}
                  genre={genre}
                  instrument={instrument}
                  audioUrl={getAudioUrl()}
                  midiUrl={getMidiUrl()}
                  assets={activeJob.assets}
                />
              </div>
            )}

            {/* State 3: Empty / Idle State */}
            {!isGenerating && (!activeJob || activeJob.status !== 'completed') && (
              <div className="border border-dashed border-[#24293d] rounded-xl p-8 text-center space-y-3">
                <div className="w-12 h-12 rounded-xl bg-slate-800/80 text-slate-400 flex items-center justify-center mx-auto">
                  <Sliders className="w-6 h-6" />
                </div>
                <h4 className="text-sm font-semibold text-white">No Track Active</h4>
                <p className="text-xs text-slate-400 max-w-xs mx-auto">
                  Select your desired genre, mood, and instrumentation on the left, then click Generate Composition.
                </p>
              </div>
            )}

            {/* Generation Parameters Summary Card */}
            <div className="rounded-lg bg-[#141724] border border-[#212638] p-4 space-y-2 text-xs">
              <span className="font-mono uppercase text-[10px] text-slate-400 tracking-wider">
                Current Settings Matrix
              </span>
              <div className="grid grid-cols-2 gap-2 text-slate-300 pt-1">
                <div>Style: <span className="text-white capitalize font-medium">{genre}</span></div>
                <div>Scale: <span className="text-white capitalize font-medium">{mood}</span></div>
                <div>Tempo: <span className="text-white font-mono font-medium">{tempo} BPM</span></div>
                <div>Timbre: <span className="text-white capitalize font-medium">{instrument}</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
