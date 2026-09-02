import { AGENTS } from '@/data/agents';
import type { AgentState } from '@/types/agent';

interface AgentPipelineProps {
  agentStates: AgentState[];
}

export function AgentPipeline({ agentStates }: AgentPipelineProps) {
  return (
    <div className="glass p-4 mb-6 overflow-x-auto">
      <div className="flex items-center gap-1 min-w-max">
        {AGENTS.map((agent, i) => {
          const state = agentStates[i] ?? 'waiting';
          return (
            <div key={agent.id} className="flex items-center">
              {i > 0 && <Connector state={state} />}
              <div
                className={`
                  px-3 py-2.5 rounded-xl border-1.5 flex-shrink-0 text-center min-w-[100px] transition-all duration-400
                  ${state === 'active'
                    ? 'border-amber bg-amber/8 animate-pulse-glow'
                    : state === 'completed'
                      ? 'border-emerald bg-emerald/6'
                      : 'border-bdr bg-main opacity-40'
                  }
                `}
                style={{ borderWidth: '1.5px' }}
              >
                <div className="mb-1">
                  {state === 'completed' ? (
                    <i className="fa-solid fa-circle-check text-emerald text-xs" />
                  ) : state === 'active' ? (
                    <i className={`fa-solid ${agent.icon} text-amber text-xs animate-pulse`} />
                  ) : (
                    <i className={`fa-solid ${agent.icon} text-dim text-xs`} />
                  )}
                </div>
                <p
                  className={`text-[10px] font-semibold whitespace-nowrap ${
                    state === 'active'
                      ? 'text-amber'
                      : state === 'completed'
                        ? 'text-emerald'
                        : 'text-dim'
                  }`}
                >
                  {agent.name}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Connector({ state }: { state: AgentState }) {
  return (
    <div
      className={`w-[30px] h-[2px] flex-shrink-0 transition-all duration-400 ${
        state === 'completed'
          ? 'bg-emerald'
          : state === 'active'
            ? 'bg-gradient-to-r from-emerald to-amber'
            : 'bg-bdr'
      }`}
    />
  );
}