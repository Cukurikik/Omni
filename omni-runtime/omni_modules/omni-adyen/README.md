# omni-adyen

> Adyen unified commerce for POS and online payments

**Category:** Payment and Financial
**Version:** 1.0.0
**License:** OMNI-Community
**Registry:** [OMNI-NEXUS](https://nexus.omniframework.dev/packages/omni-adyen)

## Installation

```bash
omni get omni-adyen
```

## Dependencies

```bash
omni get omni-std
omni get omni-net
omni get omni-crypto-tls
```

## Quick Start

```omni
import { init, create_client } from "omni-adyen"

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
omni-adyen/
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