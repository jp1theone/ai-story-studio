import type { AgentDef } from '@/types/agent';

// IMPORTANTE: El orden aquí debe coincidir con agents_pipeline en generation_task.py
// Guionista, Divisor Capítulos, Editor, Storyboard, Diseñador Chars,
// Director Visual, Gen. Imágenes, Gen. Voces, SEO, QA
export const AGENTS: AgentDef[] = [
  { id: 'writer',   name: 'Guionista IA',       icon: 'fa-pen-nib',               description: 'Historia, arcos, giros y diálogos de anime' },
  { id: 'chapters', name: 'Divisor Capítulos',   icon: 'fa-layer-group',           description: 'Organiza la historia en capítulos' },
  { id: 'editor',   name: 'Editor IA',           icon: 'fa-scissors',              description: 'Coherencia, ritmo y calidad narrativa' },
  { id: 'story',    name: 'Storyboard IA',       icon: 'fa-table-cells',           description: 'Escenas, cámara y composición visual' },
  { id: 'chars',    name: 'Diseñador Chars',     icon: 'fa-user-pen',              description: 'Character Bible y consistencia visual' },
  { id: 'visual',   name: 'Director Visual',     icon: 'fa-palette',               description: 'Estilo, paleta de colores y modelo IA' },
  { id: 'images',   name: 'Gen. Imágenes',       icon: 'fa-image',                 description: 'ComfyUI · Anime realista por escena' },
  { id: 'voices',   name: 'Gen. Voces',          icon: 'fa-microphone',            description: 'TTS · Narrador profesional por escena' },
  { id: 'seo',      name: 'SEO IA',              icon: 'fa-magnifying-glass-chart', description: 'Títulos, hashtags y descripciones' },
  { id: 'qa',       name: 'QA IA',              icon: 'fa-check-double',           description: 'Control de calidad final' },
];