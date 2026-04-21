# OMNI Domain Layer Engines

This directory contains **business logic, DDD aggregates, and enterprise rule engines**
implementing convention-over-configuration patterns and schema-first API contracts.

## Supported Languages
| Language | Idiom | Use Case |
|----------|-------|----------|
| **C#** | `cs::domain` | DDD aggregate, CQRS, enterprise business logic |
| **Java** | `java::spring` | Enterprise backend, Android, legacy bridge |
| **Ruby** | `rb::route` | Convention-over-configuration, rapid DSL |
| **PHP** | `php::web` | Web request lifecycle, CMS integration |
| **GraphQL** | `@schema` | Schema-first data contract, type-safe API |

## Engines
| File | Source Repo | Purpose |
|------|-------------|---------|
| `AndroidViewClientDomain.cs` | AndroidViewClient | Mobile view business aggregates |
| `AutoCommenterEngine.java` | auto-commenter | Enterprise PR review rules engine |
| `auto_anime_organizer.rb` | AutoAnimeMv | Media episode recognition & directory DSL |
| `app_store_connect.rb` | app-store-connect-cli | App Store release management |
| `comic_dl_service.php` | comic-dl | Stateful media asset management |
| `Order.cs` | OMNI Core | Domain order aggregate root |
| `schema.graphql` | OMNI Core | Unified API contract (all domain entities) |
| `SysBotPokemon.cs` | SysBot.NET | Remote console game automation controller |
| `wordmove_deployer.rb` | Wordmove | WordPress deployment automation |
| `YoutarrMediaService.java` | Youtarr | Enterprise media download service |
