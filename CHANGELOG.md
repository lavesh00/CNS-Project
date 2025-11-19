# Changelog

All notable changes to Agent Lucky will be documented in this file.

## [1.0.0] - 2025-11-19

### Added
- Initial release of Agent Lucky
- Agentic loop (Planner → Worker → Summarizer)
- Local model support with llama.cpp
- Model Manager with HuggingFace integration
- RAG system with FAISS and sentence-transformers
- Git automation with configurable commit strategies
- GitHub integration (repo creation, PR management)
- Web scraper with Playwright
- MCP (Model Context Protocol) client
- Test sandbox with Docker support
- Project templates (React + FastAPI, Python CLI)
- Cursor-style professional dark theme
- Comprehensive documentation

### Models Supported
- Code Llama (7B, 13B, 34B)
- StarCoder (7B)
- DeepSeek Coder (6.7B)
- Llama 3 (8B)
- Mistral (7B)
- Phi-3 (3.8B)

### Features
- ✅ Offline operation with local models
- ✅ Full project generation from prompts
- ✅ Context-aware code generation with RAG
- ✅ Intelligent code refactoring
- ✅ Automated Git workflows
- ✅ Website scraping and cloning
- ✅ Multi-language support (20+ languages)
- ✅ Docker-based test isolation
- ✅ Structured reasoning with evidence
- ✅ Extensible via MCP

### Architecture
- FastAPI backend (Python 3.10+)
- llama.cpp for local inference
- FAISS for vector search
- React UI components
- VS Code integration (planned)

## [Unreleased]

### Planned
- VS Code extension with custom panels
- Multi-model support (different models per task)
- Voice input for prompts
- Cloud sync (optional)
- Team collaboration features
- Visual debugging interface
- Plugin marketplace
- Auto-update system

### In Progress
- VS Code fork with integrated agent panels
- Build system for distribution
- Additional project templates
- Enhanced MCP server implementations

## Contributing

See [CONTRIBUTING.md](docs/contributing.md) for how to contribute.

## License

MIT License - see [LICENSE](LICENSE) for details.

