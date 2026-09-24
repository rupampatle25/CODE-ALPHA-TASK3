import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import type { MusicProject } from '../services/api';
import { AudioPlayer } from '../components/AudioPlayer';
import {
  Search,
  Wand2,
  Trash2,
  Edit2,
  Check,
  Heart,
  SlidersHorizontal,
  Layers,
} from 'lucide-react';

export const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<MusicProject[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedGenre, setSelectedGenre] = useState<string>('all');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState<string>('');

  const fetchProjects = async () => {
    try {
      const res = await api.listProjects();
      setProjects(res.data);
    } catch (err) {
      console.error("Error fetching projects:", err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleToggleFavorite = async (p: MusicProject) => {
    try {
      const res = await api.updateProject(p.id, { is_favorite: !p.is_favorite });
      setProjects((prev) => prev.map((item) => (item.id === p.id ? res.data : item)));
    } catch (err) {
      console.error("Failed to toggle favorite:", err);
    }
  };

  const handleSaveTitle = async (id: string) => {
    if (!editTitle.trim()) return;
    try {
      const res = await api.updateProject(id, { title: editTitle.trim() });
      setProjects((prev) => prev.map((item) => (item.id === id ? res.data : item)));
      setEditingId(null);
    } catch (err) {
      console.error("Failed to update project title:", err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to delete this track project?")) return;
    try {
      await api.deleteProject(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      console.error("Failed to delete project:", err);
    }
  };

  const filteredProjects = projects.filter((p) => {
    const matchesSearch =
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.prompt && p.prompt.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesGenre = selectedGenre === 'all' || p.genre.toLowerCase() === selectedGenre.toLowerCase();
    return matchesSearch && matchesGenre;
  });

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#1f2434] pb-6">
        <div className="flex items-center gap-3.5">
          <img
            src="/sargam-logo.jpg"
            alt="Sargam AI"
            className="w-12 h-12 rounded-xl object-contain border border-[#232738] bg-[#0c0e14] shadow-md shadow-indigo-600/20 shrink-0"
          />
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center gap-2">
              <span>My Music Projects</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
              Organize, rename, and download your generated musical compositions.
            </p>
          </div>
        </div>

        <Link
          to="/studio"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all hover:scale-[1.02]"
        >
          <Wand2 className="w-4 h-4" />
          <span>New Track</span>
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search projects by title or prompt..."
            className="w-full bg-[#121520] border border-[#232738] rounded-xl pl-10 pr-4 py-2.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Genre Selector */}
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-slate-400" />
          <select
            value={selectedGenre}
            onChange={(e) => setSelectedGenre(e.target.value)}
            className="bg-[#121520] border border-[#232738] rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="all">All Genres</option>
            <option value="classical">Classical</option>
            <option value="lo-fi">Lo-Fi</option>
            <option value="ambient">Ambient</option>
            <option value="cinematic">Cinematic</option>
            <option value="electronic">Electronic</option>
            <option value="jazz">Jazz</option>
          </select>
        </div>
      </div>

      {/* Track List */}
      {filteredProjects.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-[#24293d] bg-[#0e1017] p-12 text-center space-y-4">
          <Layers className="w-10 h-10 text-slate-600 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-base font-semibold text-white">No tracks match your query</h3>
            <p className="text-xs text-slate-400">Try adjusting your filters or compose a brand new track.</p>
          </div>
          <Link
            to="/studio"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-colors"
          >
            <Wand2 className="w-4 h-4" />
            <span>Launch Studio</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {filteredProjects.map((p) => {
            const audioAsset = p.assets?.find((a) => a.asset_type === 'audio_wav');
            const midiAsset = p.assets?.find((a) => a.asset_type === 'midi');

            return (
              <div
                key={p.id}
                className="rounded-2xl border border-[#212638] bg-[#0f1118] p-5 sm:p-6 space-y-4 hover:border-slate-700 transition-colors"
              >
                {/* Header row */}
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1 flex-1">
                    {editingId === p.id ? (
                      <div className="flex items-center gap-2 max-w-md">
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="bg-[#181c2b] border border-indigo-500 rounded px-2.5 py-1 text-sm text-white focus:outline-none w-full"
                          autoFocus
                        />
                        <button
                          onClick={() => handleSaveTitle(p.id)}
                          className="p-1 rounded bg-indigo-600 text-white hover:bg-indigo-500"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 group">
                        <h3 className="text-base font-bold text-white tracking-tight">{p.title}</h3>
                        <button
                          onClick={() => {
                            setEditingId(p.id);
                            setEditTitle(p.title);
                          }}
                          className="text-slate-500 hover:text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Rename track"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}

                    {p.prompt && (
                      <p className="text-xs text-slate-400 italic">"{p.prompt}"</p>
                    )}

                    {/* Metadata tags */}
                    <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-400">
                      <span className="px-2 py-0.5 rounded bg-[#181b28] border border-[#252a3d] text-indigo-400 uppercase font-mono">
                        {p.genre}
                      </span>
                      <span className="capitalize">{p.mood}</span>
                      <span>•</span>
                      <span className="font-mono">{p.tempo} BPM</span>
                      <span>•</span>
                      <span className="capitalize">{p.instrument}</span>
                      <span>•</span>
                      <span className="font-mono">{p.duration_seconds}s</span>
                    </div>
                  </div>

                  {/* Actions: Favorite & Delete */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleFavorite(p)}
                      className={`p-2 rounded-lg transition-colors ${
                        p.is_favorite
                          ? 'text-rose-500 bg-rose-500/10'
                          : 'text-slate-500 hover:text-rose-400 hover:bg-slate-800'
                      }`}
                      title={p.is_favorite ? 'Favorited' : 'Add to favorites'}
                    >
                      <Heart className={`w-4 h-4 ${p.is_favorite ? 'fill-rose-500' : ''}`} />
                    </button>
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="p-2 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                      title="Delete project"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Audio Player */}
                {audioAsset ? (
                  <AudioPlayer
                    title={p.title}
                    genre={p.genre}
                    instrument={p.instrument}
                    audioUrl={audioAsset.download_url}
                    midiUrl={midiAsset?.download_url}
                  />
                ) : (
                  <div className="text-xs text-slate-500 italic py-2">
                    Audio asset processing or missing.
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
