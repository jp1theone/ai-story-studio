export interface AgentDef {
  id: string;
  name: string;
  icon: string;
  description: string;
}

export type AgentState = 'waiting' | 'active' | 'completed';