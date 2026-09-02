import type { AgentLogEntry } from '@/types/generation';
import { AGENTS } from '@/data/agents';

interface AgentLogProps {
  log: AgentLogEntry[];
  currentAgentIndex: number;
}

export function AgentLog({ log, currentAgentIndex }: AgentLogProps) {
  const currentAgent =
    currentAgentIndex >= 0 && currentAgentIndex < AGENTS.length
      ? AGENTS[currentAgentIndex]
      : null;

  return (
    <div className="glass p-4 flex flex-col overflow-hidden">
      <div className="flex items-center gap-2 mb-3">
        <div
          className={`w-2 h-2 rounded-full ${
            currentAgent ? 'bg-amber animate-pulse' : 'bg-dim'
          }`}
        />
        <h4 className="text-xs font-semibold font-heading">
          {currentAgent
            ? `${currentAgent.name} — ${currentAgent.description}`
            : 'Iniciando...'}
        </h4>
      </div>
      <div className="flex-1 overflow-y-auto text-xs text-muted space-y-1.5 font-mono leading-relaxed">
        {log.map((entry, i) => (
          <div
            key={i}
            className={`animate-slide-in ${
              entry.log_type === 'success'
                ? 'text-emerald'
                : entry.log_type === 'error'
                  ? 'text-rose'
                  : entry.log_type === 'warning'
                    ? 'text-amber'
                    : ''
            }`}
          >
            {entry.message}
          </div>
        ))}
      </div>
    </div>
  );
}