# Test model download status tracking

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Testing Model Download Status" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$backendUrl = "http://127.0.0.1:7777"

Write-Host "[1/5] Checking backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$backendUrl/health" -TimeoutSec 5
    Write-Host "  [OK] Backend is healthy" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Backend is not running!" -ForegroundColor Red
    Write-Host "  Start it with: cd backend; py main.py" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[2/5] Listing available models..." -ForegroundColor Yellow
try {
    $models = Invoke-RestMethod -Uri "$backendUrl/models/list" -TimeoutSec 5
    Write-Host "  Available models: $($models.available.Count)" -ForegroundColor Green
    foreach ($model in $models.available) {
        Write-Host "    - $($model.id): $($model.name) ($($model.size))" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [FAIL] Could not list models" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/5] Starting test download (codellama-7b-q4)..." -ForegroundColor Yellow
try {
    $body = @{
        model_id = "codellama-7b-q4"
    } | ConvertTo-Json

    $download = Invoke-RestMethod -Uri "$backendUrl/models/download" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 10

    Write-Host "  [OK] Download started!" -ForegroundColor Green
    Write-Host "  Status: $($download.status)" -ForegroundColor Gray
    Write-Host "  Model ID: $($download.model_id)" -ForegroundColor Gray
} catch {
    Write-Host "  [FAIL] Could not start download" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n[4/5] Checking download status (polling)..." -ForegroundColor Yellow
Write-Host "  This will check status every 2 seconds for 20 seconds..." -ForegroundColor Gray

for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 2
    
    try {
        $status = Invoke-RestMethod -Uri "$backendUrl/models/status/codellama-7b-q4" -TimeoutSec 5
        
        $statusEmoji = switch ($status.status) {
            "downloading" { "[DOWNLOADING]" }
            "completed" { "[COMPLETED]" }
            "error" { "[ERROR]" }
            default { "[INFO]" }
        }
        
        $progressStr = "$($status.progress)%"
        Write-Host "  $statusEmoji Status: $($status.status) | Progress: $progressStr | $($status.message)" -ForegroundColor Cyan
        
        if ($status.status -eq "completed") {
            Write-Host "`n  [SUCCESS] Download completed!" -ForegroundColor Green
            Write-Host "  Path: $($status.path)" -ForegroundColor Gray
            break
        }
        
        if ($status.status -eq "error") {
            Write-Host "`n  [ERROR] Download failed!" -ForegroundColor Red
            Write-Host "  Error: $($status.message)" -ForegroundColor Red
            break
        }
    } catch {
        Write-Host "  [FAIL] Could not check status" -ForegroundColor Red
    }
}

Write-Host "`n[5/5] Checking all active downloads..." -ForegroundColor Yellow
try {
    $allDownloads = Invoke-RestMethod -Uri "$backendUrl/models/downloads" -TimeoutSec 5
    
    if ($allDownloads.downloads.Count -eq 0) {
        Write-Host "  No active downloads" -ForegroundColor Gray
    } else {
        Write-Host "  Active downloads: $($allDownloads.downloads.Count)" -ForegroundColor Green
        foreach ($modelId in $allDownloads.downloads.Keys) {
            $dl = $allDownloads.downloads[$modelId]
            $progStr = "$($dl.progress)%"
            Write-Host "    - ${modelId}: $($dl.status) ($progStr)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  [FAIL] Could not check downloads" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Test Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n" -NoNewline
Write-Host "Now check VS Code:" -ForegroundColor Yellow
Write-Host "  1. Press Ctrl+Shift+P" -ForegroundColor White
Write-Host "  2. Type: Agent Lucky: Show Panel" -ForegroundColor White
Write-Host "  3. Look for the progress bar!" -ForegroundColor White
Write-Host "  4. Check status bar (bottom left) for progress" -ForegroundColor White
Write-Host ""

