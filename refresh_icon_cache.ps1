# ==============================================================================
# Windows Icon Cache Refresh Utility
# ==============================================================================
# Use this script if the icon doesn't update after building a new .exe file
# ==============================================================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Windows Icon Cache Refresh Tool" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Method 1: Delete IconCache.db files
Write-Host "[1/4] Deleting icon cache database..." -ForegroundColor Yellow
$iconCachePath = "$env:LOCALAPPDATA\IconCache.db"
if (Test-Path $iconCachePath) {
    Remove-Item -Path $iconCachePath -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ IconCache.db deleted" -ForegroundColor Green
} else {
    Write-Host "  ℹ IconCache.db not found" -ForegroundColor Gray
}

# Method 2: Delete all icon cache files (Windows 10/11)
Write-Host "[2/4] Deleting thumbnail cache..." -ForegroundColor Yellow
$thumbCachePath = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer"
if (Test-Path $thumbCachePath) {
    Get-ChildItem -Path $thumbCachePath -Filter "iconcache*" -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Deleted: $($_.Name)" -ForegroundColor Green
    }
    Get-ChildItem -Path $thumbCachePath -Filter "thumbcache*" -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Deleted: $($_.Name)" -ForegroundColor Green
    }
}

# Method 3: Clear icon cache using ie4uinit
Write-Host "[3/4] Clearing icon cache with ie4uinit..." -ForegroundColor Yellow
try {
    Start-Process -FilePath "ie4uinit.exe" -ArgumentList "-show" -WindowStyle Hidden -Wait
    Start-Process -FilePath "ie4uinit.exe" -ArgumentList "-ClearIconCache" -WindowStyle Hidden -Wait
    Write-Host "  ✓ Icon cache cleared" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ ie4uinit.exe not available" -ForegroundColor Yellow
}

# Method 4: Restart Windows Explorer
Write-Host "[4/4] Restarting Windows Explorer..." -ForegroundColor Yellow
try {
    Stop-Process -Name explorer -Force -ErrorAction Stop
    Start-Sleep -Seconds 2
    Start-Process explorer
    Write-Host "  ✓ Windows Explorer restarted" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Failed to restart Explorer" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Icon cache refresh complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your .exe icon should now be visible." -ForegroundColor White
Write-Host "If not, try logging out and back in." -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to exit"
