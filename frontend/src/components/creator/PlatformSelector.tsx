import { useGenerationStore } from '@/stores/generationStore';
import { PlatformCheck } from '../ui/PlatformCheck';

export const PLATFORMS = [
  { id: 'youtube', name: 'YouTube', icon: 'fa-youtube', color: '#FF0000', meta: '1920x1080 · 24fps' },
  { id: 'tiktok', name: 'TikTok', icon: 'fa-tiktok', color: '#00F2EA', meta: '1080x1920 · 30fps' },
  { id: 'facebook', name: 'Facebook', icon: 'fa-facebook', color: '#1877F2', meta: '1080x1920 · 30fps' },
  { id: 'shorts', name: 'Shorts', icon: 'fa-mobile-screen', color: '#FF0000', meta: '1080x1920 · 30fps' },
];

export function PlatformSelector() {
  const platforms = useGenerationStore((s) => s.request.platforms);
  const setRequest = useGenerationStore((s) => s.setRequest);

  const toggle = (id: string) => {
    const next = platforms.includes(id)
      ? platforms.filter((p) => p !== id)
      : [...platforms, id];
    setRequest({ platforms: next });
  };

  return (
    <div className="space-y-2">
      {PLATFORMS.map((p) => (
        <PlatformCheck
          key={p.id}
          platformId={p.id}
          checked={platforms.includes(p.id)}
          onToggle={() => toggle(p.id)}
          icon={p.icon}
          iconColor={p.color}
          name={p.name}
          meta={p.meta}
        />
      ))}
    </div>
  );
}