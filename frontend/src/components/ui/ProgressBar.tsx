interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  size?: 'sm' | 'md';
}

export function ProgressBar({ value, max = 100, className = '', size = 'md' }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const h = size === 'sm' ? 'h-1' : 'h-2';

  return (
    <div className={`bg-bdr rounded-full overflow-hidden ${h} ${className}`}>
      <div
        className="h-full bg-gradient-to-r from-amber to-amber-hover rounded-full transition-all duration-300"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}