# omni-mariadb

> MariaDB native driver with Galera cluster support

**Category:** Database and Data Store
**Version:** 1.0.0
**License:** OMNI-Community
**Registry:** [OMNI-NEXUS](https://nexus.omniframework.dev/packages/omni-mariadb)

## Installation

```bash
omni get omni-mariadb
```

## Dependencies

```bash
omni get omni-std
omni get omni-net
omni get omni-crypto-tls
```

## Quick Start

```omni
import { init, create_client } from "omni-mariadb"

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
omni-mariadb/
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