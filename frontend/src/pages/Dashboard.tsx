import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useProjectStore } from '@/stores/projectStore';
import { GENRES } from '@/data/genres';
import { Button } from '@/components/ui/Button';

export function Dashboard() {
  const fetchList = useProjectStore((s) => s.fetchList);
  const list = useProjectStore((s) => s.list);

  useQuery({ queryKey: ['projects'], queryFn: fetchList });

  const totalScenes = list.reduce((a, b) => a + b.scene_count, 0);
  const totalDur = list.reduce((a, b) => a + b.duration_minutes, 0);

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Historias Generadas"
          value={String(list.length)}
          sub="Todas completadas"
          subColor="text-emerald"
          icon="fa-film"
        />
        <StatCard
          label="Tiempo Total"
          value={`${totalDur}`}
          unit="min"
          sub={`${totalScenes} escenas totales`}
          icon="fa-clock"
        />
        <StatCard
          label="Cortos Generados"
          value={String(list.filter((x) => x.status === 'completado').length * 3)}
          sub="Para TikTok y Shorts"
          icon="fa-mobile-screen"
        />
        <StatCard
          label="Modelos Cargados"
          value="3"
          unit="/ 5"
          sub="LLM + SDXL + F5-TTS"
          subColor="text-muted"
          icon="fa-brain"
          iconColor="text-emerald"
        />
      </div>

      {/* Acción rápida + Recientes */}
      <div className="grid grid-cols-3 gap-6">
        <div className="glass p-6">
          <h3 className="text-sm font-semibold font-heading mb-4">Acción Rápida</h3>
          <p className="text-xs text-muted mb-5">
            Genera una historia completa con un solo clic. La IA decide todo: mundo, personajes,
            conflicto y desenlace.
          </p>
          <Link to="/creator">
            <Button fullWidth size="lg">
              <i className="fa-solid fa-wand-magic-sparkles mr-2" />
              GENERAR PRÓXIMA HISTORIA
            </Button>
          </Link>
          <div className="mt-4 pt-4 border-t border-bdr space-y-2">
            <CheckItem text="Duración mínima: 20 minutos" />
            <CheckItem text="Cortos automáticos incluidos" />
            <CheckItem text="SEO multiplataforma" />
          </div>
        </div>

        <div className="col-span-2 glass p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold font-heading">Proyectos Recientes</h3>
            <Link
              to="/projects"
              className="text-xs text-amber hover:text-amber-hover transition-colors"
            >
              Ver todos <i className="fa-solid fa-arrow-right ml-1 text-[10px]" />
            </Link>
          </div>
          {list.length === 0 ? (
            <p className="text-xs text-dim text-center py-8">
              No hay proyectos aún. Crea tu primera historia.
            </p>
          ) : (
            <div className="space-y-3">
              {list.slice(0, 5).map((proj) => (
                <Link
                  key={proj.id}
                  to={`/projects/${proj.id}`}
                  className="flex items-center gap-4 p-3 rounded-lg hover:bg-card-hover transition-colors group"
                >
                  <div className="w-16 h-10 rounded-lg overflow-hidden flex-shrink-0 bg-card">
                    <img
                      src={`https://picsum.photos/seed/${proj.id}story/128/80`}
                      className="w-full h-full object-cover"
                      alt=""
                      loading="lazy"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate group-hover:text-amber transition-colors">
                      {proj.title}
                    </p>
                    <p className="text-[11px] text-muted">
                      {proj.genres.map((g) => GENRES.find((x) => x.id === g)?.name ?? g).join(' + ')} ·{' '}
                      {proj.duration_minutes} min · {proj.scene_count} escenas
                    </p>
                  </div>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-medium ml-1 ${
                      proj.status === 'completado'
                        ? 'bg-emerald/10 text-emerald'
                        : 'bg-amber/10 text-amber'
                    }`}
                  >
                    {proj.status}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Pipeline Status */}
      <div className="glass p-6">
        <h3 className="text-sm font-semibold font-heading mb-4">
          Estado del Pipeline — Agentes IA
        </h3>
        <div className="flex items-center gap-1 overflow-x-auto pb-2">
          {['Director', 'Guionista', 'Editor', 'Storyboard', 'Diseñador Chars', 'Dir. Visual', 'Gen. Imágenes', 'Gen. Voces', 'FFmpeg', 'SEO', 'QA'].map(
            (name, i) => (
              <div key={name} className="flex items-center">
                {i > 0 && <div className="w-[30px] h-[2px] bg-bdr flex-shrink-0" />}
                <div className="px-3 py-2 rounded-xl border border-bdr bg-main min-w-[90px] text-center opacity-40 flex-shrink-0">
                  <p className="text-[10px] font-medium text-dim whitespace-nowrap">{name}</p>
                </div>
              </div>
            ),
          )}
        </div>
        <p className="text-xs text-dim mt-3">
          <i className="fa-solid fa-circle-info mr-1" />
          Los agentes se activan secuencialmente durante la generación para optimizar el uso de VRAM.
        </p>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  unit,
  sub,
  subColor = 'text-emerald',
  icon,
  iconColor = 'text-amber',
}: {
  label: string;
  value: string;
  unit?: string;
  sub: string;
  subColor?: string;
  icon: string;
  iconColor?: string;
}) {
  return (
    <div className="p-5 rounded-xl bg-gradient-to-br from-card/90 to-main/90 border border-bdr">
      <div className="flex items-center justify-between mb-3">
        <span className="text-muted text-xs font-medium">{label}</span>
        <div className={`w-8 h-8 rounded-lg bg-amber/10 flex items-center justify-center`}>
          <i className={`fa-solid ${icon} ${iconColor} text-sm`} />
        </div>
      </div>
      <p className="text-3xl font-bold font-heading">
        {value}
        {unit && <span className="text-lg text-muted">{unit}</span>}
      </p>
      <p className={`text-xs ${subColor} mt-1`}>{sub}</p>
    </div>
  );
}

function CheckItem({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3 text-xs text-muted">
      <i className="fa-solid fa-circle-check text-emerald text-[10px]" />
      <span>{text}</span>
    </div>
  );
}