export interface GenerationRequest {
  mode: 'auto' | 'prompt' | 'manuscript' | 'expand' | 'continue';
  genres: string[];
  style: string;
  duration_minutes: number;
  num_characters: number;
  tone: number;
  platforms: string[];
  prompt_text?: string;
  continue_from_project_id?: number;
  // Soporte capítulos
  chapters_mode: boolean;
  chapter_duration_minutes: number;
}

export interface AgentLogEntry {
  agent: string;
  message: string;
  log_type: 'info' | 'success' | 'warning' | 'error';
}

export interface ChapterInfo {
  chapter_number: number;
  title: string;
  synopsis?: string;
  duration_minutes: number;
  start_scene: number;
  end_scene: number;
  video_path?: string;
}

export interface GenerationStatus {
  project_id: number | null;
  phase: 'idle' | 'generating' | 'shorts' | 'done' | 'failed';
  current_agent_index: number;
  progress: number;
  scenes_generated: number;
  total_scenes: number;
  current_chapter: number;
  total_chapters: number;
  log: AgentLogEntry[];
  chapters: ChapterInfo[];
  error?: string | null;
}
