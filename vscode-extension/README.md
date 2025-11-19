# Agent Lucky VS Code Extension

Connect Agent Lucky to VS Code for seamless AI-powered coding.

## Features

- **Agent Panel**: Interactive UI to start agent tasks
- **Status Bar**: Real-time backend status
- **Commands**: Quick access via command palette
- **Model Management**: Download and manage AI models
- **Auto-completion**: Generate code with AI assistance

## Installation

1. Copy the `vscode-extension` folder to VS Code extensions:
   - Windows: `%USERPROFILE%\.vscode\extensions\agent-lucky`
   - Mac/Linux: `~/.vscode/extensions/agent-lucky`

2. Install dependencies:
   ```bash
   cd vscode-extension
   npm install
   ```

3. Reload VS Code

## Usage

### Start Agent
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Agent Lucky: Start Agent"
3. Enter your prompt
4. Agent will generate code in your workspace

### Show Panel
1. Click the Agent Lucky icon in the Activity Bar (left sidebar)
2. Or use command: "Agent Lucky: Show Panel"

### Download Models
1. Command: "Agent Lucky: List Models"
2. Select a model to download
3. Wait for download to complete

## Configuration

Access settings via File > Preferences > Settings > Agent Lucky

- **Backend URL**: Default `http://127.0.0.1:7777`
- **Auto Start**: Auto-start backend on launch
- **Default Model**: Model to use for generation

## Requirements

- VS Code 1.80.0 or higher
- Agent Lucky backend running
- Python 3.10+

## Commands

- `Agent Lucky: Start Agent` - Start a new agent task
- `Agent Lucky: Show Panel` - Open agent panel
- `Agent Lucky: Check Status` - Check backend status
- `Agent Lucky: List Models` - List available models
- `Agent Lucky: Download Model` - Download a model

## Status Bar

The status bar shows:
- ✅ Ready - Backend is healthy
- ⚠️  Offline - Backend not running
- 🔄 Working - Agent is processing

## Troubleshooting

**Extension not working?**
- Ensure backend is running: `py backend/main.py`
- Check backend URL in settings
- Reload VS Code window

**Agent not responding?**
- Check workspace folder is open
- Verify backend status in terminal
- Check output panel for errors

## Support

- GitHub: https://github.com/lavesh00/agent-lucky
- Issues: https://github.com/lavesh00/agent-lucky/issues

