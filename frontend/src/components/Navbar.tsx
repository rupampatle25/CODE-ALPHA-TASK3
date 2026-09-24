import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Wand2, FolderHeart, LayoutDashboard, LogOut, Sparkles } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="border-b border-[#1f2433] bg-[#0c0e14]/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <img
            src="/sargam-logo.jpg"
            alt="Sargam AI"
            className="w-10 h-10 rounded-xl object-contain shadow-md shadow-indigo-600/30 group-hover:scale-105 transition-transform border border-[#232738] bg-[#0c0e14]"
          />
          <div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
              Sargam<span className="text-indigo-400"> AI</span>
            </span>
            <span className="hidden sm:block text-[10px] text-slate-400 font-mono tracking-wider -mt-1">
              STUDIO SUITE
            </span>
          </div>
        </Link>

        {/* Navigation links */}
        <div className="hidden md:flex items-center gap-1.5">
          <Link
            to="/studio"
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              isActive('/studio')
                ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Wand2 className="w-4 h-4" />
            Studio
          </Link>
          <Link
            to="/projects"
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              isActive('/projects')
                ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <FolderHeart className="w-4 h-4" />
            My Projects
          </Link>
          {user && (
            <Link
              to="/dashboard"
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                isActive('/dashboard')
                  ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </Link>
          )}
        </div>

        {/* Auth Actions */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              {/* Credits Pill */}
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-950/50 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
                <span>{user.credits_balance} Credits</span>
              </div>

              {/* User Profile Info */}
              <div className="hidden sm:flex flex-col items-end">
                <span className="text-xs font-semibold text-slate-200">{user.name}</span>
                <span className="text-[10px] uppercase font-mono tracking-wider text-emerald-400">
                  {user.plan}
                </span>
              </div>

              {/* Logout */}
              <button
                onClick={() => {
                  logout();
                  navigate('/login');
                }}
                title="Logout"
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2.5">
              <Link
                to="/login"
                className="text-sm font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-800/60 transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/studio"
                className="flex items-center gap-1.5 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg shadow-md shadow-indigo-600/25 transition-all hover:scale-[1.02]"
              >
                <Wand2 className="w-4 h-4" />
                <span>Start Creating</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
