# Agent Lucky VS Code Extension Installation

## Quick Install (Windows)

1. **Run the installer:**
   ```powershell
   cd vscode-extension
   .\install.ps1
   ```

2. **Reload VS Code:**
   - Press `Ctrl+Shift+P`
   - Type "Reload Window"
   - Press Enter

3. **Done!** Look for Agent Lucky icon in the Activity Bar (left sidebar)

## Manual Install

### Windows
```powershell
# Copy extension
xcopy vscode-extension %USERPROFILE%\.vscode\extensions\agent-lucky /E /I /Y

# Install dependencies
cd %USERPROFILE%\.vscode\extensions\agent-lucky
npm install

# Reload VS Code
```

### Mac / Linux
```bash
# Copy extension
cp -r vscode-extension ~/.vscode/extensions/agent-lucky

# Install dependencies
cd ~/.vscode/extensions/agent-lucky
npm install

# Reload VS Code
```

## Verify Installation

1. Open VS Code
2. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
3. Type "Agent Lucky"
4. You should see Agent Lucky commands

## Usage

### Start Agent
1. Press `Ctrl+Shift+P`
2. Type "Agent Lucky: Start Agent"
3. Enter your prompt
4. Agent will generate code

### Show Panel
1. Click Agent Lucky icon in Activity Bar
2. Or press `Ctrl+Shift+P` -> "Agent Lucky: Show Panel"

### Download Models
1. Press `Ctrl+Shift+P`
2. Type "Agent Lucky: List Models"
3. Select model to download

## Troubleshooting

### Extension not showing?
- Reload VS Code window
- Check extensions folder: `%USERPROFILE%\.vscode\extensions\agent-lucky`
- Look for errors in: Help > Toggle Developer Tools > Console

### Backend not connecting?
- Ensure backend is running: `py backend/main.py`
- Check backend URL in settings: File > Preferences > Settings > Agent Lucky
- Default: http://127.0.0.1:7777

### Status bar shows "Offline"?
- Start backend: `py backend/main.py`
- Wait a few seconds
- Click status bar to recheck

## Configuration

Access: File > Preferences > Settings > Extensions > Agent Lucky

**Backend URL**: Default `http://127.0.0.1:7777`  
**Auto Start**: Auto-start backend on launch  
**Default Model**: Model for code generation  

## Features

✅ **Agent Panel** - Interactive UI for prompts  
✅ **Status Bar** - Real-time backend status  
✅ **Commands** - Quick access via palette  
✅ **Model Management** - Download models  
✅ **Pure JavaScript** - No TypeScript required  

## Support

Need help?
- GitHub: https://github.com/lavesh00/agent-lucky
- Issues: https://github.com/lavesh00/agent-lucky/issues
- Docs: docs/getting-started.md


