import type { GenerationRequest } from '@/types/generation';

interface ModeSelectorProps {
  mode: GenerationRequest['mode'];
  onChange: (mode: GenerationRequest['mode']) => void;
}

const MODES: { value: GenerationRequest['mode']; label: string; icon: string }[] = [
  { value: 'auto', label: 'Auto', icon: 'fa-wand-magic-sparkles' },
  { value: 'prompt', label: 'Prompt', icon: 'fa-lightbulb' },
  { value: 'manuscript', label: 'Manuscrito', icon: 'fa-file-lines' },
  { value: 'expand', label: 'Expandir', icon: 'fa-expand' },
  { value: 'continue', label: 'Continuar', icon: 'fa-forward' },
];

export function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {MODES.map((m) => (
        <button
          key={m.value}
          type="button"
          onClick={() => onChange(m.value)}
          className={`
            py-2 px-3 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer border
            ${mode === m.value
              ? 'bg-amber/15 border-amber text-amber'
              : 'border-bdr text-muted hover:border-bdr-light hover:text-txt'
            }
          `}
        >
          <i className={`fa-solid ${m.icon} text-[10px] mr-1.5`} />
          {m.label}
        </button>
      ))}
    </div>
  );
}