export interface StyleDef {
  id: string;
  name: string;
  description: string;
  icon: string;
  emoji: string;
}

export const STYLES: StyleDef[] = [
  { id: 'anime', name: 'Anime', description: 'Japonés clásico', icon: 'fa-star', emoji: '🌸' },
  { id: 'anime-cine', name: 'Anime Cinemático', description: 'Dramático y épico', icon: 'fa-clapperboard', emoji: '🎬' },
  { id: 'realista', name: 'Realista', description: 'Fotografía hiperrealista', icon: 'fa-camera', emoji: '📷' },
  { id: 'semi-realista', name: 'Semi-realista', description: 'CGI artístico 3D', icon: 'fa-cube', emoji: '🖌️' },
  { id: 'manhwa', name: 'Manhwa', description: 'Webtoon coreano', icon: 'fa-book-open', emoji: '📖' },
  { id: 'manga', name: 'Manga Colorizado', description: 'Manga a color', icon: 'fa-paintbrush', emoji: '✏️' },
];