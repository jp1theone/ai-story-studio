import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';
import { api } from '@/services/api';

const MODELS = [
  { name: 'Qwen2.5-7B-Instruct (GGUF Q4)', desc: 'LLM principal — Generación de historias', size: '~4.2 GB', installed: true },
  { name: 'Animagine XL 3.1', desc: 'Modelo visual activo — Anime cinematográfico HD', size: '~6.5 GB', installed: true },
  { name: 'Pony Diffusion V6 XL + Juggernaut XL', desc: 'Modelos visuales alternativos — ComfyUI', size: '~12.4 GB', installed: true },
  { name: 'F5-TTS', desc: 'Síntesis de voz — Múltiples voces', size: '~1.8 GB', installed: true },
];

const PATHS = [
  { label: 'Modelos LLM', path: 'models/llm/' },
  { label: 'Modelos Visuales', path: 'comfyui/ComfyUI/models/checkpoints/' },
  { label: 'Modelos TTS', path: 'models/tts/' },
  { label: 'Workflows ComfyUI', path: 'comfyui/workflows/' },
  { label: 'Salida de Videos', path: 'output/' },
];

type ServiceStatus = { name: string; url: string; active: boolean };

export function Settings() {
  const [gpuLayers, setGpuLayers] = useState(28);
  const [resolution, setResolution] = useState('896x512');
  const [steps, setSteps] = useState(35);
  const [contentFolder, setContentFolder] = useState('');
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'FastAPI Backend', url: 'localhost:8000', active: false },
    { name: 'ComfyUI (Motor Visual)', url: 'localhost:8188', active: false },
  ]);

  useEffect(() => {
    api.settings.outputFolder()
      .then(({ path }) => setContentFolder(path))
      .catch(() => toast('No se pudo leer la carpeta de entregas', 'error'));

    // Verificar estado real de los servicios
    const checkServices = async () => {
      const results: ServiceStatus[] = [];

      // Backend
      try {
        const r = await fetch('http://localhost:8000/api/health', { signal: AbortSignal.timeout(3000) });
        results.push({ name: 'FastAPI Backend', url: 'localhost:8000', active: r.ok });
      } catch {
        results.push({ name: 'FastAPI Backend', url: 'localhost:8000', active: false });
      }

      // ComfyUI
      try {
        const r = await fetch('http://127.0.0.1:8188/system_stats', { signal: AbortSignal.timeout(3000) });
        results.push({ name: 'ComfyUI (Motor Visual)', url: 'localhost:8188', active: r.ok });
      } catch {
        results.push({ name: 'ComfyUI (Motor Visual)', url: 'localhost:8188', active: false });
      }

      setServices(results);
    };

    checkServices();
    const interval = setInterval(checkServices, 15000);
    return () => clearInterval(interval);
  }, []);

  const saveContentFolder = async () => {
    try {
      const { path } = await api.settings.setOutputFolder(contentFolder);
      setContentFolder(path);
      toast('Carpeta de entregas actualizada', 'success');
    } catch (error) {
      toast((error as Error).message, 'error');
    }
  };

  return (
    <div className="p-6 animate-fade-in max-w-3xl">
      <h3 className="text-lg font-bold font-heading mb-6">Configuración del Sistema</h3>

      {/* Modelos */}
      <Section title="Modelos IA" icon="fa-brain">
        <div className="space-y-3">
          {MODELS.map((m) => (
            <div key={m.name} className="flex items-center justify-between p-3 rounded-lg bg-deep border border-bdr">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-amber/10 flex items-center justify-center">
                  <i className="fa-solid fa-brain text-amber text-xs" />
                </div>
                <div>
                  <p className="text-xs font-semibold">{m.name}</p>
                  <p className="text-[10px] text-dim">{m.desc}</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-[10px] font-medium ${m.installed ? 'text-emerald' : 'text-dim'}`}>
                  <i className={`fa-solid ${m.installed ? 'fa-circle-check' : 'fa-circle-xmark'} mr-1`} />
                  {m.installed ? 'Instalado' : 'No instalado'}
                </p>
                <p className="text-[10px] text-dim">{m.size}</p>
              </div>
            </div>
          ))}
        </div>
        <Button
          variant="secondary"
          size="sm"
          className="mt-4"
          onClick={() => toast('Ejecuta: python scripts/download_models.py --tier full', 'info')}
        >
          <i className="fa-solid fa-download mr-1" />
          Gestionar Modelos
        </Button>
      </Section>

      {/* Rendimiento */}
      <Section title="Rendimiento" icon="fa-gauge-high">
        <div className="space-y-5">
          <SliderRow
            label="Capas LLM en GPU"
            value={gpuLayers}
            suffix="/ 32"
            onChange={setGpuLayers}
            min={10}
            max={32}
            hint="Reduce si hay errores de CUDA out of memory"
          />
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-xs text-muted">Resolución de imágenes</label>
              <span className="text-xs font-semibold text-amber">{resolution}</span>
            </div>
            <div className="flex gap-2">
              {['768x768', '896x512', '1024x1024'].map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setResolution(r)}
                  className={`
                    px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer border
                    ${resolution === r
                      ? 'bg-amber/15 border-amber text-amber'
                      : 'border-bdr text-muted hover:border-bdr-light'
                    }
                  `}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>
          <SliderRow
            label="Steps de generación de imagen"
            value={steps}
            onChange={setSteps}
            min={15}
            max={50}
          />
        </div>
      </Section>

      {/* Rutas */}
      <Section title="Rutas del Sistema" icon="fa-folder">
        <div className="mb-4 rounded-lg border border-amber/20 bg-amber/5 p-3">
          <p className="text-xs font-semibold text-amber mb-1">Carpeta de entregas finales</p>
          <p className="text-[10px] text-muted mb-2">
            Los videos se guardan en <code>Videos</code> y los cortos en <code>Shorts</code> dentro de esta carpeta.
          </p>
          <div className="flex gap-2">
            <input
              value={contentFolder}
              onChange={(event) => setContentFolder(event.target.value)}
              placeholder="C:\\Users\\TuUsuario\\Desktop\\Contenido"
              className="min-w-0 flex-1 rounded-lg border border-bdr bg-deep px-3 py-2 text-xs text-txt outline-none focus:border-amber"
            />
            <Button size="sm" onClick={saveContentFolder}>Guardar</Button>
          </div>
        </div>
        <div className="space-y-2">
          {PATHS.map((r) => (
            <div key={r.label} className="flex items-center gap-3 p-2 rounded-lg bg-deep border border-bdr">
              <span className="text-muted w-32 flex-shrink-0 text-xs">{r.label}</span>
              <code className="text-amber text-[11px] flex-1 truncate">{r.path}</code>
              <button
                className="text-dim hover:text-amber transition-colors"
                onClick={() => { navigator.clipboard.writeText(r.path); toast(`Ruta copiada: ${r.path}`, 'success'); }}
              >
                <i className="fa-solid fa-copy text-[10px]" />
              </button>
            </div>
          ))}
        </div>
      </Section>

      {/* Servicios */}
      <Section title="Estado de Servicios" icon="fa-server">
        <div className="space-y-2">
          {services.map((s) => (
            <div key={s.name} className="flex items-center justify-between p-2.5 rounded-lg bg-deep border border-bdr">
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full transition-colors ${s.active ? 'bg-emerald animate-pulse' : 'bg-rose'}`} />
                <span className="text-xs font-medium">{s.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <code className="text-[10px] text-dim">{s.url}</code>
                <span className={`text-[10px] font-medium ${s.active ? 'text-emerald' : 'text-rose'}`}>
                  {s.active ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-dim mt-3">
          <i className="fa-solid fa-circle-info mr-1" />
          Los servicios se verifican automáticamente cada 15 segundos. ComfyUI se inicia solo cuando generas una historia.
        </p>
      </Section>
    </div>
  );
}

function Section({ title, icon, children }: { title: string; icon: string; children: React.ReactNode }) {
  return (
    <div className="glass p-5 mb-4">
      <h4 className="text-sm font-semibold font-heading mb-4 flex items-center gap-2">
        <i className={`fa-solid ${icon} text-amber text-xs`} />
        {title}
      </h4>
      {children}
    </div>
  );
}

function SliderRow({
  label,
  value,
  suffix,
  onChange,
  min,
  max,
  hint,
}: {
  label: string;
  value: number;
  suffix?: string;
  onChange: (v: number) => void;
  min: number;
  max: number;
  hint?: string;
}) {
  return (
    <div>
      <div className="flex justify-between mb-2">
        <label className="text-xs text-muted">{label}</label>
        <span className="text-xs font-semibold text-amber">
          {value}{suffix ? ` ${suffix}` : ''}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full"
      />
      {hint && <span className="text-[10px] text-dim block mt-1">{hint}</span>}
    </div>
  );
}
