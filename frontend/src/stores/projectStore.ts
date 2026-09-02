import { create } from 'zustand';
import type { Project, ProjectListItem } from '@/types/project';
import { api } from '@/services/api';

interface ProjectStore {
  list: ProjectListItem[];
  current: Project | null;
  loading: boolean;
  error: string | null;

  fetchList: () => Promise<void>;
  fetchProject: (id: number) => Promise<void>;
  deleteProject: (id: number) => Promise<void>;
  clearCurrent: () => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  list: [],
  current: null,
  loading: false,
  error: null,

  fetchList: async () => {
    set({ loading: true, error: null });
    try {
      const list = await api.projects.list();
      set({ list, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  fetchProject: async (id: number) => {
    set({ loading: true, error: null });
    try {
      const project = await api.projects.get(id);
      set({ current: project, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  deleteProject: async (id: number) => {
    try {
      await api.projects.delete(id);
      set((s) => ({ list: s.list.filter((p) => p.id !== id) }));
    } catch (err) {
      set({ error: (err as Error).message });
    }
  },

  clearCurrent: () => set({ current: null }),
}));