import type { Project, PlatformSeo } from '@/types/project';
import { Button } from '../ui/Button';
import { toast } from '../ui/Toast';
import { api } from '@/services/api';

interface ExportTabProps {
  project: Project;
}

const PLATFORM_CONFIG = [
  { id: 'youtube', name: 'YouTube', icon: 'fa-youtube', color: '#FF0000', res: '1920x1080', fps: 24 },
  { id: 'tiktok', name: 'TikTok', icon: 'fa-tiktok', color: '#00F2EA', res: '1080x1920', fps: 30 },
  { id: 'facebook', name: 'Facebook', icon: 'fa-facebook', color: '#1877F2', res: '1080x1920', fps: 30 },
  { id: 'shorts', name: 'Shorts', icon: 'fa-mobile-screen', color: '#FF0000', res: '1080x1920', fps: 30 },
];

export function ExportTab({ project }: ExportTabProps) {
  const seo = project.seo_data;

  return (
    <div className="space-y-4">
      {PLATFORM_CONFIG.map((pl) => {
        const plSeo = (seo?.[pl.id as keyof typeof seo] ?? seo?.youtube) as PlatformSeo | undefined;
        if (!plSeo) return null;

        return (
          <div key={pl.id} className="glass p-5">
            <div className="flex items-center gap-3 mb-4">
              <i className={`fa-brands ${pl.icon} text-xl`} style={{ color: pl.color }} />
              <div>
                <h4 className="text-sm font-semibold font-heading">{pl.name}</h4>
                <p className="text-[10px] text-dim">
                  {pl.res} · {pl.fps}fps · MP4 H.264
                </p>
              </div>
              <Button
                variant="primary"
                size="sm"
                className="ml-auto"
                onClick={() => {
                  window.location.assign(api.projects.downloadUrl(project.id, { platform: pl.id }));
                  toast(`Preparando la descarga de ${pl.name}...`, 'success');
                }}
              >
                <i className="fa-solid fa-download mr-1" />
                Descargar
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-deep rounded-lg p-3">
                <p className="text-[10px] text-dim mb-1 font-semibold">Título</p>
                <p className="text-xs">{plSeo.title}</p>
              </div>
              <div className="bg-deep rounded-lg p-3">
                <p className="text-[10px] text-dim mb-1 font-semibold">Descripción</p>
                <p className="text-xs text-muted line-clamp-3">{plSeo.description}</p>
              </div>
            </div>
            <div className="mt-3 bg-deep rounded-lg p-3">
              <p className="text-[10px] text-dim mb-2 font-semibold">Hashtags</p>
              <div className="flex flex-wrap gap-1.5">
                {plSeo.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-[10px] px-2 py-0.5 rounded-full bg-card border border-bdr text-amber"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
