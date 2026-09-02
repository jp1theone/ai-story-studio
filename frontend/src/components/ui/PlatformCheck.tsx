
interface PlatformCheckProps {
  platformId: string;
  checked: boolean;
  onToggle: () => void;
  icon: string;
  iconColor: string;
  name: string;
  meta: string;
}

export function PlatformCheck({ checked, onToggle, icon, iconColor, name, meta }: PlatformCheckProps) {
  return (
    <div
      className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-card-hover transition-colors cursor-pointer"
      onClick={onToggle}
      role="checkbox"
      aria-checked={checked}
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); onToggle(); } }}
    >
      <div
        className={`
          w-[18px] h-[18px] rounded flex-shrink-0 flex items-center justify-center transition-all
          border-2 ${checked ? 'bg-amber border-amber' : 'border-bdr-light'}
        `}
      >
        {checked && <i className="fa-solid fa-check text-deep text-[10px]" />}
      </div>
      <i className={`fa-brands ${icon} text-sm`} style={{ color: iconColor }} />
      <span className="text-xs font-medium flex-1">{name}</span>
      <span className="text-[10px] text-dim">{meta}</span>
    </div>
  );
}