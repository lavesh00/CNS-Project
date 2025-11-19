# Quick test to verify extension

Write-Host "`n=== Agent Lucky Extension Quick Test ===" -ForegroundColor Cyan

$extensionPath = "$env:USERPROFILE\.vscode\extensions\agent-lucky"

Write-Host "`n[1] Extension files..." -ForegroundColor Yellow
if (Test-Path $extensionPath) {
    Write-Host "  [OK] Extension directory exists" -ForegroundColor Green
    
    if (Test-Path "$extensionPath\package.json") {
        Write-Host "  [OK] package.json found" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] package.json missing!" -ForegroundColor Red
    }
    
    if (Test-Path "$extensionPath\extension.js") {
        Write-Host "  [OK] extension.js found" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] extension.js missing!" -ForegroundColor Red
    }
    
    if (Test-Path "$extensionPath\node_modules") {
        Write-Host "  [OK] node_modules found" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] node_modules missing! Run: cd $extensionPath; npm install" -ForegroundColor Red
    }
} else {
    Write-Host "  [FAIL] Extension not installed!" -ForegroundColor Red
    Write-Host "  Run: .\vscode-extension\install.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[2] Backend status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:7777/health" -TimeoutSec 2
    Write-Host "  [OK] Backend is running!" -ForegroundColor Green
    Write-Host "  Status: $($response.status)" -ForegroundColor Gray
} catch {
    Write-Host "  [WARN] Backend is offline" -ForegroundColor Yellow
    Write-Host "  Start it: cd backend; py main.py" -ForegroundColor Gray
}

Write-Host "`n[3] VS Code check..." -ForegroundColor Yellow
$vscodeRunning = Get-Process -Name "Code" -ErrorAction SilentlyContinue
if ($vscodeRunning) {
    Write-Host "  [OK] VS Code is running" -ForegroundColor Green
    Write-Host "  [NOTE] You may need to reload: Ctrl+Shift+P -> 'Developer: Reload Window'" -ForegroundColor Yellow
} else {
    Write-Host "  [INFO] VS Code is not running" -ForegroundColor Gray
    Write-Host "  Open it and press Ctrl+Shift+P" -ForegroundColor Gray
}

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Open VS Code (or reload if already open)" -ForegroundColor White
Write-Host "2. Press: Ctrl + Shift + P" -ForegroundColor White
Write-Host "3. Type: Agent Lucky" -ForegroundColor White
Write-Host "4. You should see 5 Agent Lucky commands!" -ForegroundColor White
Write-Host "`nIf you see the commands -> Extension works!`n" -ForegroundColor Green

