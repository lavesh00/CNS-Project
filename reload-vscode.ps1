#!/usr/bin/env pwsh
# Force reload VS Code to recognize extension

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Fixing Agent Lucky Extension" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$extensionPath = "$env:USERPROFILE\.vscode\extensions\agent-lucky"

Write-Host "[1/3] Checking extension installation..." -ForegroundColor Green
if (Test-Path $extensionPath) {
    Write-Host "  Found at: $extensionPath" -ForegroundColor Gray
} else {
    Write-Host "  ERROR: Extension not found!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/3] Verifying package.json..." -ForegroundColor Green
$packagePath = Join-Path $extensionPath "package.json"
if (Test-Path $packagePath) {
    $package = Get-Content $packagePath | ConvertFrom-Json
    Write-Host "  Name: $($package.name)" -ForegroundColor Gray
    Write-Host "  Version: $($package.version)" -ForegroundColor Gray
    Write-Host "  Commands: $($package.contributes.commands.Count)" -ForegroundColor Gray
} else {
    Write-Host "  ERROR: package.json not found!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/3] Opening VS Code..." -ForegroundColor Green

# Try to find VS Code executable
$vscodeExecutable = $null
$possiblePaths = @(
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
    "$env:ProgramFiles\Microsoft VS Code\Code.exe",
    "$env:ProgramFiles(x86)\Microsoft VS Code\Code.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $vscodeExecutable = $path
        break
    }
}

if ($vscodeExecutable) {
    Write-Host "  Starting VS Code..." -ForegroundColor Gray
    Start-Process $vscodeExecutable -ArgumentList "--disable-extensions", "--install-extension", $extensionPath
    Start-Sleep -Seconds 2
    Start-Process $vscodeExecutable
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  VS Code Opened!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. VS Code should now be open"
    Write-Host "  2. Press Ctrl+Shift+P"
    Write-Host "  3. Type: Developer: Reload Window"
    Write-Host "  4. Look for Agent Lucky in:"
    Write-Host "     - Command Palette (Ctrl+Shift+P -> 'Agent Lucky')"
    Write-Host "     - Status Bar (bottom right)"
    Write-Host "     - Activity Bar (left sidebar - rocket icon)`n"
    
} else {
    Write-Host "`n  Could not find VS Code executable." -ForegroundColor Yellow
    Write-Host "  Please manually:" -ForegroundColor Yellow
    Write-Host "  1. Open VS Code"
    Write-Host "  2. Press Ctrl+Shift+P"
    Write-Host "  3. Type: Developer: Reload Window"
    Write-Host "  4. Check for 'Agent Lucky' in commands`n"
}

