// OmniNERDashboard.tsx — Biomedical NER Annotation Dashboard
// Inspired by: Bio-Epidemiology-NER visualization UI
// Layer: Interface / TypeScript+React
//
// Real-time entity visualization with confidence-based highlighting,
// entity filtering, and annotation export.

interface BioEntity {
  text: string;
  label: string;
  startChar: number;
  endChar: number;
  confidence: number;
}

interface NERResult {
  text: string;
  entities: BioEntity[];
  processingTimeMs: number;
  modelName: string;
}

interface EntityColorMap {
  [key: string]: { bg: string; border: string; text: string };
}

const ENTITY_COLORS: EntityColorMap = {
  DISEASE: { bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444', text: '#dc2626' },
  DRUG: { bg: 'rgba(59, 130, 246, 0.15)', border: '#3b82f6', text: '#2563eb' },
  GENE: { bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981', text: '#059669' },
  SYMPTOM: { bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b', text: '#d97706' },
  ORGANISM: { bg: 'rgba(139, 92, 246, 0.15)', border: '#8b5cf6', text: '#7c3aed' },
  CHEMICAL: { bg: 'rgba(236, 72, 153, 0.15)', border: '#ec4899', text: '#db2777' },
  ANATOMY: { bg: 'rgba(6, 182, 212, 0.15)', border: '#06b6d4', text: '#0891b2' },
  PROCEDURE: { bg: 'rgba(234, 179, 8, 0.15)', border: '#eab308', text: '#ca8a04' },
  SOCIAL_FACTOR: { bg: 'rgba(107, 114, 128, 0.15)', border: '#6b7280', text: '#4b5563' },
  LOCATION: { bg: 'rgba(34, 197, 94, 0.15)', border: '#22c55e', text: '#16a34a' },
};

interface AnnotatedSpan {
  text: string;
  entity?: BioEntity;
  isEntity: boolean;
}

function buildAnnotatedSpans(text: string, entities: BioEntity[]): AnnotatedSpan[] {
  const sorted = [...entities].sort((a, b) => a.startChar - b.startChar);
  const spans: AnnotatedSpan[] = [];
  let cursor = 0;

  for (const entity of sorted) {
    if (entity.startChar > cursor) {
      spans.push({
        text: text.slice(cursor, entity.startChar),
        isEntity: false,
      });
    }

    if (entity.startChar >= cursor) {
      spans.push({
        text: text.slice(entity.startChar, entity.endChar),
        entity,
        isEntity: true,
      });
      cursor = entity.endChar;
    }
  }

  if (cursor < text.length) {
    spans.push({ text: text.slice(cursor), isEntity: false });
  }

  return spans;
}

interface EntityStats {
  label: string;
  count: number;
  avgConfidence: number;
  examples: string[];
}

function computeEntityStats(entities: BioEntity[]): EntityStats[] {
  const grouped: Map<string, BioEntity[]> = new Map();
  for (const e of entities) {
    const list = grouped.get(e.label) || [];
    list.push(e);
    grouped.set(e.label, list);
  }

  const stats: EntityStats[] = [];
  for (const [label, ents] of grouped) {
    const avgConf = ents.reduce((s, e) => s + e.confidence, 0) / ents.length;
    const unique = [...new Set(ents.map(e => e.text))].slice(0, 5);
    stats.push({
      label,
      count: ents.length,
      avgConfidence: Math.round(avgConf * 1000) / 1000,
      examples: unique,
    });
  }

  return stats.sort((a, b) => b.count - a.count);
}

interface FilterState {
  enabledLabels: Set<string>;
  minConfidence: number;
  searchText: string;
}

function filterEntities(entities: BioEntity[], filter: FilterState): BioEntity[] {
  return entities.filter(e => {
    if (!filter.enabledLabels.has(e.label)) return false;
    if (e.confidence < filter.minConfidence) return false;
    if (filter.searchText && !e.text.toLowerCase().includes(filter.searchText.toLowerCase())) {
      return false;
    }
    return true;
  });
}

interface ExportFormat {
  type: 'json' | 'conll' | 'brat';
}

function exportAnnotations(result: NERResult, format: ExportFormat): string {
  switch (format.type) {
    case 'json':
      return JSON.stringify({
        text: result.text,
        entities: result.entities.map(e => ({
          text: e.text,
          label: e.label,
          start: e.startChar,
          end: e.endChar,
          confidence: e.confidence,
        })),
        metadata: {
          model: result.modelName,
          processingTimeMs: result.processingTimeMs,
          exportedAt: new Date().toISOString(),
        },
      }, null, 2);

    case 'conll': {
      const lines: string[] = [];
      const words = result.text.split(/\s+/);
      let charPos = 0;

      for (const word of words) {
        const wordStart = result.text.indexOf(word, charPos);
        const wordEnd = wordStart + word.length;

        const matchingEntity = result.entities.find(
          e => e.startChar <= wordStart && e.endChar >= wordEnd
        );

        let tag = 'O';
        if (matchingEntity) {
          tag = wordStart === matchingEntity.startChar
            ? `B-${matchingEntity.label}`
            : `I-${matchingEntity.label}`;
        }

        lines.push(`${word}\t${tag}`);
        charPos = wordEnd;
      }

      return lines.join('\n');
    }

    case 'brat': {
      const annotations: string[] = [];
      result.entities.forEach((e, i) => {
        annotations.push(
          `T${i + 1}\t${e.label} ${e.startChar} ${e.endChar}\t${e.text}`
        );
      });
      return annotations.join('\n');
    }
  }
}

// Dashboard state management
interface DashboardState {
  results: NERResult[];
  currentResultIndex: number;
  filter: FilterState;
  selectedEntity: BioEntity | null;
  isProcessing: boolean;
  error: string | null;
}

function createInitialState(): DashboardState {
  return {
    results: [],
    currentResultIndex: 0,
    filter: {
      enabledLabels: new Set(Object.keys(ENTITY_COLORS)),
      minConfidence: 0.0,
      searchText: '',
    },
    selectedEntity: null,
    isProcessing: false,
    error: null,
  };
}

type DashboardAction =
  | { type: 'ADD_RESULT'; payload: NERResult }
  | { type: 'SET_CURRENT_INDEX'; payload: number }
  | { type: 'TOGGLE_LABEL'; payload: string }
  | { type: 'SET_MIN_CONFIDENCE'; payload: number }
  | { type: 'SET_SEARCH_TEXT'; payload: string }
  | { type: 'SELECT_ENTITY'; payload: BioEntity | null }
  | { type: 'SET_PROCESSING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };

function dashboardReducer(state: DashboardState, action: DashboardAction): DashboardState {
  switch (action.type) {
    case 'ADD_RESULT':
      return {
        ...state,
        results: [...state.results, action.payload],
        currentResultIndex: state.results.length,
        isProcessing: false,
      };
    case 'SET_CURRENT_INDEX':
      return { ...state, currentResultIndex: action.payload };
    case 'TOGGLE_LABEL': {
      const labels = new Set(state.filter.enabledLabels);
      if (labels.has(action.payload)) {
        labels.delete(action.payload);
      } else {
        labels.add(action.payload);
      }
      return { ...state, filter: { ...state.filter, enabledLabels: labels } };
    }
    case 'SET_MIN_CONFIDENCE':
      return { ...state, filter: { ...state.filter, minConfidence: action.payload } };
    case 'SET_SEARCH_TEXT':
      return { ...state, filter: { ...state.filter, searchText: action.payload } };
    case 'SELECT_ENTITY':
      return { ...state, selectedEntity: action.payload };
    case 'SET_PROCESSING':
      return { ...state, isProcessing: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

export {
  type BioEntity,
  type NERResult,
  type EntityStats,
  type FilterState,
  type DashboardState,
  type DashboardAction,
  type AnnotatedSpan,
  type ExportFormat,
  ENTITY_COLORS,
  buildAnnotatedSpans,
  computeEntityStats,
  filterEntities,
  exportAnnotations,
  createInitialState,
  dashboardReducer,
};
