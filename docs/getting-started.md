# Getting Started with Agent Lucky

Welcome to Agent Lucky - your production-grade agentic AI coding assistant!

## Prerequisites

- **Node.js** 18+ (for VS Code build)
- **Python** 3.10+ (for backend)
- **Git**
- **8GB+ RAM** (16GB+ recommended for larger models)
- **Docker** (optional, for test sandbox)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lavesh00/agent-lucky.git
cd agent-lucky
```

### 2. Set Up the Backend

```bash
cd backend
pip install -r requirements.txt
python main.py --host 127.0.0.1 --port 7777
```

The backend will start on `http://127.0.0.1:7777`

### 3. Download Your First Model

Agent Lucky can run completely offline using local models. To get started:

1. Keep the backend running
2. Use the Model Manager API or UI to download a model:

```bash
# Example: Download Code Llama 7B (4GB)
curl -X POST http://127.0.0.1:7777/models/download \
  -H "Content-Type: application/json" \
  -d '{"model_id": "codellama-7b-q4"}'
```

Available models:
- **Code Llama** (7B, 13B) - Best for code generation
- **StarCoder** - Trained on 80+ languages
- **DeepSeek Coder** - Advanced code understanding
- **Mistral 7B** - General purpose with 32k context
- **Phi-3** - Small but powerful (3.8B)

Models are stored in `~/.agent-lucky/models/`

## Quick Start

### Generate a New Project

```python
import requests

response = requests.post('http://127.0.0.1:7777/agent/start', json={
    "prompt": "Create a React + FastAPI todo app with SQLite database",
    "workspace_path": "./my-project"
})

print(response.json())
```

The agent will:
1. Create a plan with structured TODOs
2. Generate all necessary files
3. Set up the project structure
4. Create tests and documentation
5. Commit changes to Git (if configured)

### Add Features to Existing Code

```python
response = requests.post('http://127.0.0.1:7777/agent/start', json={
    "prompt": "Add user authentication with JWT tokens",
    "workspace_path": "./my-existing-project"
})
```

The agent will:
1. Analyze your existing code
2. Plan the authentication implementation
3. Modify existing files
4. Add new auth routes
5. Update tests

## Configuration

### Backend Settings

Create a `.env` file in the backend directory:

```env
# Model Settings
AGENT_LUCKY_MODEL_PATH=~/.agent-lucky/models
AGENT_LUCKY_DEFAULT_MODEL=codellama-13b

# Backend Settings
AGENT_LUCKY_BACKEND_PORT=7777
AGENT_LUCKY_LOG_LEVEL=info

# Git Settings
AGENT_LUCKY_GIT_COMMIT_MODE=per-todo  # per-file, per-todo, batch

# GitHub Settings
GITHUB_TOKEN=your_github_token_here  # Optional

# RAG Settings
AGENT_LUCKY_RAG_ENABLED=true
AGENT_LUCKY_RAG_CHUNK_SIZE=1000
```

### Model Selection

Different models for different tasks:

- **Planning**: Use larger models (13B+) for better task breakdown
- **Code Generation**: Code Llama or DeepSeek Coder
- **General Tasks**: Mistral or Llama 3

```python
# Specify model for specific task
response = requests.post('http://127.0.0.1:7777/agent/start', json={
    "prompt": "...",
    "workspace_path": "...",
    "model_preference": "deepseek-coder-6.7b-q4"
})
```

## Next Steps

- [Model Management](models.md) - Download and manage models
- [GitHub Integration](github-setup.md) - Set up GitHub automation
- [Project Templates](templates.md) - Available project templates
- [MCP Integration](mcp.md) - Extend with custom tools
- [Architecture](architecture.md) - System architecture overview

## Troubleshooting

### Backend won't start

**Problem**: `ModuleNotFoundError` or import errors

**Solution**: Make sure all dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

### Model download fails

**Problem**: `HfHubHTTPError` or timeout

**Solution**: Check your internet connection and HuggingFace access. Some models require accepting license agreements on HuggingFace.

### Out of memory

**Problem**: System freezes when running large models

**Solution**: 
- Use smaller quantized models (Q4 instead of Q8)
- Close other applications
- Use smaller models like Phi-3 (3.8B) instead of 13B models

### Agent produces invalid code

**Problem**: Generated code has syntax errors

**Solution**:
- Use code-specific models (Code Llama, DeepSeek Coder)
- Increase temperature (0.4-0.6 works well for code)
- Provide more context in your prompt
- Enable RAG to give agent access to existing codebase

## Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/lavesh00/agent-lucky/issues)
- **Discussions**: [Ask questions](https://github.com/lavesh00/agent-lucky/discussions)
- **Discord**: [Join the community](https://discord.gg/agentlucky)

## What's Next?

Now that you have Agent Lucky running, try:

1. **Generate a sample project** to see the full workflow
2. **Explore different models** to find what works best for you
3. **Set up GitHub integration** for automated commits and PRs
4. **Try web scraping** to clone and analyze existing sites
5. **Create custom MCP tools** for your specific needs

Happy coding with Agent Lucky! 🍀

