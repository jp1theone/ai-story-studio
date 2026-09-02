import type { Project } from '@/types/project';

interface StoryTabProps {
  project: Project;
}

export function StoryTab({ project }: StoryTabProps) {
  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2 space-y-4">
        <div className="glass p-5">
          <h3 className="text-sm font-semibold font-heading mb-3">Sinopsis</h3>
          <p className="text-sm text-muted leading-relaxed">{project.synopsis}</p>
        </div>
        <div className="glass p-5">
          <h3 className="text-sm font-semibold font-heading mb-4">Escenas</h3>
          <div className="space-y-3">
            {project.scenes.map((s) => (
              <div
                key={s.id}
                className="flex gap-3 p-3 rounded-lg bg-deep border border-bdr hover:border-bdr-light transition-colors"
              >
                <div className="w-20 h-14 rounded-lg overflow-hidden flex-shrink-0">
                  {s.image_path ? (
                    <img
                      src={`/api/projects/${project.id}/scene/${s.id}/image`}
                      className="w-full h-full object-cover"
                      alt=""
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-full h-full animate-shimmer" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-[10px] text-amber font-semibold">
                      ESCENA {s.scene_number}
                    </span>
                    {s.chapter_number && s.chapter_number > 0 && (
                      <>
                        <span className="text-[10px] text-dim">·</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber/10 text-amber">
                          Cap. {s.chapter_number}
                        </span>
                      </>
                    )}
                    <span className="text-[10px] text-dim">·</span>
                    <span className="text-[10px] text-dim">{formatTime(s.duration_seconds)}</span>
                    <span className="text-[10px] text-dim">·</span>
                    <span className="text-[10px] text-dim capitalize">{s.emotion}</span>
                  </div>
                  <p className="text-xs font-medium mb-1">{s.title}</p>
                  <p className="text-[11px] text-muted line-clamp-2">{s.narration}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="glass p-5">
          <h3 className="text-sm font-semibold font-heading mb-3">Personajes</h3>
          <div className="space-y-3">
            {project.characters.map((c) => (
              <div
                key={c.id}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-card-hover transition-colors"
              >
                <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 bg-card">
                  {c.reference_image_path ? (
                    <img
                      src={`/api/projects/${project.id}/character/${c.id}/image`}
                      className="w-full h-full object-cover"
                      alt=""
                    />
                  ) : (
                    <img
                      src={`https://picsum.photos/seed/${encodeURIComponent(c.name)}char/80/80`}
                      className="w-full h-full object-cover"
                      alt=""
                      loading="lazy"
                    />
                  )}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold truncate">{c.name}</p>
                  <p className="text-[10px] text-dim">
                    {c.role} · {c.voice_type}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass p-5">
          <h3 className="text-sm font-semibold font-heading mb-3">Detalles</h3>
          <div className="space-y-2 text-xs">
            <InfoRow label="Duración total" value={`${project.duration_minutes}:00`} />
            <InfoRow label="Escenas" value={String(project.scenes.length)} />
            {project.total_chapters > 1 && (
              <InfoRow label="Capítulos" value={String(project.total_chapters)} />
            )}
            <InfoRow label="Estilo" value={project.style} />
            <InfoRow
              label="Tono"
              value={project.tone < 40 ? 'Ligero' : project.tone < 70 ? 'Equilibrado' : 'Oscuro'}
            />
            <InfoRow label="Plataformas" value={project.platforms.join(', ')} />
          </div>
        </div>

        <div className="glass p-5">
          <h3 className="text-sm font-semibold font-heading mb-3">Miniatura</h3>
          <div className="rounded-lg overflow-hidden aspect-video">
            <img
              src={`https://picsum.photos/seed/${project.id}thumb/640/360`}
              className="w-full h-full object-cover"
              alt="Miniatura"
              loading="lazy"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-muted">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}
