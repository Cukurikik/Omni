# omni-cloudflare-workers

> Cloudflare Workers runtime with KV, Durable Objects, D1

**Category:** Cloud and Object Storage
**Version:** 1.0.0
**License:** OMNI-Community
**Registry:** [OMNI-NEXUS](https://nexus.omniframework.dev/packages/omni-cloudflare-workers)

## Installation

```bash
omni get omni-cloudflare-workers
```

## Dependencies

```bash
omni get omni-std
omni get omni-net
```

## Quick Start

```omni
import { init, create_client } from "omni-cloudflare-workers"

fn main() -> Result<(), Error> {
    let client = create_client(Config::default())?
    let result = client.execute()?
    println("Result: {}", result)
    Ok(())
}
```

## API Reference

| Function | Description | Returns |
|----------|-------------|---------|
| `init()` | Initialize the module runtime | `Result<Instance, InitError>` |
| `create_client(config)` | Create a configured client | `Result<Client, ConfigError>` |
| `health_check()` | Verify connectivity and readiness | `Result<Status, HealthError>` |
| `shutdown()` | Gracefully shutdown all connections | `Result<(), ShutdownError>` |

## Architecture

```
omni-cloudflare-workers/
+-- Omnifile.toml
+-- README.md
+-- src/
|   +-- lib.omni
|   +-- types.omni
|   +-- config.omni
+-- tests/
|   +-- test.omni
+-- examples/
    +-- basic.omni
```

## Performance

- Zero-copy I/O for data larger than 1MB
- Connection pooling with adaptive sizing
- LLVM-optimized hot paths
- Monadic error handling, no try/catch overhead

## License

OMNI-Community License. See Omnifile.toml for details.