# Agent Lucky 🍀

**A Production-Grade Agentic AI Coding System Built on VS Code**

Agent Lucky is a Cursor-style AI coding assistant that transforms VS Code into a powerful agentic system capable of generating entire projects, fixing bugs, and managing codebases—all while running completely offline with local open-source models.

## 🌟 Features

### Core Capabilities
- **🤖 Agentic Loop**: Planner → Worker → Reasoning Summarizer architecture
- **💻 Local Models**: Run Code Llama, StarCoder, DeepSeek Coder, and more—completely offline
- **🔌 MCP Integration**: Model Context Protocol support for extensibility
- **🌐 Web Scraping**: Clone and convert websites into projects
- **🔄 Git Automation**: Intelligent commit strategies with GitHub integration
- **🎨 Professional UI**: Cursor-inspired dark theme integrated into VS Code
- **🧠 RAG System**: Context-aware code understanding with FAISS vector search
- **🔒 Privacy-First**: All data stays local, no telemetry

### Agentic Workflow
1. **Planner**: Breaks down high-level prompts into structured TODOs
2. **Worker**: Executes each TODO with RAG context and MCP tools
3. **Summarizer**: Creates evidence-backed summaries for continuous improvement

### Project Generation
Generate complete, production-ready projects from a single prompt:
- Python backends (Flask, Django, FastAPI)
- JavaScript frontends (React, Next.js, Vue)
- Full-stack applications
- Docker configurations
- CI/CD pipelines
- Tests and documentation

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (for VS Code build)
- Python 3.10+ (for backend)
- Git
- 8GB+ RAM (16GB+ recommended for larger models)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/lavesh00/agent-lucky.git
cd agent-lucky
```

2. **Set up the backend**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **Build VS Code distribution**
```bash
cd ../vscode
npm install
npm run build
```

4. **Download your first model**
- Open Agent Lucky
- Click "Model Manager" in the Activity Bar
- Select a model (e.g., Code Llama 13B)
- Click "Download"

## 📚 Architecture

```
agent-lucky/
├── vscode/                  # Custom VS Code distribution
├── backend/                 # Python FastAPI backend
│   ├── models/             # Local model management
│   ├── agent/              # Planner/Worker/Summarizer
│   ├── rag/                # FAISS + embeddings
│   ├── scraper/            # Web scraping & automation
│   ├── git_automation/     # Git/GitHub integration
│   ├── mcp/                # MCP protocol
│   └── sandbox/            # Test runner
├── ui-components/          # React components for agent panels
├── theme/                  # Cursor-style dark theme
└── docs/                   # Documentation
```

## 🎯 Usage

### Generate a New Project
1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Run `Agent: Start New Project`
3. Describe your project in natural language
4. Watch as Agent Lucky creates your entire codebase

### Add Features to Existing Code
1. Open your project in Agent Lucky
2. Click the Agent panel
3. Type: "Add user authentication with JWT"
4. Review and accept the changes

### Fix Bugs
1. Select problematic code
2. Right-click → "Ask Agent to Fix This"
3. Agent analyzes, proposes fixes, and runs tests

### Scrape and Clone Websites
1. Run `Agent: Scrape Website`
2. Enter the URL
3. Agent downloads assets and generates a project

## 🔧 Configuration

Configure Agent Lucky via Settings (`Ctrl+,` / `Cmd+,`):

```json
{
  "agentLucky.modelPath": "~/.agent-lucky/models",
  "agentLucky.defaultModel": "codellama-13b",
  "agentLucky.backend.port": 7777,
  "agentLucky.git.commitMode": "per-todo",
  "agentLucky.rag.enabled": true,
  "agentLucky.scraper.respectRobotsTxt": true
}
```

## 🤝 Supported Models

### Code-Specific Models
- **Code Llama** (7B, 13B, 34B)
- **StarCoder / StarCoder2** (3B, 7B, 15B)
- **DeepSeek Coder** (6.7B, 33B)

### General Models
- **Llama 3 / 3.1** (8B, 70B)
- **Mistral / Mixtral** (7B, 8x7B)
- **Phi-3** (3.8B, 14B)

All models run locally via llama.cpp with quantization support (4-bit, 5-bit, 8-bit).

## 🔐 Security & Privacy

- ✅ All processing happens locally
- ✅ No telemetry or tracking
- ✅ Backend listens only on localhost
- ✅ Explicit permission prompts for external actions
- ✅ Secure credential storage (OS keychain)
- ✅ No data sent to external servers

## 📖 Documentation

- [Getting Started Guide](docs/getting-started.md)
- [Model Download Guide](docs/models.md)
- [GitHub Setup Tutorial](docs/github-setup.md)
- [MCP Integration Guide](docs/mcp.md)
- [Architecture Overview](docs/architecture.md)
- [Contributing Guide](docs/contributing.md)

## 🛠️ Development

### Building from Source

1. **Clone with VS Code submodule**
```bash
git clone --recursive https://github.com/lavesh00/agent-lucky.git
```

2. **Install dependencies**
```bash
# Backend
cd backend
pip install -r requirements-dev.txt

# VS Code
cd ../vscode
npm install
```

3. **Run in development mode**
```bash
# Terminal 1: Backend
cd backend
python main.py --dev

# Terminal 2: VS Code
cd vscode
npm run watch
```

### Testing
```bash
# Backend tests
cd backend
pytest

# VS Code tests
cd vscode
npm test
```

## 🌐 MCP Integration

Agent Lucky supports the Model Context Protocol for extensibility:

- Add custom tools
- Integrate external models
- Connect to documentation sources
- Build custom context providers

See [MCP Guide](docs/mcp.md) for details.

## 📜 License

Agent Lucky is released under the MIT License. See [LICENSE](LICENSE) for details.

VS Code is licensed under the MIT License by Microsoft Corporation.

## 🙏 Acknowledgments

- **VS Code**: Built on top of the excellent VS Code platform
- **llama.cpp**: Local model inference engine
- **FAISS**: Vector similarity search
- **FastAPI**: Modern Python web framework
- **Cursor**: Inspiration for the UI/UX design

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/contributing.md) for guidelines.

## 📞 Support

- 📧 Email: support@agentlucky.dev
- 💬 Discord: [Join our community](https://discord.gg/agentlucky)
- 🐛 Issues: [GitHub Issues](https://github.com/lavesh00/agent-lucky/issues)

## 🗺️ Roadmap

- [ ] VS Code extension with integrated panels
- [ ] Multi-model support (use different models for different tasks)
- [ ] Cloud sync (optional)
- [ ] Team collaboration features
- [ ] Voice input for prompts
- [ ] Visual debugging interface
- [ ] Plugin marketplace
- [ ] Mobile app for monitoring

## 📊 Project Status

✅ **v1.0.0 Released** - Core functionality complete
- Agentic loop (Planner/Worker/Summarizer)
- Local model support
- RAG system
- Git/GitHub automation
- Web scraping
- MCP integration
- Project templates

🚧 **In Progress**
- VS Code UI panels
- Build system for distribution
- Additional templates

📋 **Planned**
- Cloud model support (optional)
- Team features
- Plugin system

---

**Built with ❤️ by the Agent Lucky team**

*Bringing the power of agentic AI to every developer, completely offline.*

