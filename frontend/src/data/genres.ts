export interface GenreDef {
  id: string;
  name: string;
  icon: string;
}

export const GENRES: GenreDef[] = [
  { id: 'romance', name: 'Romance', icon: 'fa-heart' },
  { id: 'ceo', name: 'CEO', icon: 'fa-briefcase' },
  { id: 'drama', name: 'Drama', icon: 'fa-masks-theater' },
  { id: 'fantasia', name: 'Fantasía', icon: 'fa-hat-wizard' },
  { id: 'mafia', name: 'Mafia', icon: 'fa-gun' },
  { id: 'venganza', name: 'Venganza', icon: 'fa-fire' },
  { id: 'escolar', name: 'Escolar', icon: 'fa-school' },
  { id: 'reencarnacion', name: 'Reencarnación', icon: 'fa-rotate' },
  { id: 'rpg', name: 'Sistema RPG', icon: 'fa-gamepad' },
  { id: 'sobrenatural', name: 'Sobrenatural', icon: 'fa-ghost' },
  { id: 'accion', name: 'Acción', icon: 'fa-explosion' },
  { id: 'cultivacion', name: 'Cultivación', icon: 'fa-mountain-sun' },
  { id: 'sliceoflife', name: 'Slice of Life', icon: 'fa-coffee' },
  { id: 'reddit', name: 'Historia Reddit', icon: 'fa-comments' },
  { id: 'viral', name: 'Viral Facebook', icon: 'fa-share-nodes' },
  { id: 'youtube', name: 'Narrada YouTube', icon: 'fa-play' },
];