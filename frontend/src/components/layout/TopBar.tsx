import { useLocation } from 'react-router-dom';

const PAGE_TITLES: Record<string, string> = {
  '/': 'Dashboard',
  '/creator': 'Creador de Historias',
  '/projects': 'Proyectos',
  '/settings': 'Configuración',
};

export function TopBar() {
  const location = useLocation();
  const title = PAGE_TITLES[location.pathname] || 'AI Story Studio';

  return (
    <header className="h-14 border-b border-bdr flex items-center justify-between px-6 bg-main/40 backdrop-blur-sm flex-shrink-0">
      <h2 className="text-sm font-semibold font-heading">{title}</h2>
      <div className="flex items-center gap-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Buscar proyectos..."
            className="bg-card border border-bdr rounded-lg px-3 py-1.5 text-xs text-txt placeholder-dim w-56 focus:outline-none focus:border-amber/50 transition-colors"
          />
          <i className="fa-solid fa-search absolute right-3 top-1/2 -translate-y-1/2 text-dim text-[10px]" />
        </div>
      </div>
    </header>
  );
}