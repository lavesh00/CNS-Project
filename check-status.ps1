#!/usr/bin/env pwsh
# Complete status check for Agent Lucky

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent Lucky - Complete Status Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Backend Status
Write-Host "[1/5] Backend Status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:7777/health" -TimeoutSec 5
    Write-Host "  [OK] Backend is running!" -ForegroundColor Green
    Write-Host "  Service: $($health.service)" -ForegroundColor Gray
    Write-Host "  Version: $($health.version)" -ForegroundColor Gray
    Write-Host "  Status: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "  [FAIL] Backend is NOT running!" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n  Start it with:" -ForegroundColor Yellow
    Write-Host "  cd backend; py -m uvicorn main:app --host 127.0.0.1 --port 7777" -ForegroundColor White
    exit 1
}

# 2. Extension Status
Write-Host "`n[2/5] VS Code Extension..." -ForegroundColor Yellow
$extensions = code --list-extensions
if ($extensions -match "agent-lucky") {
    Write-Host "  [OK] Extension is installed" -ForegroundColor Green
    $extensionId = $extensions | Select-String "agent-lucky"
    Write-Host "  ID: $extensionId" -ForegroundColor Gray
} else {
    Write-Host "  [FAIL] Extension NOT installed" -ForegroundColor Red
    Write-Host "  Install it with:" -ForegroundColor Yellow
    Write-Host "  code --install-extension vscode-extension\agent-lucky-1.0.0.vsix" -ForegroundColor White
}

# 3. Models
Write-Host "`n[3/5] Available Models..." -ForegroundColor Yellow
try {
    $models = Invoke-RestMethod -Uri "http://127.0.0.1:7777/models/list" -TimeoutSec 5
    Write-Host "  [OK] Models endpoint working" -ForegroundColor Green
    Write-Host "  Installed: $($models.installed.Count)" -ForegroundColor Gray
    Write-Host "  Available: $($models.available.Count)" -ForegroundColor Gray
    
    if ($models.available.Count -gt 0) {
        Write-Host "`n  Available Models:" -ForegroundColor Cyan
        foreach ($model in $models.available) {
            Write-Host "    - $($model.id): $($model.name) ($($model.size))" -ForegroundColor White
        }
    }
} catch {
    Write-Host "  [FAIL] Could not get models" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Active Downloads
Write-Host "`n[4/5] Active Downloads..." -ForegroundColor Yellow
try {
    $downloads = Invoke-RestMethod -Uri "http://127.0.0.1:7777/models/downloads" -TimeoutSec 5
    
    if ($downloads.downloads.PSObject.Properties.Count -eq 0) {
        Write-Host "  [INFO] No active downloads" -ForegroundColor Gray
    } else {
        Write-Host "  [OK] Active downloads found: $($downloads.downloads.PSObject.Properties.Count)" -ForegroundColor Green
        foreach ($prop in $downloads.downloads.PSObject.Properties) {
            $modelId = $prop.Name
            $dl = $prop.Value
            $progStr = "$($dl.progress)%"
            Write-Host "    - ${modelId}: $($dl.status) ($progStr) - $($dl.message)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "  [FAIL] Could not check downloads" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Port Check
Write-Host "`n[5/5] Network Ports..." -ForegroundColor Yellow
$port7777 = Get-NetTCPConnection -LocalPort 7777 -ErrorAction SilentlyContinue
if ($port7777) {
    Write-Host "  [OK] Port 7777 is in use (backend listening)" -ForegroundColor Green
    Write-Host "  Process ID: $($port7777.OwningProcess)" -ForegroundColor Gray
    $process = Get-Process -Id $port7777.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "  Process Name: $($process.ProcessName)" -ForegroundColor Gray
    }
} else {
    Write-Host "  [WARN] Port 7777 is not in use" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$allGood = $true

if ($health.status -eq "healthy") {
    Write-Host "[OK] Backend: Running" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Backend: Not Running" -ForegroundColor Red
    $allGood = $false
}

if ($extensions -match "agent-lucky") {
    Write-Host "[OK] Extension: Installed" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Extension: Not Installed" -ForegroundColor Red
    $allGood = $false
}

if ($allGood) {
    Write-Host "`n[SUCCESS] Everything looks good!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. In VS Code: Ctrl+Shift+P" -ForegroundColor White
    Write-Host "  2. Type: Developer: Reload Window" -ForegroundColor White
    Write-Host "  3. Then: Ctrl+Shift+P -> 'Agent Lucky: Show Panel'" -ForegroundColor White
} else {
    Write-Host "`n[ISSUES FOUND] Please fix the issues above" -ForegroundColor Red
}

Write-Host ""

