# Agent Lucky VS Code Extension Installer

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Agent Lucky VS Code Extension Installer" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Get VS Code extensions directory
$extensionsDir = "$env:USERPROFILE\.vscode\extensions"

if (-not (Test-Path $extensionsDir)) {
    Write-Host "Creating VS Code extensions directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $extensionsDir -Force | Out-Null
}

# Extension target directory
$targetDir = "$extensionsDir\agent-lucky"

Write-Host "[1/4] Checking for existing installation..." -ForegroundColor Green

if (Test-Path $targetDir) {
    Write-Host "  Found existing installation. Removing..." -ForegroundColor Yellow
    Remove-Item -Path $targetDir -Recurse -Force
}

Write-Host "[2/4] Copying extension files..." -ForegroundColor Green

# Copy extension files
$sourceDir = $PSScriptRoot
Copy-Item -Path $sourceDir -Destination $targetDir -Recurse -Force

Write-Host "  Copied to: $targetDir" -ForegroundColor Gray

Write-Host "[3/4] Installing dependencies..." -ForegroundColor Green

# Install npm dependencies
Set-Location $targetDir
npm install --silent

Write-Host "[4/4] Installation complete!" -ForegroundColor Green

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  SUCCESS! Extension installed" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Reload VS Code (Ctrl+Shift+P -> 'Reload Window')"
Write-Host "  2. Ensure backend is running: py backend/main.py"
Write-Host "  3. Click Agent Lucky icon in Activity Bar"
Write-Host "  4. Or use: Ctrl+Shift+P -> 'Agent Lucky: Show Panel'`n"

Write-Host "Extension location: $targetDir`n" -ForegroundColor Gray

pause

