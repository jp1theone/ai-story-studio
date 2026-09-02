import { useQuery } from '@tanstack/react-query';
import { useProjectStore } from '@/stores/projectStore';
import { ProjectCard } from '@/components/project/ProjectCard';
import { Button } from '@/components/ui/Button';
import { Link } from 'react-router-dom';

export function Projects() {
  const fetchList = useProjectStore((s) => s.fetchList);
  const list = useProjectStore((s) => s.list);
  const loading = useProjectStore((s) => s.loading);

  useQuery({ queryKey: ['projects'], queryFn: fetchList });

  return (
    <div className="p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold font-heading">Todos los Proyectos</h3>
          <p className="text-xs text-muted mt-0.5">{list.length} proyectos en total</p>
        </div>
        <Link to="/creator">
          <Button>
            <i className="fa-solid fa-plus mr-1" />
            Nuevo Proyecto
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="text-center py-20">
          <i className="fa-solid fa-spinner animate-spin text-2xl text-dim mb-4 block" />
          <p className="text-sm text-muted">Cargando proyectos...</p>
        </div>
      ) : list.length === 0 ? (
        <div className="text-center py-20">
          <div className="w-20 h-20 rounded-2xl bg-card border border-bdr flex items-center justify-center mx-auto mb-4">
            <i className="fa-solid fa-folder-open text-3xl text-dim" />
          </div>
          <p className="text-sm text-muted mb-1">No hay proyectos aún</p>
          <p className="text-xs text-dim mb-6">Crea tu primera historia para verla aquí.</p>
          <Link to="/creator">
            <Button>
              <i className="fa-solid fa-plus mr-1" />
              Crear Primera Historia
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {list.map((proj) => (
            <ProjectCard key={proj.id} project={proj} />
          ))}
        </div>
      )}
    </div>
  );
}