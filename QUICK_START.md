# 🚀 Agent Lucky - Quick Start Guide

## ✅ Extension Successfully Installed!

Your extension is now installed as: **agent-lucky.agent-lucky**

---

## 🎯 How to Use (3 Simple Steps)

### Step 1: Reload VS Code

**In your VS Code window:**

1. Press: **`Ctrl + Shift + P`**
2. Type: **`Developer: Reload Window`**
3. Press: **`Enter`**

### Step 2: Verify Extension is Active

After reload, you should see:

**✅ In Status Bar (Bottom Left):**
- Look for: `✓ Agent Lucky: Ready` or `⚠ Agent Lucky: Offline`

**✅ In Command Palette:**
- Press: `Ctrl + Shift + P`
- Type: `Agent Lucky`
- You should see 5 commands:
  - Agent Lucky: Start Agent
  - Agent Lucky: Show Panel
  - Agent Lucky: Check Status
  - Agent Lucky: List Models
  - Agent Lucky: Download Model

### Step 3: Open the Agent Panel

**Press: `Ctrl + Shift + P`**
**Type: `Agent Lucky: Show Panel`**

This opens the Agent Lucky interface where you can:
- Enter prompts
- Start coding tasks
- Check backend status

---

## 🎨 What You'll See

### Status Bar Item (Bottom Left)
```
✓ Agent Lucky: Ready     ← Backend connected
⚠ Agent Lucky: Offline   ← Backend not running
```

### Agent Panel
- 🍀 Logo and title
- Text area for your prompts
- Buttons to start agent and check status
- Real-time status display

---

## 💡 Try Your First Task

1. **Open Agent Lucky Panel**
   - `Ctrl + Shift + P` → `Agent Lucky: Show Panel`

2. **Enter a prompt**, for example:
   ```
   Create a simple Flask REST API with /hello endpoint
   ```

3. **Click "🚀 Start Agent"**

4. **Watch the magic happen!**
   - Backend processes your request
   - Agent plans and executes tasks
   - Code is generated in your workspace
   - Each file is committed to Git automatically

---

## 🔧 Commands Reference

### `Agent Lucky: Show Panel`
Opens the main Agent Lucky interface

### `Agent Lucky: Start Agent`
Quick way to start a task (shows input box)

### `Agent Lucky: Check Status`
Check backend connection and health

### `Agent Lucky: List Models`
View available models for download

### `Agent Lucky: Download Model`
Download a specific model by ID

---

## 🐛 Troubleshooting

### "Backend Offline" Message

**Solution:** Start the backend:
```powershell
cd "C:\Users\asus\Desktop\agent lucky\backend"
py main.py
```

Backend should run at: `http://127.0.0.1:7777`

### Extension Not Showing

1. Close ALL VS Code windows
2. Reopen VS Code
3. Wait 5 seconds
4. Try `Ctrl + Shift + P` → `Agent Lucky`

### Commands Don't Work

1. Check backend is running (see above)
2. Check status bar shows "Ready"
3. Try `Agent Lucky: Check Status` command

---

## 📊 Verification Checklist

Run this to verify everything:
```powershell
cd "C:\Users\asus\Desktop\agent lucky"
.\quick-test.ps1
```

Should show:
- ✅ Extension files
- ✅ Backend running
- ✅ VS Code running

---

## 🎉 You're All Set!

**Extension:** ✅ Installed
**Backend:** ✅ Running at http://127.0.0.1:7777
**Commands:** ✅ Available in Command Palette

**Now reload VS Code and start coding with Agent Lucky!** 🍀

---

## 💻 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Command Palette | `Ctrl + Shift + P` |
| Show Agent Panel | `Ctrl + Shift + P` → "Agent Lucky: Show Panel" |
| Check Status | Click status bar item (bottom left) |

---

## 🌟 Next Steps

1. **Reload VS Code** (`Ctrl + Shift + P` → Reload Window)
2. **Open Agent Panel** (Command Palette → Agent Lucky: Show Panel)
3. **Enter your first prompt!**

Happy coding with Agent Lucky! 🚀🍀


