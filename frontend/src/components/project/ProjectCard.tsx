import { Link } from 'react-router-dom';
import type { ProjectListItem } from '@/types/project';
import { GENRES } from '@/data/genres';
import { STYLES } from '@/data/styles';

interface ProjectCardProps {
  project: ProjectListItem;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const genreNames = project.genres
    .map((g) => GENRES.find((x) => x.id === g)?.name ?? g)
    .join(' + ');
  const styleName = STYLES.find((s) => s.id === project.style)?.name ?? project.style;

  return (
    <Link
      to={`/projects/${project.id}`}
      className="glass overflow-hidden hover:border-amber/20 transition-all duration-300 group block"
    >
      <div className="aspect-video relative overflow-hidden">
        <img
          src={`https://picsum.photos/seed/${project.id}story/480/270`}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          alt=""
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        <div className="absolute bottom-3 left-3 right-3">
          <p className="text-sm font-bold">{project.title}</p>
          <p className="text-[10px] text-white/70">{genreNames}</p>
        </div>
        <div className="absolute top-3 right-3">
          <span
            className={`text-[9px] px-2 py-0.5 rounded-full font-semibold ${
              project.status === 'completado'
                ? 'bg-emerald/20 text-emerald'
                : project.status === 'fallido'
                  ? 'bg-rose/20 text-rose'
                  : 'bg-amber/20 text-amber'
            }`}
          >
            {project.status}
          </span>
        </div>
      </div>
      <div className="p-4">
        <div className="grid grid-cols-3 gap-2 text-xs">
          <Stat label="Duración" value={`${project.duration_minutes} min`} />
          <Stat
            label={project.chapters_mode ? 'Capítulos' : 'Escenas'}
            value={project.chapters_mode ? String(project.total_chapters) : String(project.scene_count)}
          />
          <Stat label="Fecha" value={project.created_at.split('-').slice(1).join('/')} />
        </div>
        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-bdr">
          {project.chapters_mode && (
            <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-amber/10 text-amber border border-amber/20 flex items-center gap-0.5">
              <i className="fa-solid fa-layer-group text-[8px]" />
              {project.total_chapters} caps.
            </span>
          )}
          <span className="text-[10px] text-dim ml-auto">{styleName}</span>
        </div>
      </div>
    </Link>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <p className="text-dim text-[10px]">{label}</p>
      <p className="font-semibold">{value}</p>
    </div>
  );
}