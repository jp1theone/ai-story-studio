import { useGenerationStore } from '@/stores/generationStore';
import { useGenerationPolling } from '@/hooks/useGeneration';
import { ModeSelector } from '@/components/creator/ModeSelector';
import { GenreSelector } from '@/components/creator/GenreSelector';
import { StyleSelector } from '@/components/creator/StyleSelector';
import { ParamSliders } from '@/components/creator/ParamSliders';
import { PlatformSelector } from '@/components/creator/PlatformSelector';
import { PreviewPanel } from '@/components/creator/PreviewPanel';
import { AgentPipeline } from '@/components/pipeline/AgentPipeline';
import { AgentLog } from '@/components/pipeline/AgentLog';
import { SceneProgress } from '@/components/pipeline/SceneProgress';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Button } from '@/components/ui/Button';
import { ProjectResult } from './ProjectResult';
import { ShortsGeneration } from './ShortsGeneration';

export function Creator() {
  const request = useGenerationStore((s) => s.request);
  const setRequest = useGenerationStore((s) => s.setRequest);
  const phase = useGenerationStore((s) => s.phase);
  const progress = useGenerationStore((s) => s.progress);
  const currentAgentIndex = useGenerationStore((s) => s.currentAgentIndex);
  const log = useGenerationStore((s) => s.log);
  const agentStates = useGenerationStore((s) => s.agentStates);
  const scenesGenerated = useGenerationStore((s) => s.scenesGenerated);
  const totalScenes = useGenerationStore((s) => s.totalScenes);
  const currentChapter = useGenerationStore((s) => s.currentChapter);
  const totalChapters = useGenerationStore((s) => s.totalChapters);
  const projectId = useGenerationStore((s) => s.projectId);
  const startGeneration = useGenerationStore((s) => s.startGeneration);
  const reset = useGenerationStore((s) => s.reset);
  const generationError = useGenerationStore((s) => s.error);

  useGenerationPolling(projectId);

  if (phase === 'failed') {
    return (
      <div className="p-6 text-center animate-fade-in">
        <i className="fa-solid fa-circle-exclamation text-3xl text-rose mb-3 block" />
        <h3 className="text-lg font-bold font-heading">La generación no pudo completarse</h3>
        <p className="text-sm text-muted mt-2 mb-5">
          {generationError ?? 'Revisa el registro de la consola del backend y vuelve a intentarlo.'}
        </p>
        <Button onClick={reset}>Volver a intentar</Button>
      </div>
    );
  }

  // Si terminó, mostrar resultado
  if (phase === 'done' && projectId) {
    return <ProjectResult projectId={projectId} onNewStory={() => reset()} />;
  }

  // Si está generando cortos
  if (phase === 'shorts' || phase === 'shorts_done') {
    return <ShortsGeneration />;
  }

  // Si está en pipeline
  if (phase === 'generating') {
    const isMultiChapter = totalChapters > 1;
    return (
      <div className="p-6 animate-fade-in">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold font-heading">Pipeline de Producción</h3>
            <p className="text-xs text-muted mt-0.5">
              Los agentes trabajan secuencialmente para optimizar VRAM
            </p>
          </div>
          <div className="flex items-center gap-4">
            {/* Indicador de capítulos */}
            {isMultiChapter && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber/10 border border-amber/20">
                <i className="fa-solid fa-layer-group text-amber text-xs" />
                <span className="text-xs text-amber font-semibold">
                  {currentChapter > 0
                    ? `Cap. ${currentChapter} / ${totalChapters}`
                    : `${totalChapters} capítulos`}
                </span>
              </div>
            )}
            {/* Indicador de escenas */}
            {totalScenes > 0 && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-card border border-bdr">
                <i className="fa-solid fa-film text-dim text-xs" />
                <span className="text-xs text-muted">
                  <span className="text-txt font-semibold">{scenesGenerated}</span>/{totalScenes} escenas
                </span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted">Progreso</span>
              <span className="text-sm font-bold text-amber">{progress}%</span>
            </div>
          </div>
        </div>

        <ProgressBar value={progress} className="mb-5" size="md" />

        {/* Barra de capítulos si es multi-capítulo */}
        {isMultiChapter && (
          <div className="mb-5 flex gap-1.5 overflow-x-auto pb-1">
            {Array.from({ length: totalChapters }, (_, i) => {
              const ch = i + 1;
              const isDone = ch < currentChapter;
              const isActive = ch === currentChapter;
              return (
                <div
                  key={ch}
                  className={`
                    flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-semibold border transition-all
                    ${isDone
                      ? 'bg-emerald/10 border-emerald/30 text-emerald'
                      : isActive
                        ? 'bg-amber/10 border-amber/50 text-amber animate-pulse'
                        : 'bg-deep border-bdr text-dim'
                    }
                  `}
                >
                  {isDone && <i className="fa-solid fa-check text-[9px]" />}
                  {isActive && <i className="fa-solid fa-spinner animate-spin text-[9px]" />}
                  Cap. {ch}
                </div>
              );
            })}
          </div>
        )}

        <AgentPipeline agentStates={agentStates} />

        <div className="grid grid-cols-5 gap-4 mt-4" style={{ height: 'calc(100vh - 380px)' }}>
          <div className="col-span-3">
            <AgentLog log={log} currentAgentIndex={currentAgentIndex} />
          </div>
          <div className="col-span-2">
            <SceneProgress scenes={[]} imagesGenerated={scenesGenerated} />
          </div>
        </div>
      </div>
    );
  }

  // Vista de configuración (default)
  const toggleGenre = (id: string) => {
    const next = request.genres.includes(id)
      ? request.genres.filter((g) => g !== id)
      : [...request.genres, id];
    setRequest({ genres: next });
  };

  const isLong = request.duration_minutes > 25;
  const estimatedChapters = isLong
    ? Math.ceil(request.duration_minutes / request.chapter_duration_minutes)
    : 1;
  const estimatedScenes = Math.round(request.duration_minutes * 0.5);

  return (
    <div className="p-6 animate-fade-in">
      <div className="flex gap-6 h-[calc(100vh-110px)]">
        {/* Panel Izquierdo */}
        <div className="w-[380px] flex-shrink-0 overflow-y-auto pr-2 space-y-5">
          <Section title="MODO DE GENERACIÓN" icon="fa-sliders">
            <ModeSelector
              mode={request.mode}
              onChange={(mode) => setRequest({ mode })}
            />
            {(request.mode === 'prompt' || request.mode === 'expand') && (
              <textarea
                className="mt-3 w-full bg-deep border border-bdr rounded-lg p-3 text-xs text-txt placeholder-dim resize-none focus:outline-none focus:border-amber/50 transition-colors"
                rows={4}
                placeholder={
                  request.mode === 'prompt'
                    ? 'Describe tu idea de historia de anime...'
                    : 'Pega el texto a expandir (10+ páginas)...'
                }
                value={request.prompt_text ?? ''}
                onChange={(e) => setRequest({ prompt_text: e.target.value })}
              />
            )}
            {request.mode === 'manuscript' && (
              <div className="mt-3 border-2 border-dashed border-bdr rounded-lg p-6 text-center cursor-pointer hover:border-amber/30 transition-colors">
                <i className="fa-solid fa-cloud-arrow-up text-2xl text-dim mb-2 block" />
                <p className="text-xs text-muted">Arrastra TXT, DOCX o PDF aquí</p>
                <p className="text-[10px] text-dim mt-1">o haz clic para seleccionar</p>
              </div>
            )}
          </Section>

          <Section title={`GÉNEROS (${request.genres.length} seleccionados)`} icon="fa-masks-theater">
            <GenreSelector selected={request.genres} onToggle={toggleGenre} />
          </Section>

          <Section title="ESTILO VISUAL" icon="fa-palette">
            <StyleSelector selected={request.style} onChange={(id) => setRequest({ style: id })} />
          </Section>

          <Section title="PARÁMETROS" icon="fa-gear">
            <ParamSliders />
          </Section>

          <Section title="PLATAFORMAS DE EXPORTACIÓN" icon="fa-share-nodes">
            <PlatformSelector />
          </Section>
        </div>

        {/* Panel Derecho */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="glass p-6 flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold font-heading">Vista Previa de Generación</h3>
              <div className="flex items-center gap-3">
                {isLong && (
                  <span className="flex items-center gap-1.5 text-[10px] px-2 py-1 rounded-full bg-amber/10 border border-amber/20 text-amber">
                    <i className="fa-solid fa-layer-group text-[9px]" />
                    {estimatedChapters} capítulos
                  </span>
                )}
                <span className="text-xs text-muted">
                  ~{estimatedScenes} escenas estimadas
                </span>
              </div>
            </div>
            <PreviewPanel />
          </div>

          <div className="mt-4">
            <Button
              fullWidth
              size="lg"
              disabled={request.genres.length === 0}
              onClick={startGeneration}
            >
              <i className="fa-solid fa-wand-magic-sparkles mr-2" />
              {isLong
                ? `GENERAR ${estimatedChapters} CAPÍTULOS (${request.duration_minutes} MIN)`
                : 'GENERAR HISTORIA DE ANIME'}
            </Button>
            {request.genres.length === 0 && (
              <p className="text-[10px] text-dim text-center mt-2">
                Selecciona al menos un género para continuar
              </p>
            )}
            {generationError && (
              <div className="mt-3 rounded-lg border border-rose/30 bg-rose/10 px-3 py-2 text-xs text-rose">
                <i className="fa-solid fa-circle-exclamation mr-1.5" />
                No se pudo iniciar la generación: {generationError}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Section({
  title,
  icon,
  children,
}: {
  title: string;
  icon: string;
  children: React.ReactNode;
}) {
  return (
    <div className="glass-sm p-4">
      <h4 className="text-xs font-semibold font-heading mb-3 flex items-center gap-2">
        <i className={`fa-solid ${icon} text-amber text-[10px]`} />
        {title}
      </h4>
      {children}
    </div>
  );
}
