import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Lock, Mail, AlertCircle, RotateCw } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsLoading(true);

    try {
      const res = await api.login({ email, password });
      login(res.data.access_token, res.data.user);
      navigate('/studio');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('producer@example.com');
    setPassword('strongPassword123!');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full rounded-2xl border border-[#232738] bg-[#0f1118] p-8 space-y-6 shadow-2xl">
        <div className="text-center space-y-3">
          <img
            src="/sargam-logo.jpg"
            alt="Sargam AI Logo"
            className="w-16 h-16 rounded-2xl mx-auto shadow-xl shadow-indigo-600/30 object-contain border border-[#232738] bg-[#0c0e14]"
          />
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Sign in to Sargam AI</h2>
            <p className="text-xs text-slate-400 mt-1">Continue producing original musical compositions</p>
          </div>
        </div>

        {errorMsg && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="producer@example.com"
                className="w-full bg-[#151824] border border-[#24293d] rounded-lg pl-9 pr-3 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#151824] border border-[#24293d] rounded-lg pl-9 pr-3 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/30 transition-all flex items-center justify-center gap-2"
          >
            {isLoading ? <RotateCw className="w-4 h-4 animate-spin" /> : 'Sign In'}
          </button>
        </form>

        <div className="pt-2 text-center space-y-3 border-t border-[#1d2130]">
          <button
            type="button"
            onClick={handleDemoLogin}
            className="text-xs text-indigo-400 hover:text-indigo-300 underline"
          >
            Fill Demo Account Credentials
          </button>
          <p className="text-xs text-slate-400">
            Don't have an account?{' '}
            <Link to="/register" className="text-indigo-400 font-semibold hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
