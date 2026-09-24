import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import type { GenerationJob, MusicProject } from '../services/api';
import { AudioPlayer } from '../components/AudioPlayer';
import {
  Wand2,
  Sparkles,
  FolderHeart,
  ShieldCheck,
  History,
  ArrowRight,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [recentJobs, setRecentJobs] = useState<GenerationJob[]>([]);
  const [projects, setProjects] = useState<MusicProject[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [jobsRes, projectsRes] = await Promise.all([
          api.listGenerations(),
          api.listProjects(),
        ]);
        setRecentJobs(jobsRes.data);
        setProjects(projectsRes.data);
      } catch (err) {
        console.error("Dashboard data load error:", err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* 1. Welcome Banner */}
      <div className="rounded-2xl border border-[#232738] bg-gradient-to-r from-[#121422] to-[#0c0e16] p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-4">
          <img
            src="/sargam-logo.jpg"
            alt="Sargam AI"
            className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl object-contain border border-[#232738] bg-[#0c0e14] shadow-lg shadow-indigo-600/20 shrink-0"
          />
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-bold text-white">
                Welcome back, {user?.name || "Creator"}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-mono uppercase tracking-wider border border-indigo-500/30">
                {user?.plan || "Free"}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-400">
              Compose new musical ideas with Sargam AI, view your library, and manage your usage.
            </p>
          </div>
        </div>

        <Link
          to="/studio"
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-indigo-600/30 transition-all hover:scale-[1.02] shrink-0"
        >
          <Wand2 className="w-4 h-4" />
          <span>New Composition</span>
        </Link>
      </div>

      {/* 2. Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            title: "Available Credits",
            value: user?.credits_balance ?? 0,
            unit: "credits",
            desc: "For neural compositions",
            icon: Sparkles,
            color: "text-indigo-400",
          },
          {
            title: "Saved Projects",
            value: projects.length,
            unit: "tracks",
            desc: "Stored in library",
            icon: FolderHeart,
            color: "text-cyan-400",
          },
          {
            title: "Total Generations",
            value: recentJobs.length,
            unit: "jobs",
            desc: "Completed sessions",
            icon: History,
            color: "text-emerald-400",
          },
          {
            title: "Account Status",
            value: user?.is_active ? "ACTIVE" : "STANDARD",
            unit: "",
            desc: "Studio access",
            icon: ShieldCheck,
            color: "text-amber-400",
          },
        ].map((stat, i) => (
          <div
            key={i}
            className="rounded-xl border border-[#212638] bg-[#0f1118] p-5 space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">{stat.title}</span>
              <stat.icon className={`w-4 h-4 ${stat.color}`} />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-bold text-white">{stat.value}</span>
              {stat.unit && <span className="text-xs text-slate-400 font-mono">{stat.unit}</span>}
            </div>
            <p className="text-[11px] text-slate-500">{stat.desc}</p>
          </div>
        ))}
      </div>

      {/* 3. Recent Generation History */}
      <div className="rounded-xl border border-[#212638] bg-[#0f1118] p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Recent Generations</h2>
            <p className="text-xs text-slate-400">Play or download your latest AI-generated outputs.</p>
          </div>
          <Link
            to="/projects"
            className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <span>View All in Library</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentJobs.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-[#24293d] rounded-xl space-y-3">
            <History className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400">No tracks generated yet.</p>
            <Link
              to="/studio"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600/20 text-indigo-400 text-xs font-medium border border-indigo-500/30 hover:bg-indigo-600/30"
            >
              <Wand2 className="w-3.5 h-3.5" />
              <span>Generate First Track</span>
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {recentJobs.slice(0, 3).map((job) => {
              const audioAsset = job.assets?.find((a) => a.asset_type === 'audio_wav');
              const midiAsset = job.assets?.find((a) => a.asset_type === 'midi');

              return audioAsset ? (
                <AudioPlayer
                  key={job.id}
                  title={`Track ${job.id.slice(0, 8)}`}
                  audioUrl={audioAsset.download_url}
                  midiUrl={midiAsset?.download_url}
                  compact
                />
              ) : null;
            })}
          </div>
        )}
      </div>
    </div>
  );
};
