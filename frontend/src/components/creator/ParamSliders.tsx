import { useGenerationStore } from '@/stores/generationStore';

export function ParamSliders() {
  const request = useGenerationStore((s) => s.request);
  const setRequest = useGenerationStore((s) => s.setRequest);

  const toneLabel = request.tone < 40 ? 'Ligero' : request.tone < 70 ? 'Equilibrado' : 'Oscuro';
  const isLong = request.duration_minutes > 25;
  const estimatedChapters = isLong
    ? Math.ceil(request.duration_minutes / request.chapter_duration_minutes)
    : 1;

  return (
    <div className="space-y-5">
      {/* Duración */}
      <div>
        <div className="flex justify-between mb-2">
          <label className="text-xs text-muted">Duración del video</label>
          <span className="text-xs font-semibold text-amber">{request.duration_minutes} min</span>
        </div>
        <input
          type="range"
          min={3}
          max={120}
          step={1}
          value={request.duration_minutes}
          onChange={(e) => setRequest({ duration_minutes: parseInt(e.target.value) })}
          className="w-full"
        />
        <div className="flex justify-between text-[9px] text-dim mt-1">
          <span>3 min</span>
          <span>30 min</span>
          <span>60 min</span>
          <span>120 min</span>
        </div>

        {/* Advertencia de video largo + capítulos */}
        {isLong && (
          <div className="mt-3 rounded-lg border border-amber/30 bg-amber/5 p-3">
            <div className="flex items-start gap-2">
              <i className="fa-solid fa-layer-group text-amber text-sm mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-[11px] font-semibold text-amber mb-1">
                  Modo Capítulos Automático
                </p>
                <p className="text-[10px] text-muted leading-relaxed">
                  Videos {'>'}25 min se dividen en <span className="text-amber font-semibold">{estimatedChapters} capítulos</span> de ~{request.chapter_duration_minutes} min cada uno para máxima calidad.
                </p>
              </div>
            </div>

            {/* Slider de duración por capítulo */}
            <div className="mt-3">
              <div className="flex justify-between mb-1.5">
                <label className="text-[10px] text-muted">Duración por capítulo</label>
                <span className="text-[10px] font-semibold text-amber">
                  ~{request.chapter_duration_minutes} min
                </span>
              </div>
              <input
                type="range"
                min={10}
                max={30}
                step={5}
                value={request.chapter_duration_minutes}
                onChange={(e) =>
                  setRequest({ chapter_duration_minutes: parseInt(e.target.value) })
                }
                className="w-full"
              />
              <div className="flex justify-between text-[9px] text-dim mt-1">
                <span>10 min</span>
                <span>20 min</span>
                <span>30 min</span>
              </div>
            </div>

            {/* Resumen de capítulos */}
            <div className="mt-2 flex flex-wrap gap-1">
              {Array.from({ length: estimatedChapters }, (_, i) => (
                <span
                  key={i}
                  className="text-[9px] px-2 py-0.5 rounded-full bg-amber/10 border border-amber/20 text-amber"
                >
                  Cap. {i + 1}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Personajes */}
      <div>
        <div className="flex justify-between mb-2">
          <label className="text-xs text-muted">Personajes principales</label>
          <span className="text-xs font-semibold text-amber">{request.num_characters}</span>
        </div>
        <input
          type="range"
          min={2}
          max={6}
          value={request.num_characters}
          onChange={(e) => setRequest({ num_characters: parseInt(e.target.value) })}
          className="w-full"
        />
        <div className="flex justify-between text-[9px] text-dim mt-1">
          <span>2 personajes</span>
          <span>6 personajes</span>
        </div>
      </div>

      {/* Tono */}
      <div>
        <div className="flex justify-between mb-2">
          <label className="text-xs text-muted">Tono narrativo</label>
          <span className="text-xs font-semibold text-amber">{toneLabel}</span>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          value={request.tone}
          onChange={(e) => setRequest({ tone: parseInt(e.target.value) })}
          className="w-full"
        />
        <div className="flex justify-between text-[9px] text-dim mt-1">
          <span>🌸 Ligero</span>
          <span>⚖️ Equilibrado</span>
          <span>🌑 Oscuro</span>
        </div>
      </div>

      {/* Activar capítulos manualmente para videos cortos */}
      {!isLong && (
        <div>
          <label className="flex items-center gap-2 cursor-pointer group">
            <div
              className={`
                relative w-9 h-5 rounded-full transition-colors duration-200
                ${request.chapters_mode ? 'bg-amber' : 'bg-bdr'}
              `}
              onClick={() => setRequest({ chapters_mode: !request.chapters_mode })}
            >
              <div
                className={`
                  absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200
                  ${request.chapters_mode ? 'translate-x-4' : 'translate-x-0.5'}
                `}
              />
            </div>
            <span className="text-xs text-muted group-hover:text-txt transition-colors">
              Dividir en capítulos
            </span>
          </label>
        </div>
      )}
    </div>
  );
}