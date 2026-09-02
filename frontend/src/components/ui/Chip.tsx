import type { ReactNode, ButtonHTMLAttributes } from 'react';

interface ChipProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean;
  children: ReactNode;
}

export function Chip({ selected = false, children, className = '', ...props }: ChipProps) {
  return (
    <button
      className={`
        px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200
        border cursor-pointer
        ${selected
          ? 'bg-amber/15 border-amber text-amber'
          : 'border-bdr text-muted hover:border-bdr-light hover:text-txt'
        }
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
}