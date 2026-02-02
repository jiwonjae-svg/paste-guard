# 🔒 Paste Guardian

A security program that intercepts clipboard paste operations and requests user confirmation.

## ✨ Key Features

- **Real-time Monitoring**: Monitors and intercepts Ctrl+V keypresses in the background
- **Elegant Confirmation Popup**: Dark mode floating window near mouse cursor
- **Text Preview**: Preview the beginning of text before pasting
- **Image Preview**: Display thumbnail of images before pasting
- **Whitelist**: Automatically allow trusted applications
- **Detailed Settings**: Text/Image monitoring toggle, opacity adjustment, and more

## 🎨 Design

- **Framework**: CustomTkinter
- **Theme**: Dark mode (#1E1E1E background)
- **Accent Color**: Soft Blue (#3B82F6)
- **UI Style**: SaaS dashboard style settings window

## 📦 Installation

### 1. Requirements

- Python 3.8 or higher
- Windows 10/11

### 2. Install Libraries

```powershell
pip install -r requirements.txt
```

### 3. Run

```powershell
python main.py
```

## 🚀 Usage

### First Run

1. Run `main.py` to create a system tray icon
2. Automatically monitors clipboard in the background
3. Press Ctrl+V to see the confirmation popup

### Open Settings Window

- Right-click the system tray icon and select "Settings"

### Add to Whitelist

1. Select "✓ Whitelist" tab in settings window
2. Enter process name (e.g., `notepad.exe`)
3. Click "+ Add" button

### Monitoring Settings

- Toggle text/image monitoring in "📋 Monitoring" tab

### Adjust Opacity

- Adjust popup opacity with slider in "🎨 Appearance" tab

## 📁 Project Structure

```
Project-Warning/
│
├── main.py                      # Main application entry point
├── config.json                  # Configuration file (auto-generated)
├── requirements.txt             # Required libraries
│
├── config/                      # Configuration layer
│   ├── config_manager.py        # Configuration management
│   └── __init__.py
│
├── services/                    # Business logic layer
│   ├── security_service.py      # Encryption/decryption service
│   ├── history_service.py       # Clipboard history with encryption
│   ├── notification_service.py  # Event notification system
│   └── __init__.py
│
├── monitors/                    # System monitoring layer
│   ├── clipboard_monitor.py     # Clipboard monitoring
│   └── __init__.py
│
├── ui/                          # User interface layer
│   ├── confirmation_popup.py    # Confirmation popup UI
│   ├── settings_window.py       # Settings window UI
│   └── __init__.py
│
├── utils/                       # Utility layer
│   ├── path_utils.py            # Path management utilities
│   └── __init__.py
│
└── core/                        # Core functionality (reserved)
    └── __init__.py
```

## 🏗️ Architecture

The application follows a **layered architecture** with clear separation of concerns:

- **Config Layer**: Configuration management and persistence
- **Services Layer**: Core business logic (security, history, notifications)
- **Monitors Layer**: System-level monitoring (clipboard, keyboard)
- **UI Layer**: User interface components
- **Utils Layer**: Cross-cutting utilities (path management, helpers)
- **Core Layer**: Reserved for future core functionality

### Key Services

#### SecurityService
- **XOR Cipher**: Machine-specific encryption using hardware identifiers
- **SHA-256 Key Derivation**: Secure key generation from machine UUID
- **Automatic Encryption**: Transparent encryption for sensitive data

#### HistoryService
- **Encrypted Storage**: All clipboard history encrypted at rest
- **Auto-save**: Automatic persistence to `history.json`
- **Limit Management**: Configurable history size (default: 10 items)

#### NotificationService
- **Event-Driven**: Pub/sub pattern for loose coupling
- **System Events**: `config_changed`, `history_updated`, `whitelist_modified`
- **Asynchronous**: Non-blocking event dispatch

## ⚙️ Configuration File (config.json)

Automatically created on first run. **Whitelist is encrypted** for security.

```json
{
    "monitor_text": true,
    "monitor_image": true,
    "whitelist": ["<encrypted_data>"],
    "popup_opacity": 0.95,
    "theme": "dark",
    "accent_color": "#3B82F6"
}
```

## 🛡️ Security Features

- **Encrypted History**: All clipboard history encrypted with machine-specific keys
- **Secure Whitelist**: Application whitelist stored with encryption
- **XOR + SHA-256**: Hybrid encryption combining XOR cipher with SHA-256 hashing
- **Machine-Specific Keys**: Encryption keys derived from hardware UUID
- **Preemptive Blocking**: Blocks all paste attempts until user confirms
- **Granular Control**: Manage trusted processes and content types

## 🔧 Technology Stack

- **UI Framework**: CustomTkinter
- **Keyboard Hooking**: pynput
- **Clipboard Access**: pyperclip, PIL (ImageGrab)
- **Process Management**: psutil, pywin32
- **System Tray**: pystray
- **Encryption**: hashlib (SHA-256), uuid (machine ID)
- **Architecture**: Layered architecture with dependency injection

## ⚡ Performance Optimization

- Minimized CPU usage with efficient event-driven architecture
- Non-blocking monitoring via background threads
- Safe multithreading using UI queue
- Service-oriented design for scalability
- Lazy loading and on-demand resource allocation

## 🛡️ Security Features

- **Encrypted History**: All clipboard history encrypted with machine-specific keys
- **Secure Whitelist**: Application whitelist stored with encryption
- **XOR + SHA-256**: Hybrid encryption combining XOR cipher with SHA-256 hashing
- **Machine-Specific Keys**: Encryption keys derived from hardware UUID
- **Preemptive Blocking**: Blocks all paste attempts until user confirms
- **Granular Control**: Manage trusted processes and content types

## 🚀 Building Executable

Create a standalone `.exe` file:

```powershell
# Quick build
.\build.bat

# Manual build with PyInstaller
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

The executable will be in the `dist/` folder.

## 📝 Notes

1. **Administrator Rights**: May require administrator rights for some system applications
2. **Background Execution**: Program runs in system tray; right-click tray icon to exit
3. **Keyboard Hooking**: Security software may block keyboard hooking

## 🐛 Troubleshooting

### Popup doesn't appear

- Check if the process is in the whitelist
- Verify monitoring settings are enabled
- Try running with administrator rights

### Paste doesn't work

- Verify correct data is in clipboard
- Try restarting the program

## 📜 License

This project is free to use for educational and personal purposes.

## 🙋 Contact

Please submit an issue if you encounter problems or have feature suggestions.

---

**Paste Guardian** - Elevate your clipboard security! 🚀
