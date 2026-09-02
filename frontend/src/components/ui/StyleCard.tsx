import type { StyleDef } from '@/data/styles';

interface StyleCardProps {
  style: StyleDef;
  selected: boolean;
  onClick: () => void;
}

export function StyleCard({ style, selected, onClick }: StyleCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        p-3 rounded-xl border-2 text-center transition-all duration-250 cursor-pointer
        ${selected
          ? 'border-amber bg-amber/8 shadow-lg shadow-amber/10'
          : 'border-bdr hover:border-bdr-light hover:bg-amber/4'
        }
      `}
    >
      <div className="text-xl mb-1">{style.emoji}</div>
      <p className="text-xs font-semibold">{style.name}</p>
      <p className="text-[10px] text-dim mt-0.5">{style.description}</p>
    </button>
  );
}