// AUTO-GENERATED OMNI CLIENT BY AST ANALYZER
export interface UserQuery {
  id: string;
  name: string;
  email: string;
}

export class OmniClient {
  static async fetchUser(id: string): Promise<UserQuery> {
     // Native type-safe GraphQL execution via OMNI Bridge
     return await __omni_internal_fetch(`query { user(id: "${id}") { id name email } }`);
  }
}