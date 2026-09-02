export interface Character {
  id: number;
  name: string;
  role: string;
  description: string;
  appearance: string;
  voice_type: string;
  reference_image_path?: string;
}

export interface Scene {
  id: number;
  scene_number: number;
  chapter_number?: number;
  title: string;
  narration: string;
  emotion: string;
  camera: string;
  image_prompt: string;
  duration_seconds: number;
  character_names: string[];
  image_path?: string;
  audio_path?: string;
}

export interface Chapter {
  id: number;
  chapter_number: number;
  title: string;
  synopsis?: string;
  duration_minutes: number;
  cliffhanger?: string;
  video_path?: string;
  start_scene_number: number;
  end_scene_number: number;
}

export interface Short {
  id: number;
  title: string;
  hook: string;
  start_scene_number: number;
  end_scene_number: number;
  duration_string: string;
  platforms: string[];
  video_path?: string;
}

export interface SeoData {
  youtube?: PlatformSeo;
  tiktok?: PlatformSeo;
  facebook?: PlatformSeo;
  shorts?: PlatformSeo;
  thumbnail_text?: string;
}

export interface PlatformSeo {
  title: string;
  description: string;
  tags: string[];
}

export interface Project {
  id: number;
  title: string;
  synopsis?: string;
  genres: string[];
  style: string;
  duration_minutes: number;
  tone: number;
  mode: string;
  platforms: string[];
  status: 'pendiente' | 'generando' | 'completado' | 'fallido';
  seo_data?: SeoData;
  chapters_mode: boolean;
  chapter_duration_minutes: number;
  total_chapters: number;
  created_at: string;
  scenes: Scene[];
  characters: Character[];
  shorts: Short[];
  chapters: Chapter[];
}

export interface ProjectListItem {
  id: number;
  title: string;
  genres: string[];
  style: string;
  duration_minutes: number;
  total_chapters: number;
  chapters_mode: boolean;
  status: string;
  created_at: string;
  scene_count: number;
}
