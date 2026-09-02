import type { Project } from '@/types/project';

interface ScenesTabProps {
  project: Project;
}

export function ScenesTab({ project }: ScenesTabProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {project.scenes.map((s) => (
        <div
          key={s.id}
          className="rounded-xl overflow-hidden border border-bdr hover:border-amber/30 transition-all duration-300 hover:-translate-y-1 cursor-pointer group"
        >
          <div className="aspect-video relative overflow-hidden">
            {s.image_path ? (
              <img
                src={`/api/projects/${project.id}/scene/${s.id}/image`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                alt=""
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full animate-shimmer" />
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
            <div className="absolute bottom-2 left-2 flex items-center gap-1.5">
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-black/60 text-white font-medium">
                {formatTime(s.duration_seconds)}
              </span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-black/60 text-white capitalize">
                {s.emotion}
              </span>
            </div>
          </div>
          <div className="p-3">
            <p className="text-xs font-semibold mb-1">
              Escena {s.scene_number}: {s.title}
            </p>
            <p className="text-[11px] text-muted line-clamp-2">{s.narration}</p>
            <div className="flex items-center gap-2 mt-2 text-[10px] text-dim">
              <span>
                <i className="fa-solid fa-video mr-1" />
                {s.camera}
              </span>
              <span>
                <i className="fa-solid fa-users mr-1" />
                {s.character_names.length}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}