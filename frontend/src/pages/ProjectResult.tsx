import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useProjectStore } from '@/stores/projectStore';
import { useGenerationStore } from '@/stores/generationStore';
import { StoryTab } from '@/components/project/StoryTab';
import { ScenesTab } from '@/components/project/ScenesTab';
import { CharactersTab } from '@/components/project/CharactersTab';
import { ExportTab } from '@/components/project/ExportTab';
import { ChaptersTab } from '@/components/project/ChaptersTab';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';

type TabId = 'story' | 'chapters' | 'scenes' | 'characters' | 'export';

interface ProjectResultProps {
  projectId: number;
  onNewStory: () => void;
}

export function ProjectResult({ projectId, onNewStory }: ProjectResultProps) {
  const fetchProject = useProjectStore((s) => s.fetchProject);
  const project = useProjectStore((s) => s.current);
  const startShorts = useGenerationStore((s) => s.startShorts);

  const isMultiChapter = (project?.total_chapters ?? 1) > 1;
  const [activeTab, setActiveTab] = useState<TabId>(isMultiChapter ? 'chapters' : 'story');

  useQuery({
    queryKey: ['project', projectId],
    queryFn: () => fetchProject(projectId),
  });

  if (!project) {
    return (
      <div className="p-6 text-center text-muted animate-fade-in">
        <i className="fa-solid fa-spinner animate-spin text-2xl mb-4 block text-amber" />
        <p className="text-sm">Cargando proyecto...</p>
      </div>
    );
  }

  const sceneCount = project.scenes.length;
  const totalDurationMin = Math.round(
    project.scenes.reduce((acc, s) => acc + (s.duration_seconds || 0), 0) / 60
  );

  // Tabs dinámicas según si tiene capítulos
  const TABS: { id: TabId; label: string; icon: string; badge?: string }[] = [
    ...(isMultiChapter
      ? [{ id: 'chapters' as TabId, label: 'Capítulos', icon: 'fa-layer-group', badge: String(project.total_chapters) }]
      : []),
    { id: 'story', label: 'Historia', icon: 'fa-book' },
    { id: 'scenes', label: 'Escenas', icon: 'fa-film', badge: String(sceneCount) },
    { id: 'characters', label: 'Personajes', icon: 'fa-users', badge: String(project.characters.length) },
    { id: 'export', label: 'Exportar', icon: 'fa-share-from-square' },
  ];

  return (
    <div className="p-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-2 flex-wrap">
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald/10 text-emerald border border-emerald/20 font-semibold">
              ✅ COMPLETADO
            </span>
            {isMultiChapter && (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber/10 text-amber border border-amber/20 font-semibold flex items-center gap-1">
                <i className="fa-solid fa-layer-group text-[9px]" />
                {project.total_chapters} CAPÍTULOS
              </span>
            )}
            <span className="text-xs text-dim">{project.created_at?.split('T')[0]}</span>
          </div>
          <h2 className="text-2xl font-bold font-heading leading-tight">{project.title}</h2>
          <p className="text-sm text-muted mt-1 flex items-center gap-2 flex-wrap">
            <span>{project.genres.join(' + ')}</span>
            <span className="text-dim">·</span>
            <span>{project.style}</span>
            <span className="text-dim">·</span>
            <span className="flex items-center gap-1">
              <i className="fa-regular fa-clock text-[10px]" />
              {totalDurationMin > 0 ? `${totalDurationMin} min reales` : `${project.duration_minutes} min objetivo`}
            </span>
            <span className="text-dim">·</span>
            <span>{sceneCount} escenas</span>
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <Button variant="secondary" size="sm" onClick={onNewStory}>
            <i className="fa-solid fa-plus mr-1" />
            Nueva Historia
          </Button>
          <Button
            size="sm"
            onClick={() => {
              startShorts(projectId);
              toast('Iniciando generación de cortos...', 'info');
            }}
          >
            <i className="fa-solid fa-mobile-screen mr-1" />
            Generar Cortos
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-bdr mb-6 gap-1 overflow-x-auto">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex-shrink-0 flex items-center gap-1.5 px-4 py-2.5 text-xs font-semibold cursor-pointer transition-all duration-200 border-b-2
              ${activeTab === tab.id
                ? 'text-amber border-amber'
                : 'text-muted border-transparent hover:text-txt'
              }
            `}
          >
            <i className={`fa-solid ${tab.icon} text-[10px]`} />
            {tab.label}
            {tab.badge && (
              <span className={`
                text-[9px] px-1.5 py-0.5 rounded-full font-semibold
                ${activeTab === tab.id ? 'bg-amber/15 text-amber' : 'bg-deep text-dim'}
              `}>
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'chapters' && <ChaptersTab project={project} />}
        {activeTab === 'story' && <StoryTab project={project} />}
        {activeTab === 'scenes' && <ScenesTab project={project} />}
        {activeTab === 'characters' && <CharactersTab project={project} />}
        {activeTab === 'export' && <ExportTab project={project} />}
      </div>
    </div>
  );
}