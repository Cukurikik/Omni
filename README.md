# Omni Framework

Omni is a high-performance, cross-platform framework designed for building unified tools across multiple layers: UI (React/TypeScript), API (Golang), and Native Engines (C++, Python).

## 🚀 Key Features

- **Unified Tool Ecosystem**: Easily create and manage tools that span across frontend and backend.
- **Cross-Platform Support**: Built with portability in mind, supporting both Windows and Unix-like systems.
- **Zero-Copy Memory Mapping**: Utilizes `mmap` for efficient data sharing between Golang and native engines.
- **Self-Healing Infrastructure**: Integrated CLI with `omni scan` and `omni fix` to detect and repair system anomalies.
- **Decentralized Module Manager**: Install and share community modules directly from GitHub.
- **Built-in API Documentation**: Automatically generate API metadata and documentation.

## 🛠️ Getting Started

### Prerequisites

- **Node.js** (v18+)
- **Golang** (v1.20+)
- **C++ Compiler** (optional, for native engines)
- **Python** (optional, for AI tools)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Cukurikik/Omni.git
   cd Omni
   ```

2. Initialize the project:
   ```bash
   node bin/omni.mjs init
   ```

3. Install dependencies:
   ```bash
   node bin/omni.mjs install
   ```

### Development

Start the development server with live-reload:
```bash
node bin/omni.mjs dev
```

## 📦 Project Structure

- `api/`: Golang backend gateway and services.
- `ui/`: React/TypeScript frontend.
- `engine/`: Native processing engines (C++, Python).
- `bin/`: Omni CLI tools.
- `configs/`: System and tool registries.
- `sdk/`: Omni client SDK.

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and ensure they pass `node bin/omni.mjs scan`.
4. Submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
