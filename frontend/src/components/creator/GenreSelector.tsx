import { GENRES } from '@/data/genres';
import { Chip } from '../ui/Chip';

interface GenreSelectorProps {
  selected: string[];
  onToggle: (id: string) => void;
}

export function GenreSelector({ selected, onToggle }: GenreSelectorProps) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {GENRES.map((g) => (
        <Chip key={g.id} selected={selected.includes(g.id)} onClick={() => onToggle(g.id)}>
          <i className={`fa-solid ${g.icon} text-[9px] mr-1`} />
          {g.name}
        </Chip>
      ))}
    </div>
  );
}