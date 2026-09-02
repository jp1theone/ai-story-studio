import { useEffect } from 'react';
import { wsClient } from '@/services/ws';
import type { WsMessageHandler } from '@/services/ws';

/** Hook para suscribirse a mensajes del WebSocket de generacion. */
export function useWebSocket(projectId: number | null, handler: WsMessageHandler) {
  useEffect(() => {
    if (!projectId) return;
    wsClient.connect(projectId);
    const unsubscribe = wsClient.onMessage(handler);
    return () => {
      unsubscribe();
      wsClient.disconnect();
    };
  }, [projectId, handler]);
}