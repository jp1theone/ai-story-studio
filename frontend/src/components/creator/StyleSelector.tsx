import { STYLES } from '@/data/styles';
import { StyleCard } from '../ui/StyleCard';

interface StyleSelectorProps {
  selected: string;
  onChange: (id: string) => void;
}

export function StyleSelector({ selected, onChange }: StyleSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {STYLES.map((s) => (
        <StyleCard
          key={s.id}
          style={s}
          selected={selected === s.id}
          onClick={() => onChange(s.id)}
        />
      ))}
    </div>
  );
}