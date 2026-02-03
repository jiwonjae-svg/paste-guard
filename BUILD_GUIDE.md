# 🚀 PasteGuardian Build Guide

Complete guide for building PasteGuardian.exe with embedded icon.

## Quick Build

### Method 1: Using build.bat (Recommended)
```batch
.\build.bat
```
Uses `build.spec` for consistent builds with all settings pre-configured.

### Method 2: Using build_quick.bat
```batch
.\build_quick.bat
```
Single command build without spec file.

### Method 3: One-Line Command
```batch
pyinstaller --clean --onefile --noconsole --name PasteGuardian --icon=icon.ico main.py
```

## Icon Configuration

### In build.spec
```python
exe = EXE(
    # ... other parameters ...
    icon='icon.ico'  # Path to icon file (relative to project root)
)
```

### In build.bat
```batch
pyinstaller --icon=icon.ico main.py
```

## Icon Not Showing? (Windows Cache Issue)

If the .exe icon doesn't appear after building, Windows is caching the old icon.

### Solution 1: Run PowerShell Script (Easiest)
```powershell
.\refresh_icon_cache.ps1
```

### Solution 2: Manual Commands

**CMD:**
```batch
del /f /s /q /a "%LocalAppData%\IconCache.db"
taskkill /f /im explorer.exe
start explorer.exe
```

**PowerShell:**
```powershell
Remove-Item "$env:LOCALAPPDATA\IconCache.db" -Force
Stop-Process -Name explorer -Force
Start-Process explorer
```

### Solution 3: Using ie4uinit
```batch
ie4uinit.exe -show
ie4uinit.exe -ClearIconCache
```

### Solution 4: Registry Refresh (Windows 11)
1. Right-click Desktop → Refresh (F5)
2. Log out and log back in
3. Restart computer (if all else fails)

## Build Files

| File | Description |
|------|-------------|
| `build.bat` | Main build script using build.spec |
| `build_quick.bat` | Quick single-command build |
| `build.spec` | PyInstaller configuration with icon |
| `refresh_icon_cache.ps1` | PowerShell script to refresh icon cache |
| `icon.ico` | Application icon (must be in project root) |

## Verification

After building, verify the icon is embedded:

1. **Check in Windows Explorer:**
   - Navigate to `PasteGuardian.exe`
   - Icon should display in file list
   - Icon should display in Properties dialog

2. **Check in Taskbar:**
   - Run the application
   - Icon should appear in taskbar when window is open

3. **Check in System Tray:**
   - Application icon should appear in system tray

## Troubleshooting

### Icon is default/blank
- Ensure `icon.ico` exists in project root
- Rebuild with `--clean` flag
- Clear icon cache (see above)

### Build fails with icon error
- Verify `icon.ico` path is correct
- Check icon file is valid .ico format
- Try absolute path: `--icon=C:\path\to\icon.ico`

### Icon works but still shows old icon
- **This is always a cache issue**
- Follow icon cache refresh steps above
- Worst case: Restart Windows

## Production Checklist

- [ ] `icon.ico` exists in project root
- [ ] Build completes without errors
- [ ] Icon visible in Windows Explorer
- [ ] Icon visible when running application
- [ ] Icon visible in system tray
- [ ] Test on clean Windows installation (no cache)

## Notes

- Icon is embedded in .exe at build time
- No external icon file needed for distribution
- Icon data also embedded in code as Base64 (utils/icon_data.py)
- Windows caches icons aggressively - refresh after every build
