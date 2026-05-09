import { z } from 'zod';

export const SqlQuerySchema = z.object({
  query: z.string().min(10).max(5000),
  dialect: z.enum(['postgres', 'mysql', 'sqlite']),
  readonly: z.boolean().default(true),
});

export type SqlQuery = z.infer<typeof SqlQuerySchema>;

export function validateIncomingQuery(payload: unknown): SqlQuery {
  const result = SqlQuerySchema.safeParse(payload);
  if (!result.success) {
    throw new Error(`Invalid Query: ${result.error.message}`);
  }
  if (result.data.readonly && /INSERT|UPDATE|DELETE|DROP|ALTER/i.test(result.data.query)) {
    throw new Error("DML/DDL detected in readonly query mode.");
  }
  return result.data;
}
