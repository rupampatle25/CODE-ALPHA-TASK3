import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Music2, FileAudio } from 'lucide-react';
import type { GeneratedAsset } from '../services/api';

interface AudioPlayerProps {
  title?: string;
  genre?: string;
  instrument?: string;
  audioUrl: string;
  midiUrl?: string;
  assets?: GeneratedAsset[];
  compact?: boolean;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  title = "AI Composition",
  genre,
  instrument,
  audioUrl,
  midiUrl,
  compact = false,
}) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [volume, setVolume] = useState<number>(0.85);
  const [isMuted, setIsMuted] = useState<boolean>(false);

  // Normalize absolute URL if relative
  const resolvedAudioUrl = audioUrl.startsWith('http')
    ? audioUrl
    : `http://localhost:8000${audioUrl}`;

  const resolvedMidiUrl = midiUrl
    ? (midiUrl.startsWith('http') ? midiUrl : `http://localhost:8000${midiUrl}`)
    : undefined;

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration || 0);
    const onEnded = () => setIsPlaying(false);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', onEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', onEnded);
    };
  }, [resolvedAudioUrl]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVol = parseFloat(e.target.value);
    setVolume(newVol);
    setIsMuted(newVol === 0);
    if (audioRef.current) {
      audioRef.current.volume = newVol;
    }
  };

  const toggleMute = () => {
    if (!audioRef.current) return;
    if (isMuted) {
      audioRef.current.volume = volume || 0.5;
      setIsMuted(false);
    } else {
      audioRef.current.volume = 0;
      setIsMuted(true);
    }
  };

  const formatTime = (seconds: number) => {
    if (isNaN(seconds) || seconds < 0) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`rounded-xl border border-[#232736] bg-[#11131a] p-4 shadow-xl shadow-black/40 ${compact ? 'py-3' : 'p-5'}`}>
      <audio ref={audioRef} src={resolvedAudioUrl} preload="metadata" />

      {/* Track info & visualizer header */}
      <div className="flex items-center justify-between gap-4 mb-3">
        <div className="min-w-0">
          <h4 className="text-sm font-semibold text-white truncate tracking-tight">{title}</h4>
          {(genre || instrument) && (
            <p className="text-xs text-slate-400 capitalize flex items-center gap-1.5 mt-0.5">
              {genre && <span className="text-indigo-400 font-medium">{genre}</span>}
              {genre && instrument && <span>•</span>}
              {instrument && <span>{instrument}</span>}
            </p>
          )}
        </div>

        {/* Real-time wave bars */}
        <div className="flex items-end gap-1 h-6 px-2">
          {[40, 75, 55, 90, 60, 85, 45, 70, 95, 65, 50, 80].map((height, i) => (
            <div
              key={i}
              className={`w-1 rounded-full transition-all duration-150 ${
                isPlaying
                  ? 'bg-gradient-to-t from-indigo-500 to-cyan-400'
                  : 'bg-slate-700'
              }`}
              style={{
                height: isPlaying ? `${Math.max(15, (height * (0.5 + Math.random() * 0.5)))}%` : '20%',
              }}
            />
          ))}
        </div>
      </div>

      {/* Scrubber & Controls */}
      <div className="space-y-2">
        <div className="relative flex items-center group">
          <input
            type="range"
            min="0"
            max={duration || 100}
            step="0.01"
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500 focus:outline-none"
          />
        </div>

        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Button Row */}
      <div className="flex items-center justify-between gap-3 mt-3 pt-3 border-t border-[#1c1f2b]">
        <div className="flex items-center gap-3">
          {/* Play/Pause */}
          <button
            onClick={togglePlay}
            className="w-9 h-9 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center shadow-md shadow-indigo-600/30 transition-transform active:scale-95"
            aria-label={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause className="w-4 h-4 fill-white" /> : <Play className="w-4 h-4 fill-white ml-0.5" />}
          </button>

          {/* Volume Control */}
          <div className="hidden sm:flex items-center gap-2">
            <button onClick={toggleMute} className="text-slate-400 hover:text-white transition-colors">
              {isMuted || volume === 0 ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-16 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-slate-400"
            />
          </div>
        </div>

        {/* Download Buttons */}
        <div className="flex items-center gap-2">
          {resolvedMidiUrl && (
            <a
              href={resolvedMidiUrl}
              download
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium border border-slate-700/60 transition-colors"
              title="Download Standard MIDI File"
            >
              <Music2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>MIDI</span>
            </a>
          )}
          <a
            href={resolvedAudioUrl}
            download
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 hover:text-white text-xs font-medium border border-indigo-500/40 transition-colors"
            title="Download 44.1kHz Stereo WAV Audio"
          >
            <FileAudio className="w-3.5 h-3.5 text-indigo-400" />
            <span>WAV Audio</span>
          </a>
        </div>
      </div>
    </div>
  );
};
