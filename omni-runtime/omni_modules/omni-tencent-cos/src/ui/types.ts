// omni-tencent-cos â€” Core TypeScript Type Definitions

export type UUID = string;
export type ISO8601 = string;
export type JSONValue = string | number | boolean | null | JSONValue[] | { [key: string]: JSONValue };

export interface Entity { id: UUID; data: JSONValue; status: Status; createdAt: ISO8601; updatedAt: ISO8601; metadata?: Record<string, string>; }
export interface PageRequest { page: number; size: number; sortBy?: string; ascending?: boolean; }
export interface PageResponse<T> { items: T[]; total: number; page: number; size: number; hasNext: boolean; }
export enum Status { Active = 'ACTIVE', Inactive = 'INACTIVE', Pending = 'PENDING', Failed = 'FAILED', Cancelled = 'CANCELLED', Completed = 'COMPLETED', Archived = 'ARCHIVED' }
export interface CreateInput { data: JSONValue; metadata?: Record<string, string>; }
export interface UpdateInput { data?: JSONValue; status?: Status; metadata?: Record<string, string>; }
export interface FilterInput { status?: Status; createdAfter?: ISO8601; createdBefore?: ISO8601; search?: string; }
export interface HealthStatus { healthy: boolean; latency: number; version: string; }
export interface Stats { totalEntities: number; activeConnections: number; uptime: number; }
export interface ErrorResponse { code: string; message: string; details?: Record<string, string>; }