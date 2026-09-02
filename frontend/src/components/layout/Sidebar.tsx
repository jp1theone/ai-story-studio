import { NavLink } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: 'fa-gauge-high' },
  { to: '/creator', label: 'Creador de Historias', icon: 'fa-film' },
  { to: '/projects', label: 'Proyectos', icon: 'fa-folder-open' },
  { to: '/settings', label: 'Configuración', icon: 'fa-gear' },
];

const EXTERNAL_LINKS = [
  { href: 'http://localhost:8000/docs', label: 'API Docs', icon: 'fa-book' },
];

export function Sidebar() {
  return (
    <aside className="w-[260px] h-screen flex flex-col border-r border-bdr bg-main/80 backdrop-blur-sm flex-shrink-0">
      {/* Logo */}
      <div className="p-5 border-b border-bdr">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber to-amber-hover flex items-center justify-center">
            <i className="fa-solid fa-clapperboard text-deep text-lg" />
          </div>
          <div>
            <h1 className="text-base font-bold font-heading tracking-tight">AI Story Studio</h1>
            <p className="text-[10px] text-dim font-medium tracking-widest uppercase">Producción Local</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 flex flex-col gap-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-amber/12 text-amber'
                  : 'text-muted hover:bg-amber/8 hover:text-txt'
              }`
            }
          >
            <i className={`fa-solid ${item.icon} w-5 text-center text-sm`} />
            <span>{item.label}</span>
          </NavLink>
        ))}

        <div className="mt-6 mb-2 px-4">
          <p className="text-[10px] font-semibold text-dim tracking-widest uppercase">Enlaces Externos</p>
        </div>
        {EXTERNAL_LINKS.map((link) => (
          <a
            key={link.href}
            href={link.href}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-muted hover:bg-amber/8 hover:text-txt transition-all duration-200"
          >
            <i className={`fa-solid ${link.icon} w-5 text-center text-sm`} />
            <span className="flex-1">{link.label}</span>
            <i className="fa-solid fa-arrow-up-right-from-square text-[10px]" />
          </a>
        ))}
      </nav>

      {/* System Status */}
      <div className="p-4 border-t border-bdr">
        <p className="text-[10px] font-semibold text-dim tracking-widest uppercase mb-3">Sistema</p>
        <div className="space-y-2 text-xs">
          <SysRow label="GPU" value="RTX 5050 8GB" valueClass="text-emerald" icon="fa-microchip" />
          <SysRow label="VRAM" value="2.1 / 8.0 GB" valueClass="text-amber" icon="fa-memory" />
          <SysRow label="RAM" value="14.2 / 32 GB" valueClass="text-txt" icon="fa-database" />
          <SysRow label="Modelo" value="Bajo demanda" valueClass="text-emerald" icon="fa-brain" />
          <SysRow label="Imágenes" value="Respaldo local" valueClass="text-emerald" icon="fa-image" />
        </div>
      </div>
    </aside>
  );
}

function SysRow({ label, value, valueClass, icon }: { label: string; value: string; valueClass: string; icon: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-muted flex items-center gap-2">
        <i className={`fa-solid ${icon} text-[10px]`} />
        {label}
      </span>
      <span className={`${valueClass} font-medium`}>{value}</span>
    </div>
  );
}
