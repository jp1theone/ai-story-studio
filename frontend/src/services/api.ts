import type { Project, ProjectListItem } from '@/types/project';
import type { GenerationRequest, GenerationStatus } from '@/types/generation';

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${res.status}`);
  }
  return res.json();
}

export const api = {
  projects: {
    list: () => request<ProjectListItem[]>('/projects'),
    get: (id: number) => request<Project>(`/projects/${id}`),
    delete: (id: number) => request<{ ok: boolean }>(`/projects/${id}`, { method: 'DELETE' }),
    downloadUrl: (id: number, options: { path?: string; platform?: string }) => {
      const params = new URLSearchParams();
      if (options.path) params.set('path', options.path);
      if (options.platform) params.set('platform', options.platform);
      return `${BASE}/projects/${id}/download?${params.toString()}`;
    },
  },
  generation: {
    start: (body: GenerationRequest) => request<GenerationStatus>('/generation/start', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
    status: (id: number) => request<GenerationStatus>(`/generation/status/${id}`),
    shorts: (id: number) => request<{ ok: boolean; message: string }>(`/generation/shorts/${id}`, {
      method: 'POST',
    }),
  },
  settings: {
    outputFolder: () => request<{ path: string }>('/settings/output-folder'),
    setOutputFolder: (path: string) => request<{ path: string }>('/settings/output-folder', {
      method: 'PUT',
      body: JSON.stringify({ path }),
    }),
  },
};
