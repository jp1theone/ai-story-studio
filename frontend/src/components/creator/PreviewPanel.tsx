import { useGenerationStore } from '@/stores/generationStore';
import { GENRES } from '@/data/genres';
import { STYLES } from '@/data/styles';
import { PLATFORMS } from './PlatformSelector';

export function PreviewPanel() {
  const request = useGenerationStore((s) => s.request);
  const estimatedScenes = Math.round(request.duration_minutes * 0.5);
  const toneLabel = request.tone < 40 ? 'Ligero' : request.tone < 70 ? 'Equilibrado' : 'Oscuro';
  const styleName = STYLES.find((s) => s.id === request.style)?.name ?? request.style;
  const genreNames = request.genres.map((g) => GENRES.find((x) => x.id === g)?.name ?? g);
  const platformNames = request.platforms.map((p) => PLATFORMS.find((x) => x.id === p)?.name ?? p);

  if (request.genres.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 rounded-2xl bg-card border border-bdr flex items-center justify-center mx-auto mb-4">
            <i className="fa-solid fa-wand-magic-sparkles text-3xl text-dim" />
          </div>
          <p className="text-sm text-muted mb-1">Selecciona al menos un género</p>
          <p className="text-xs text-dim max-w-xs">
            Los géneros definen la estructura narrativa, los arcos de personajes y los giros de la historia.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto space-y-4">
      {/* Resumen */}
      <div className="bg-deep rounded-lg p-4 border border-bdr">
        <h4 className="text-xs font-semibold text-amber mb-3">RESUMEN DE PRODUCCIÓN</h4>
        <div className="grid grid-cols-2 gap-3 text-xs">
          <InfoRow label="Géneros" value={genreNames.join(' + ')} />
          <InfoRow label="Estilo" value={styleName} />
          <InfoRow label="Duración" value={`${request.duration_minutes} minutos`} />
          <InfoRow label="Personajes" value={String(request.num_characters)} />
          <InfoRow label="Escenas" value={`~${estimatedScenes}`} />
          <InfoRow label="Tono" value={toneLabel} />
          <div className="col-span-2">
            <InfoRow label="Plataformas" value={platformNames.join(', ')} />
          </div>
        </div>
      </div>

      {/* Estimación de pipeline */}
      <div className="bg-deep rounded-lg p-4 border border-bdr">
        <h4 className="text-xs font-semibold text-amber mb-3">PIPELINE ESTIMADO</h4>
        <div className="space-y-2">
          <PipelineRow icon="fa-pen-nib" name="Generación de historia" time="15-25s" />
          <PipelineRow icon="fa-image" name={`Generación de ~${estimatedScenes} imágenes`} time="3-6 min" />
          <PipelineRow icon="fa-microphone" name={`Síntesis de ${request.num_characters} voces`} time="2-4 min" />
          <PipelineRow icon="fa-film" name="Ensamblaje de video" time="1-2 min" />
          <PipelineRow icon="fa-mobile-screen" name="Generación de cortos" time="2-3 min" />
          <div className="pt-2 mt-2 border-t border-bdr flex items-center justify-between text-xs">
            <span className="text-muted font-medium">Tiempo total estimado</span>
            <span className="text-amber font-semibold">~8-16 min</span>
          </div>
        </div>
      </div>

      {/* Nota VRAM */}
      <div className="bg-amber/5 border border-amber/20 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <i className="fa-solid fa-triangle-exclamation text-amber text-sm mt-0.5" />
          <div className="text-xs text-muted">
            <p className="font-medium text-amber mb-1">Gestión de VRAM Inteligente</p>
            <p>
              Los modelos se cargan y descargan secuencialmente. Solo un modelo pesado estará en VRAM en
              cada momento. Si experimentas errores de memoria, reduce la resolución en Configuración.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-muted">{label}: </span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

function PipelineRow({ icon, name, time }: { icon: string; name: string; time: string }) {
  return (
    <div className="flex items-center gap-3 text-xs">
      <i className={`fa-solid ${icon} text-dim w-4 text-center text-[10px]`} />
      <span className="flex-1 text-muted">{name}</span>
      <span className="text-dim">{time}</span>
    </div>
  );
}