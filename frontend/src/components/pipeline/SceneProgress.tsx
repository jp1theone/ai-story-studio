import type { Scene } from '@/types/project';

interface SceneProgressProps {
  scenes: Scene[];
  imagesGenerated: number;
}

export function SceneProgress({ scenes, imagesGenerated }: SceneProgressProps) {
  if (scenes.length === 0) {
    return (
      <div className="glass p-4 flex flex-col overflow-hidden">
        <h4 className="text-xs font-semibold font-heading mb-3">Escenas</h4>
        <p className="text-xs text-dim text-center mt-8">
          Las escenas aparecerán cuando el Storyboard las genere...
        </p>
      </div>
    );
  }

  return (
    <div className="glass p-4 flex flex-col overflow-hidden">
      <h4 className="text-xs font-semibold font-heading mb-3">
        Escenas{' '}
        <span className="text-dim font-normal">
          ({imagesGenerated}/{scenes.length})
        </span>
      </h4>
      <div className="flex-1 overflow-y-auto space-y-2">
        {scenes.map((scene) => (
          <div
            key={scene.id}
            className="flex items-center gap-2 p-2 rounded-lg bg-deep border border-bdr"
          >
            <div
              className={`w-12 h-8 rounded overflow-hidden flex-shrink-0 ${
                scene.image_path ? '' : 'animate-shimmer'
              }`}
            >
              {scene.image_path && (
                <img
                  src={`/api/projects/${scene.id}/image`}
                  className="w-full h-full object-cover"
                  alt=""
                  loading="lazy"
                />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[10px] font-medium truncate">
                Escena {scene.scene_number}: {scene.title}
              </p>
              <div className="flex items-center gap-2 mt-0.5">
                {scene.image_path ? (
                  <span className="text-[9px] text-emerald">
                    <i className="fa-solid fa-image" />
                  </span>
                ) : (
                  <span className="text-[9px] text-dim">
                    <i className="fa-solid fa-hourglass-half" />
                  </span>
                )}
                {scene.audio_path ? (
                  <span className="text-[9px] text-emerald">
                    <i className="fa-solid fa-microphone" />
                  </span>
                ) : (
                  <span className="text-[9px] text-dim">
                    <i className="fa-solid fa-hourglass-half" />
                  </span>
                )}
                <span className="text-[9px] text-dim ml-auto">
                  {formatTime(scene.duration_seconds)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}