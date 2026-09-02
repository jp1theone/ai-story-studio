import { useEffect, useRef } from 'react';
import { useGenerationStore } from '@/stores/generationStore';
import { api } from '@/services/api';

/** Hook que hace polling del estado de generación como fallback si el WS falla. */
export function useGenerationPolling(projectId: number | null) {
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    if (!projectId) return;

    intervalRef.current = setInterval(async () => {
      try {
        const status = await api.generation.status(projectId);
        
        useGenerationStore.setState({
          progress: status.progress,
          phase: status.phase,
          currentAgentIndex: status.current_agent_index,
          scenesGenerated: status.scenes_generated,
          totalScenes: status.total_scenes,
          totalChapters: status.total_chapters ?? 1,
          currentChapter: status.current_chapter ?? 0,
          error: status.error ?? null,
        });

        if (status.phase === 'done' || status.phase === 'idle' || status.phase === 'failed') {
          clearInterval(intervalRef.current);
        }
      } catch {
        // El WS debería manejar esto; el polling es solo fallback
      }
    }, 5000);

    return () => clearInterval(intervalRef.current);
  }, [projectId]);
}
