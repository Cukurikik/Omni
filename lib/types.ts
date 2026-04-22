// ==========================================
// ⚡ OMNI TOOLS - TypeScript Types
// ==========================================

export type ToolCategory = 
  | 'VIDEO' 
  | 'AUDIO' 
  | 'IMAGE' 
  | 'PDF' 
  | 'CONVERTER' 
  | 'AI' 
  | 'LLM' 
  | 'SYSTEM';

export interface OmniTool {
  id: string;
  name: string;
  description: string;
  category: ToolCategory;
  emoji: string;
  endpoint: string;
  method: 'POST' | 'GET';
  accepts: string;
  delegateTo: 'C++' | 'Golang' | 'Python' | 'JavaScript' | 'C#';
  icon?: string;
}

export interface ToolExecutionRequest {
  tool_id: string;
  parameters: Record<string, any>;
  files?: File[];
}

export interface ToolExecutionResponse {
  success: boolean;
  result?: any;
  error?: string;
  processing_time_ms?: number;
}

export interface CategoryInfo {
  id: ToolCategory | 'ALL';
  label: string;
  emoji: string;
}