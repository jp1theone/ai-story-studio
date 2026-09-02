import { create } from 'zustand';
import type { GenerationRequest, AgentLogEntry, ChapterInfo } from '@/types/generation';
import type { AgentState } from '@/types/agent';
import { AGENTS } from '@/data/agents';
import { api } from '@/services/api';
import { wsClient } from '@/services/ws';

interface GenerationStore {
  // Form state
  request: GenerationRequest;
  setRequest: (patch: Partial<GenerationRequest>) => void;

  // Pipeline state
  phase: 'idle' | 'config' | 'generating' | 'done' | 'failed' | 'shorts' | 'shorts_done';
  currentAgentIndex: number;
  progress: number;
  log: AgentLogEntry[];
  agentStates: AgentState[];
  scenesGenerated: number;
  totalScenes: number;
  currentChapter: number;
  totalChapters: number;
  chapters: ChapterInfo[];
  projectId: number | null;
  error: string | null;

  // Actions
  startGeneration: () => Promise<void>;
  startShorts: (projectId: number) => Promise<void>;
  reset: () => void;
}

const defaultRequest: GenerationRequest = {
  mode: 'auto',
  genres: [],
  style: 'anime',
  duration_minutes: 22,
  num_characters: 3,
  tone: 70,
  platforms: ['youtube'],
  prompt_text: undefined,
  continue_from_project_id: undefined,
  chapters_mode: false,
  chapter_duration_minutes: 20,
};

export const useGenerationStore = create<GenerationStore>((set, get) => {
  // Suscribir al WebSocket una vez
  wsClient.onMessage((data) => {
    if (data.type === 'log') {
      const entry: AgentLogEntry = {
        agent: data.agent as string,
        message: data.message as string,
        log_type: (data.log_type as AgentLogEntry['log_type']) || 'info',
      };
      set((s) => ({ log: [...s.log.slice(-200), entry] })); // limitar a 200 entradas
    }

    if (data.type === 'progress') {
      const idx = data.agent_index as number;
      const progress = data.progress as number;
      const phase = (data.phase as GenerationStore['phase']) || get().phase;
      const newAgentStates = [...get().agentStates];

      if (idx >= 0 && idx < AGENTS.length) {
        for (let i = 0; i < idx; i++) newAgentStates[i] = 'completed';
        newAgentStates[idx] = 'active';
        for (let i = idx + 1; i < newAgentStates.length; i++) newAgentStates[i] = 'waiting';
      }
      if (progress >= 100) {
        for (let i = 0; i < newAgentStates.length; i++) newAgentStates[i] = 'completed';
      }

      set({
        currentAgentIndex: idx,
        progress,
        phase,
        agentStates: newAgentStates,
        scenesGenerated: (data.scenes_generated as number) ?? get().scenesGenerated,
        totalScenes: (data.total_scenes as number) ?? get().totalScenes,
        totalChapters: (data.total_chapters as number) ?? get().totalChapters,
        currentChapter: (data.current_chapter as number) ?? get().currentChapter,
      });
    }

    if (data.type === 'chapter_complete') {
      const chapterInfo = data.chapter as ChapterInfo;
      if (chapterInfo) {
        set((s) => ({
          chapters: [...s.chapters.filter(c => c.chapter_number !== chapterInfo.chapter_number), chapterInfo],
          currentChapter: chapterInfo.chapter_number,
        }));
      }
    }
  });

  return {
    request: { ...defaultRequest },
    setRequest: (patch) =>
      set((s) => ({ request: { ...s.request, ...patch } })),

    phase: 'idle',
    currentAgentIndex: -1,
    progress: 0,
    log: [],
    agentStates: AGENTS.map(() => 'waiting'),
    scenesGenerated: 0,
    totalScenes: 0,
    currentChapter: 0,
    totalChapters: 1,
    chapters: [],
    projectId: null,
    error: null,

    startGeneration: async () => {
      const { request } = get();
      if (request.genres.length < 1) return;

      // Auto-activar modo capítulos para duraciones largas
      const finalRequest = { ...request };
      if (request.duration_minutes > 25 && !request.chapters_mode) {
        finalRequest.chapters_mode = true;
      }

      set({
        phase: 'generating',
        currentAgentIndex: 0,
        progress: 0,
        log: [],
        agentStates: AGENTS.map(() => 'waiting'),
        scenesGenerated: 0,
        totalScenes: 0,
        currentChapter: 0,
        totalChapters: 1,
        chapters: [],
        error: null,
      });

      try {
        const status = await api.generation.start(finalRequest);
        set({ projectId: status.project_id });
        wsClient.connect(status.project_id!);
      } catch (err) {
        set((s) => ({
          phase: 'idle',
          error: (err as Error).message,
          log: [
            ...s.log,
            { agent: 'Sistema', message: `Error: ${(err as Error).message}`, log_type: 'error' },
          ],
        }));
      }
    },

    startShorts: async (projectId: number) => {
      set({ phase: 'shorts', log: [], progress: 0 });
      wsClient.connect(projectId);
      try {
        await api.generation.shorts(projectId);
      } catch (err) {
        set((s) => ({
          phase: 'idle',
          error: (err as Error).message,
          log: [
            ...s.log,
            { agent: 'Sistema', message: `Error: ${(err as Error).message}`, log_type: 'error' },
          ],
        }));
      }
    },

    reset: () => {
      wsClient.disconnect();
      set({
        phase: 'idle',
        currentAgentIndex: -1,
        progress: 0,
        log: [],
        agentStates: AGENTS.map(() => 'waiting'),
        scenesGenerated: 0,
        totalScenes: 0,
        currentChapter: 0,
        totalChapters: 1,
        chapters: [],
        projectId: null,
        error: null,
      });
    },
  };
});
