import { LucideIcon, Video, Mic, Image, FileText, ArrowRightLeft, Sparkles, Box, Bot } from 'lucide-react';

export type OmniCategory = 'VIDEO' | 'AUDIO' | 'IMAGE' | 'PDF' | 'CONVERTER' | 'AI' | 'LLM' | 'SYSTEM';

export interface OmniToolUI {
  id: string;
  name: string;
  description: string;
  category: OmniCategory;
  accepts: string;
  icon: LucideIcon;
  requiresInput?: { key: string; label: string; type: 'text' | 'password' }[];
  endpoint?: string;
  extraInputs?: any[];
}

export const OMNI_TOOLS_UI: OmniToolUI[] = [
  // @omni-gen-start
  { 
    id: 'demo_tool', 
    name: 'Alat Demo', 
    description: 'Otomatis dibuat oleh sistem.', 
    category: 'SYSTEM', 
    accepts: '*/*',
    icon: Box,
    endpoint: '/api/v1/tools/universal/execute',
    extraInputs: []
  },
  // @omni-gen-end
];