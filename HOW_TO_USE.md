# 🍀 How to Use Agent Lucky with VS Code

## ✅ Current Status

**Backend**: ✅ RUNNING on http://127.0.0.1:7777  
**VS Code Extension**: ✅ INSTALLED at `C:\Users\asus\.vscode\extensions\agent-lucky`  
**Status**: 🟢 Ready to use!

## 🚀 Quick Start Guide

### Step 1: Reload VS Code

The extension is installed but VS Code needs to reload:

1. Press `Ctrl+Shift+P`
2. Type: **Reload Window**
3. Press Enter

### Step 2: Find Agent Lucky

After reload, you'll see Agent Lucky in multiple places:

**A) Activity Bar (Left Sidebar)**
- Look for the Agent Lucky icon 
- Click it to open the panel

**B) Command Palette**
- Press `Ctrl+Shift+P`
- Type: **Agent Lucky**
- See all available commands

**C) Status Bar (Bottom)**
- Look for: **✅ Agent Lucky: Ready**
- Click it to check backend status

### Step 3: Use Agent Lucky

#### Option A: Use the Panel (Recommended)

1. Click Agent Lucky icon in Activity Bar (left sidebar)
2. Enter your prompt in the text area:
   ```
   Create a REST API with user authentication
   ```
3. Click **🚀 Start Agent**
4. Watch the magic happen!

#### Option B: Use Commands

1. Press `Ctrl+Shift+P`
2. Type: **Agent Lucky: Start Agent**
3. Enter your prompt
4. Done!

## 📋 Available Commands

Access via `Ctrl+Shift+P`:

- **Agent Lucky: Start Agent** - Start a new task
- **Agent Lucky: Show Panel** - Open the agent panel
- **Agent Lucky: Check Status** - Check backend health
- **Agent Lucky: List Models** - Browse available models
- **Agent Lucky: Download Model** - Download a model

## 💡 Example Prompts

Try these prompts to see Agent Lucky in action:

**Create a new project:**
```
Create a React todo app with local storage
```

**Add features:**
```
Add user authentication with JWT tokens
```

**Fix bugs:**
```
Fix the API endpoint that's returning 500 errors
```

**Generate tests:**
```
Create unit tests for the UserService class
```

**Refactor code:**
```
Refactor this component to use React hooks
```

## 📊 What Happens When You Start Agent?

1. **Planning** - Agent analyzes your prompt and creates a plan
2. **TODO Generation** - Breaks down into actionable steps
3. **Code Generation** - Writes code using RAG context
4. **Git Commits** - Auto-commits changes (configurable)
5. **Testing** - Runs tests if specified
6. **Summary** - Provides evidence-backed summary

## 🎯 Features You Can Use Right Now

### ✅ Working Features:

- ✅ **Agent Panel** - Interactive UI in VS Code
- ✅ **Status Bar** - Real-time backend monitoring
- ✅ **Start Agent** - Generate code from prompts
- ✅ **Model Management** - Download AI models
- ✅ **Backend Integration** - Full API connection
- ✅ **WebView UI** - Beautiful, integrated interface

### 📥 Download a Model

To use the agent, you need a model:

1. Press `Ctrl+Shift+P`
2. Type: **Agent Lucky: List Models**
3. Select a model:
   - **Code Llama 7B** (4.1GB) - Fast, good quality
   - **Code Llama 13B** (7.9GB) - Best quality
   - **Phi-3 Mini** (2.3GB) - Smallest, fastest
4. Wait for download (5-20 minutes depending on speed)

## 🔧 Settings

Access: `File > Preferences > Settings > Agent Lucky`

**Backend URL**: `http://127.0.0.1:7777`  
**Auto Start**: Enable to start backend automatically  
**Default Model**: Choose your preferred model  

## 📸 What You'll See

### Status Bar
```
✅ Agent Lucky: Ready     ← Green = Backend healthy
⚠️  Agent Lucky: Offline  ← Red = Backend down
🔄 Agent Lucky: Working   ← Blue = Agent processing
```

### Agent Panel

```
┌─────────────────────────────────┐
│     🍀 Agent Lucky              │
├─────────────────────────────────┤
│                                 │
│  What do you want to create?    │
│  ┌─────────────────────────┐   │
│  │ Create a REST API with  │   │
│  │ authentication...       │   │
│  └─────────────────────────┘   │
│                                 │
│  [🚀 Start Agent] [📊 Status]  │
│                                 │
│  Status: Ready                  │
│  Backend: Running               │
│  Models: 0 installed            │
└─────────────────────────────────┘
```

## 🐛 Troubleshooting

### Extension not appearing?
```
1. Check: %USERPROFILE%\.vscode\extensions\agent-lucky exists
2. Reload: Ctrl+Shift+P -> "Reload Window"
3. Check: Help > Toggle Developer Tools > Console for errors
```

### Status bar shows "Offline"?
```
1. Ensure backend is running:
   cd backend
   py main.py

2. Check terminal for errors
3. Wait 5 seconds, click status bar to recheck
```

### Commands not working?
```
1. Reload VS Code window
2. Check backend is running: http://127.0.0.1:7777/health
3. Open workspace folder (Agent needs a workspace)
```

## 📚 Learn More

- **Architecture**: `docs/architecture.md`
- **API Reference**: `docs/api-reference.md`
- **Models Guide**: `docs/models.md`
- **FAQ**: `docs/FAQ.md`

## 🎓 Tips for Best Results

1. **Be Specific**: "Create a REST API with JWT auth" > "Make an API"
2. **Provide Context**: Mention your tech stack (React, FastAPI, etc.)
3. **Use Workspaces**: Open a folder before starting agent
4. **Review Changes**: Check generated code before committing
5. **Iterate**: Start simple, then add features incrementally

## 🆘 Need Help?

- **Backend logs**: Check terminal where `py main.py` is running
- **Extension logs**: `Help > Toggle Developer Tools > Console`
- **GitHub Issues**: https://github.com/lavesh00/agent-lucky/issues

---

## 🎉 You're All Set!

**Agent Lucky is ready to use!** Just:
1. Reload VS Code (`Ctrl+Shift+P` -> "Reload Window")
2. Click Agent Lucky icon in left sidebar
3. Enter your prompt
4. Click "Start Agent"

**Happy coding with Agent Lucky!** 🍀

