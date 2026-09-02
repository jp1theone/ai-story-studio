import { useGenerationStore } from '@/stores/generationStore';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';

const MOCK_SHORTS = [
  { id: 1, title: 'El inicio que no esperabas', hook: 'Todo cambió en un solo momento...', duration: '8:30' },
  { id: 2, title: 'El giro que lo cambió todo', hook: 'Nunca vi esto venir...', duration: '9:15' },
  { id: 3, title: 'La verdad sale a la luz', hook: 'No podía creer lo que veía...', duration: '10:00' },
  { id: 4, title: 'El final que te dejará sin palabras', hook: 'Nadie esperaba este final...', duration: '8:45' },
];

export function ShortsGeneration() {
  const phase = useGenerationStore((s) => s.phase);
  const progress = useGenerationStore((s) => s.progress);
  const log = useGenerationStore((s) => s.log);

  if (phase === 'shorts') {
    return (
      <div className="p-6 animate-fade-in">
        <h3 className="text-lg font-bold font-heading mb-2">Generación de Cortos</h3>
        <p className="text-xs text-muted mb-6">
          Extrayendo momentos clave y generando versiones verticales
        </p>
        <ProgressBar value={progress} className="mb-6" size="md" />
        <div className="glass p-4">
          <div className="text-xs text-muted space-y-1.5 font-mono leading-relaxed max-h-[60vh] overflow-y-auto">
            {log.map((entry, i) => (
              <div
                key={i}
                className={`animate-slide-in ${
                  entry.log_type === 'success'
                    ? 'text-emerald'
                    : entry.log_type === 'error'
                      ? 'text-rose'
                      : entry.log_type === 'warning'
                        ? 'text-amber'
                        : ''
                }`}
              >
                {entry.message}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // phase === 'shorts_done'
  return (
    <div className="p-6 animate-fade-in">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold font-heading">Cortos Generados</h3>
          <p className="text-xs text-muted mt-1">{MOCK_SHORTS.length} cortos extraídos</p>
        </div>
        <Button
          variant="secondary"
          onClick={() => useGenerationStore.getState().setRequest({} as never)}
        >
          <i className="fa-solid fa-arrow-left mr-1" />
          Volver al Proyecto
        </Button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {MOCK_SHORTS.map((s) => (
          <div
            key={s.id}
            className="glass overflow-hidden hover:border-amber/30 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="aspect-[9/16] relative">
              <img
                src={`https://picsum.photos/seed/${s.id}short/360/640`}
                className="w-full h-full object-cover"
                alt=""
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-3">
                <p className="text-xs font-bold mb-1">{s.title}</p>
                <p className="text-[10px] text-white/70 mb-2">"{s.hook}"</p>
                <div className="flex items-center gap-2">
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/20 text-white">
                    {s.duration}
                  </span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/20 text-white">
                    1080x1920
                  </span>
                </div>
              </div>
            </div>
            <div className="p-3 space-y-2">
              <div className="flex items-center gap-1">
                <i className="fa-brands fa-tiktok text-xs text-dim" />
                <i className="fa-brands fa-facebook text-xs text-dim" />
                <i className="fa-solid fa-mobile-screen text-xs text-dim" />
              </div>
              <Button
                variant="secondary"
                fullWidth
                size="sm"
                onClick={() => toast(`Corto descargado: ${s.title}`, 'success')}
              >
                <i className="fa-solid fa-download mr-1" />
                Descargar
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}