export type WsMessageHandler = (data: Record<string, unknown>) => void;

export class GenerationWebSocket {
  private ws: WebSocket | null = null;
  private handlers: Set<WsMessageHandler> = new Set();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private projectId: number | null = null;

  connect(projectId: number): void {
    // Cerrar una conexión anterior sin borrar el proyecto que se quiere abrir.
    // Antes se asignaba projectId y `disconnect()` lo volvía a null, por lo que
    // el cierre nunca programaba la reconexión.
    this.closeConnection(false);
    this.projectId = projectId;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/generation/${projectId}`);

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handlers.forEach((handler) => handler(data));
      } catch {
        // ignorar mensajes malformedos
      }
    };

    this.ws.onclose = () => {
      // Reconectar solo si sigue siendo el mismo proyecto
      if (this.projectId === projectId) {
        this.reconnectTimer = setTimeout(() => this.connect(projectId), 3000);
      }
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect(): void {
    this.closeConnection(true);
  }

  private closeConnection(clearProject: boolean): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.onclose = null; // evitar reconnect loop
      this.ws.close();
      this.ws = null;
    }
    if (clearProject) {
      this.projectId = null;
    }
  }

  onMessage(handler: WsMessageHandler): () => void {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }
}

export const wsClient = new GenerationWebSocket();
