import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('sargam_token') || localStorage.getItem('melodia_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  plan: string;
  credits_balance: number;
  is_active: boolean;
  created_at: string;
}

export interface GeneratedAsset {
  id: string;
  asset_type: 'midi' | 'audio_wav';
  file_size_bytes: number;
  mime_type: string;
  download_url: string;
  created_at: string;
}

export interface GenerationJob {
  id: string;
  project_id: string | null;
  status: 'queued' | 'generating' | 'rendering' | 'completed' | 'failed';
  progress: number;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
  assets: GeneratedAsset[];
}

export interface MusicProject {
  id: string;
  user_id: string;
  title: string;
  prompt: string | null;
  genre: string;
  mood: string;
  tempo: number;
  instrument: string;
  duration_seconds: number;
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
  latest_job: GenerationJob | null;
  assets: GeneratedAsset[];
}


// API Methods
export const api = {
  // Auth
  register: (data: { email: string; name: string; password: string }) =>
    apiClient.post<{ access_token: string; user: User }>('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    apiClient.post<{ access_token: string; user: User }>('/auth/login', data),
  getMe: () => apiClient.get<User>('/auth/me'),

  // Music Generations
  createGeneration: (data: {
    prompt?: string;
    genre: string;
    mood: string;
    tempo: number;
    instrument: string;
    duration_seconds: number;
    temperature?: number;
    project_id?: string;
  }) => apiClient.post<GenerationJob>('/generations', data),

  getGenerationStatus: (id: string) => apiClient.get<GenerationJob>(`/generations/${id}`),
  listGenerations: () => apiClient.get<GenerationJob[]>('/generations'),

  // Projects
  listProjects: () => apiClient.get<MusicProject[]>('/projects'),
  createProject: (data: Partial<MusicProject>) => apiClient.post<MusicProject>('/projects', data),
  getProject: (id: string) => apiClient.get<MusicProject>(`/projects/${id}`),
  updateProject: (id: string, data: { title?: string; is_favorite?: boolean }) =>
    apiClient.patch<MusicProject>(`/projects/${id}`, data),
  deleteProject: (id: string) => apiClient.delete(`/projects/${id}`),


  // Usage
  getUsage: () =>
    apiClient.get<{
      credits_balance: number;
      plan: string;
      total_generations: number;
      history: any[];
    }>('/usage'),
};
