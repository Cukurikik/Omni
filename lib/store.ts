import { create } from 'zustand';
import { ToolCategory, OmniTool } from './types';
import { OMNI_TOOLS } from './config';

interface OmniStore {
  // Tools state
  tools: OmniTool[];
  selectedCategory: ToolCategory | 'ALL';
  searchQuery: string;
  
  // Execution state
  isExecuting: boolean;
  currentTool: string | null;
  progress: number;
  result: any;
  error: string | null;
  
  // UI state
  sidebarOpen: boolean;
  
  // Actions
  setCategory: (category: ToolCategory | 'ALL') => void;
  setSearchQuery: (query: string) => void;
  setExecuting: (executing: boolean) => void;
  setCurrentTool: (toolId: string | null) => void;
  setProgress: (progress: number) => void;
  setResult: (result: any) => void;
  setError: (error: string | null) => void;
  toggleSidebar: () => void;
  
  // Computed
  getFilteredTools: () => OmniTool[];
  getToolCounts: () => Record<string, number>;
}

export const useOmniStore = create<OmniStore>((set, get) => ({
  // Initial state
  tools: OMNI_TOOLS,
  selectedCategory: 'ALL',
  searchQuery: '',
  
  isExecuting: false,
  currentTool: null,
  progress: 0,
  result: null,
  error: null,
  
  sidebarOpen: true,
  
  // Actions
  setCategory: (category) => set({ selectedCategory: category }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setExecuting: (executing) => set({ isExecuting: executing }),
  setCurrentTool: (toolId) => set({ currentTool: toolId }),
  setProgress: (progress) => set({ progress }),
  setResult: (result) => set({ result }),
  setError: (error) => set({ error }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  // Computed
  getFilteredTools: () => {
    const { tools, selectedCategory, searchQuery } = get();
    return tools.filter(tool => {
      const matchCat = selectedCategory === 'ALL' || tool.category === selectedCategory;
      const matchSearch = !searchQuery || 
        tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    });
  },
  
  getToolCounts: () => {
    const counts: Record<string, number> = { ALL: OMNI_TOOLS.length };
    OMNI_TOOLS.forEach(tool => {
      counts[tool.category] = (counts[tool.category] || 0) + 1;
    });
    return counts;
  },
}));