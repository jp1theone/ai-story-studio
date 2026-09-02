import type { Project } from '@/types/project';

interface CharactersTabProps {
  project: Project;
}

export function CharactersTab({ project }: CharactersTabProps) {
  return (
    <div className="grid grid-cols-2 gap-6">
      {project.characters.map((c) => (
        <div key={c.id} className="glass p-6">
          <div className="flex items-start gap-4 mb-4">
            <div className="w-20 h-20 rounded-xl overflow-hidden flex-shrink-0 bg-card">
              {c.reference_image_path ? (
                <img
                  src={`/api/projects/${project.id}/character/${c.id}/image`}
                  className="w-full h-full object-cover"
                  alt={c.name}
                />
              ) : (
                <img
                  src={`https://picsum.photos/seed/${encodeURIComponent(c.name)}char/160/160`}
                  className="w-full h-full object-cover"
                  alt={c.name}
                  loading="lazy"
                />
              )}
            </div>
            <div>
              <h4 className="text-base font-bold font-heading">{c.name}</h4>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber/10 text-amber font-medium">
                {c.role}
              </span>
              <p className="text-xs text-muted mt-2">{c.description}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-deep rounded-lg p-3">
              <p className="text-dim text-[10px] mb-1">Apariencia</p>
              <p className="text-muted">{c.appearance}</p>
            </div>
            <div className="bg-deep rounded-lg p-3">
              <p className="text-dim text-[10px] mb-1">Voz</p>
              <p className="text-muted">{c.voice_type}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
