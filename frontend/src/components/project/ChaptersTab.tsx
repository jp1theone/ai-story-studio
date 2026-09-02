import type { Project } from '@/types/project';
import { Button } from '../ui/Button';
import { toast } from '../ui/Toast';
import { api } from '@/services/api';

interface ChaptersTabProps {
  project: Project;
}

const EMOTION_ICONS: Record<string, string> = {
  intriga: '🔍',
  drama: '🎭',
  accion: '⚡',
  tension: '😤',
  giro: '🌀',
  melancolia: '🌧️',
  impacto: '💥',
  esperanza: '✨',
  tragedia: '💔',
  resolucion: '🏆',
  romance: '💖',
  terror: '👻',
  sorpresa: '😱',
  misterio: '🌑',
};

export function ChaptersTab({ project }: ChaptersTabProps) {
  const chapters = project.chapters ?? [];
  const scenes = project.scenes ?? [];

  if (chapters.length === 0) {
    return (
      <div className="text-center py-12 text-muted">
        <i className="fa-solid fa-layer-group text-3xl mb-3 block text-dim" />
        <p className="text-sm">Esta historia es un video único sin capítulos.</p>
        <p className="text-xs text-dim mt-1">
          Para dividir en capítulos, usa duraciones mayores a 25 minutos.
        </p>
      </div>
    );
  }

  const totalDuration = chapters.reduce((acc, ch) => acc + (ch.duration_minutes || 0), 0);
  const totalScenes = scenes.length;

  return (
    <div className="space-y-5">
      {/* Resumen */}
      <div className="grid grid-cols-3 gap-3">
        <StatCard icon="fa-layer-group" label="Capítulos" value={String(chapters.length)} color="amber" />
        <StatCard icon="fa-clock" label="Duración total" value={`${totalDuration} min`} color="blue" />
        <StatCard icon="fa-film" label="Escenas totales" value={String(totalScenes)} color="green" />
      </div>

      {/* Lista de capítulos */}
      <div className="space-y-4">
        {chapters.map((chapter) => {
          const chScenes = scenes.filter((s) => s.chapter_number === chapter.chapter_number);
          const emotions = [...new Set(chScenes.map((s) => s.emotion))];

          return (
            <div key={chapter.chapter_number} className="glass p-5">
              {/* Header del capítulo */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-amber/10 border border-amber/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-amber">{chapter.chapter_number}</span>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold font-heading">{chapter.title}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-dim">
                        <i className="fa-regular fa-clock mr-1" />
                        {chapter.duration_minutes} min
                      </span>
                      <span className="text-dim">·</span>
                      <span className="text-[10px] text-dim">
                        <i className="fa-solid fa-film mr-1" />
                        {chScenes.length} escenas
                      </span>
                      <span className="text-dim">·</span>
                      <span className="text-[10px] text-dim">
                        Esc. {chapter.start_scene_number}–{chapter.end_scene_number}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Botón de descarga */}
                <Button
                  variant={chapter.video_path ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => {
                    if (chapter.video_path) {
                      window.location.assign(api.projects.downloadUrl(project.id, { path: chapter.video_path }));
                      toast(`Preparando la descarga del capítulo ${chapter.chapter_number}...`, 'success');
                    } else {
                      toast('Video del capítulo no disponible aún.', 'warning');
                    }
                  }}
                >
                  <i className={`fa-solid ${chapter.video_path ? 'fa-download' : 'fa-hourglass-half'} mr-1`} />
                  {chapter.video_path ? 'Descargar' : 'Pendiente'}
                </Button>
              </div>

              {/* Sinopsis */}
              {chapter.synopsis && (
                <p className="text-xs text-muted leading-relaxed mb-3 pl-13">
                  {chapter.synopsis}
                </p>
              )}

              {/* Emociones presentes */}
              {emotions.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {emotions.slice(0, 6).map((emo) => (
                    <span
                      key={emo}
                      className="text-[10px] px-2 py-0.5 rounded-full bg-deep border border-bdr text-muted flex items-center gap-1"
                    >
                      {EMOTION_ICONS[emo] ?? '🎬'} {emo}
                    </span>
                  ))}
                </div>
              )}

              {/* Cliffhanger (si no es el último capítulo) */}
              {chapter.cliffhanger && (
                <div className="mt-3 rounded-lg bg-deep border border-bdr p-3">
                  <p className="text-[10px] text-dim mb-1 flex items-center gap-1 font-semibold">
                    <i className="fa-solid fa-bolt text-amber" />
                    CLIFFHANGER
                  </p>
                  <p className="text-xs text-muted italic">"{chapter.cliffhanger}"</p>
                </div>
              )}

              {/* Barra de escenas */}
              <div className="mt-3 flex gap-0.5 h-1.5 rounded-full overflow-hidden bg-deep">
                {chScenes.map((scene) => (
                  <div
                    key={scene.scene_number}
                    className={`flex-1 transition-all ${
                      scene.image_path && scene.audio_path
                        ? 'bg-emerald'
                        : scene.image_path
                          ? 'bg-amber'
                          : 'bg-bdr'
                    }`}
                    title={`Escena ${scene.scene_number}: ${scene.title}`}
                  />
                ))}
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-[9px] text-dim">
                  {chScenes.filter((s) => s.image_path && s.audio_path).length}/{chScenes.length} completas
                </span>
                {chapter.video_path && (
                  <span className="text-[9px] text-emerald flex items-center gap-1">
                    <i className="fa-solid fa-circle-check" /> Video listo
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Descarga completa */}
      <div className="glass p-4 border border-amber/20">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold font-heading">Video Completo</p>
            <p className="text-[10px] text-dim mt-0.5">
              Todos los capítulos unidos en un solo archivo · {totalDuration} min
            </p>
          </div>
          <Button
            onClick={() =>
              toast(
                `Video completo disponible en output/${project.id}/youtube/`,
                'success'
              )
            }
          >
            <i className="fa-solid fa-download mr-1" />
            Descargar Completo
          </Button>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: string;
  label: string;
  value: string;
  color: 'amber' | 'blue' | 'green';
}) {
  const colorMap = {
    amber: 'text-amber bg-amber/10 border-amber/20',
    blue: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    green: 'text-emerald bg-emerald/10 border-emerald/20',
  };
  return (
    <div className={`glass p-3 rounded-lg border ${colorMap[color]}`}>
      <i className={`fa-solid ${icon} text-lg mb-1 block`} />
      <p className="text-lg font-bold font-heading">{value}</p>
      <p className="text-[10px] text-muted">{label}</p>
    </div>
  );
}
