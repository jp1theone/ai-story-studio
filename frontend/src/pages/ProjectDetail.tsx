import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useProjectStore } from '@/stores/projectStore';
import { StoryTab } from '@/components/project/StoryTab';
import { ScenesTab } from '@/components/project/ScenesTab';
import { CharactersTab } from '@/components/project/CharactersTab';
import { ExportTab } from '@/components/project/ExportTab';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';
import { useState } from 'react';

const TABS = ['story', 'scenes', 'characters', 'export'] as const;
type TabId = (typeof TABS)[number];

export function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabId>('story');
  const fetchProject = useProjectStore((s) => s.fetchProject);
  const project = useProjectStore((s) => s.current);
  const deleteProject = useProjectStore((s) => s.deleteProject);
  const loading = useProjectStore((s) => s.loading);

  useQuery({
    queryKey: ['project', id],
    queryFn: () => fetchProject(Number(id)),
    enabled: !!id,
  });

  if (loading) {
    return (
      <div className="p-6 text-center text-muted animate-fade-in">
        <i className="fa-solid fa-spinner animate-spin text-2xl mb-4 block" />
        Cargando...
      </div>
    );
  }

  if (!project) {
    return (
      <div className="p-6 text-center text-muted animate-fade-in">
        <p className="text-sm mb-4">Proyecto no encontrado.</p>
        <Button variant="secondary" onClick={() => navigate('/projects')}>
          Volver a Proyectos
        </Button>
      </div>
    );
  }

  if (project.status === 'fallido') {
    return (
      <div className="p-6 animate-fade-in">
        <div className="max-w-2xl rounded-xl border border-rose/30 bg-rose/10 p-6">
          <i className="fa-solid fa-circle-exclamation text-2xl text-rose mb-3 block" />
          <h2 className="text-lg font-bold font-heading">La producción no se completó</h2>
          <p className="mt-2 text-sm text-muted">{project.synopsis || 'No se generó un video final.'}</p>
          <Button className="mt-5" onClick={() => navigate('/creator')}>Volver al creador</Button>
        </div>
      </div>
    );
  }

  const handleDelete = async () => {
    await deleteProject(project.id);
    toast('Proyecto eliminado', 'error');
    navigate('/projects');
  };

  return (
    <div className="p-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                project.status === 'completado'
                  ? 'bg-emerald/10 text-emerald'
                  : 'bg-amber/10 text-amber'
              }`}
            >
              {project.status}
            </span>
            <span className="text-xs text-dim">{project.created_at}</span>
          </div>
          <h2 className="text-2xl font-bold font-heading">{project.title}</h2>
          <p className="text-sm text-muted mt-1">
            {project.genres.join(' + ')} · {project.style} · {project.duration_minutes} min
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="danger" onClick={handleDelete}>
            <i className="fa-solid fa-trash mr-1" />
            Eliminar
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-bdr mb-6">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`
              px-5 py-2.5 text-xs font-semibold cursor-pointer transition-all duration-200 border-b-2 capitalize
              ${activeTab === tab
                ? 'text-amber border-amber'
                : 'text-muted border-transparent hover:text-txt'
              }
            `}
          >
            {tab}
            {tab === 'scenes' && (
              <span className="text-dim font-normal ml-1">({project.scenes.length})</span>
            )}
          </button>
        ))}
      </div>

      {activeTab === 'story' && <StoryTab project={project} />}
      {activeTab === 'scenes' && <ScenesTab project={project} />}
      {activeTab === 'characters' && <CharactersTab project={project} />}
      {activeTab === 'export' && <ExportTab project={project} />}
    </div>
  );
}
