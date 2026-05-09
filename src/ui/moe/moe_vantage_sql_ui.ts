// moe_vantage_sql_ui.ts — Interface Layer: Vantage SQL UI
// TypeScript React Hook managing Text-to-SQL form state securely.

import { useState } from 'react';

export interface SqlQueryState {
  naturalInput: string;
  generatedSql: string | null;
  isLoading: boolean;
  error: string | null;
}

export function useVantageSql() {
  const [state, setState] = useState<SqlQueryState>({
    naturalInput: '',
    generatedSql: null,
    isLoading: false,
    error: null,
  });

  const generate = async (prompt: string, schemaId: string) => {
    setState(s => ({ ...s, isLoading: true, error: null }));
    try {
      // Zero-mock: Simulated fetch to internal API
      const response = await fetch('/api/vantage/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, schemaId })
      });
      
      if (!response.ok) throw new Error("SQL Generation failed");
      const data = await response.json();
      
      setState(s => ({ ...s, generatedSql: data.sql, isLoading: false }));
    } catch (err: any) {
      setState(s => ({ ...s, error: err.message, isLoading: false }));
    }
  };

  return { state, generate };
}
