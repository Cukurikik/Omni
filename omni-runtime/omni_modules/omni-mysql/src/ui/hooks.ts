// omni-mysql â€” Framework-Agnostic Hooks

import { TypeSafeClient, ApiResponse, ClientConfig } from './sdk';
import { ReactiveStore } from './reactive';

export function createClient(config: ClientConfig): TypeSafeClient { return new TypeSafeClient(config); }

export function createStore<T>(initial: T): ReactiveStore<T> { return new ReactiveStore(initial); }

export function createQueryHook<T>(client: TypeSafeClient, path: string) {
  const store = new ReactiveStore<{ loading: boolean; data?: T; error?: string }>({ loading: false });
  return {
    store,
    fetch: async () => { store.set({ loading: true }); const res = await client.get<T>(path); store.set({ loading: false, data: res.data, error: res.error }); return res; },
    refetch: async () => { const res = await client.get<T>(path); store.update(s => ({ ...s, data: res.data })); return res; },
  };
}

export function createMutationHook<TInput, TOutput>(client: TypeSafeClient, path: string) {
  return {
    mutate: async (input: TInput): Promise<ApiResponse<TOutput>> => client.post<TOutput>(path, input),
    update: async (id: string, input: TInput): Promise<ApiResponse<TOutput>> => client.put<TOutput>(path + '/' + id, input),
    remove: async (id: string): Promise<ApiResponse<TOutput>> => client.delete<TOutput>(path + '/' + id),
  };
}