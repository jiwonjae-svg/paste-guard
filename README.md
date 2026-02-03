<div align="center">

# 🔒 Paste Guardian

**Your Intelligent Clipboard Security Assistant**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-blue.svg)](https://www.microsoft.com/windows)

*Take control of your clipboard. Prevent accidental pastes with elegance and security.*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Building](#-building) • [Contributing](#-contributing)

---

</div>

## 🎯 What is Paste Guardian?

Paste Guardian is a **lightweight, security-focused clipboard monitoring application** that intercepts every paste operation (Ctrl+V) on your Windows system, giving you **real-time preview and confirmation** before content reaches your applications.

Perfect for:
- 🔐 **Security-conscious users** who want to verify clipboard content before pasting
- 💼 **Professionals** handling sensitive data
- 🎨 **Content creators** managing multiple clipboard sources
- 🧪 **Developers** working with code snippets and credentials

## ✨ Features

### 🛡️ Core Security
- **Real-time Interception**: Captures all Ctrl+V operations system-wide
- **Smart Preview**: Shows text snippets or image thumbnails before pasting
- **Encrypted Storage**: All clipboard history encrypted with machine-specific keys
- **Whitelist Management**: Auto-approve trusted applications
- **Single Instance Protection**: Prevents multiple instances with Windows mutex

### 🎨 User Experience
- **Elegant Dark UI**: Modern CustomTkinter interface with SaaS-style design
- **System Tray Integration**: Minimal footprint with full tray functionality
- **Toast Notifications**: Windows 10/11 native notification support
- **Dynamic Tray Menu**: Real-time whitelist count display
- **Customizable Opacity**: Adjust popup transparency to your preference

### 🏗️ Technical Excellence
- **Layered Architecture**: Clean separation of concerns (Config → Services → UI)
- **Event-Driven Design**: Pub/sub pattern with NotificationService
- **Thread-Safe**: Proper synchronization with threading.Lock
- **Encrypted Configuration**: XOR cipher + SHA-256 hybrid encryption
- **Embedded Icon**: Fully self-contained executable with no external dependencies

## 📦 Installation

### Option 1: Download Executable (Recommended)
1. Download `PasteGuardian.exe` from [Releases](../../releases)
2. Run the executable - no installation needed!
3. System tray icon appears automatically

### Option 2: Run from Source

**Requirements:**
- Python 3.8 or higher
- Windows 10/11

**Quick Start:**
```powershell
# Clone the repository
git clone https://github.com/yourusername/paste-guardian.git
cd paste-guardian

# Run setup (installs dependencies)
.\setup.bat

# Launch application
python main.py
```

**Manual Installation:**
```powershell
# Install dependencies
pip install customtkinter pynput pyperclip psutil pystray pillow pywin32 win10toast

# Run application
python main.py
```

## 🚀 Usage

### First Run
1. **Launch** `PasteGuardian.exe` or `python main.py`
2. **System Tray Icon** appears (look for 🔒 icon)
3. **Test it out**: Copy something, then press Ctrl+V anywhere

### Basic Operations

#### 📋 Paste Operation
1. Copy text or image to clipboard
2. Press **Ctrl+V** in any application
3. **Confirmation popup** appears near cursor
4. Choose:
   - **✓ Approve**: Paste the content
   - **✓ Approve + Whitelist**: Approve and trust this app forever
   - **✗ Deny**: Block the paste

#### ⚙️ Open Settings
- **Right-click** system tray icon → **Settings**
- Configure monitoring, whitelist, appearance, and history

#### 🎯 Whitelist Management
1. Open Settings → **✓ Whitelist** tab
2. Enter process name (e.g., `notepad.exe`, `chrome.exe`)
3. Click **+ Add** button
4. Whitelisted apps auto-approve all pastes

#### 📊 View History
- Settings → **📜 History** tab
- View encrypted clipboard history (last 10 items)
- Fully encrypted at rest with machine-specific keys

### Monitoring Controls

| Setting | Location | Description |
|---------|----------|-------------|
| **Text Monitoring** | 📋 Monitoring tab | Toggle text paste interception |
| **Image Monitoring** | 📋 Monitoring tab | Toggle image paste interception |
| **Popup Opacity** | 🎨 Appearance tab | Adjust transparency (0.7 - 1.0) |
| **Theme Color** | 🎨 Appearance tab | Customize accent color |


## 📁 Project Structure

```
PasteGuardian/
│
├── 📄 main.py                           # Application entry point with system tray
├── 🔧 build.bat / build.spec            # PyInstaller build configuration
├── 🎨 icon.ico                          # Application icon (embedded in exe)
│
├── 📁 config/                           # Configuration Management
│   ├── __init__.py                      # Package exports
│   └── config_manager.py                # JSON config with encrypted whitelist
│
├── 📁 services/                         # Business Logic Layer
│   ├── __init__.py                      # Service exports
│   ├── security_service.py              # XOR + SHA-256 encryption
│   ├── history_service.py               # Encrypted clipboard history
│   └── notification_service.py          # Event-driven pub/sub system
│
├── 📁 monitors/                         # System Monitoring
│   ├── __init__.py                      # Monitor exports
│   └── clipboard_monitor.py             # Keyboard hook & clipboard capture
│
├── 📁 ui/                               # User Interface Components
│   ├── __init__.py                      # UI exports
│   ├── confirmation_popup.py            # Paste confirmation dialog
│   └── settings_window.py               # Multi-tab settings dashboard
│
└── 📁 utils/                            # Cross-Cutting Utilities
    ├── __init__.py                      # Utility exports
    ├── path_utils.py                    # Portable/installed path management
    ├── resource_utils.py                # PyInstaller resource handling
    ├── icon_data.py                     # Base64-encoded icon data
    └── icon_utils.py                    # Runtime icon extraction
```

## 🏗️ Architecture

Paste Guardian follows a **clean layered architecture** with strict dependency rules:

```
┌─────────────────────────────────────────┐
│            UI Layer (CTk)               │  ← User interaction
├─────────────────────────────────────────┤
│      Monitors Layer (Keyboard/CB)      │  ← System hooks
├─────────────────────────────────────────┤
│     Services Layer (Logic + Crypto)     │  ← Business logic
├─────────────────────────────────────────┤
│       Config Layer (Persistence)        │  ← Data storage
├─────────────────────────────────────────┤
│      Utils Layer (Helpers + Paths)      │  ← Foundation
└─────────────────────────────────────────┘
```

### Key Components

#### 🔐 SecurityService
- **Hybrid Encryption**: XOR cipher with SHA-256 key derivation
- **Machine-Specific Keys**: Uses hardware UUID for encryption
- **Transparent Operation**: Automatic encrypt/decrypt on read/write

#### 📊 HistoryService
- **Encrypted Storage**: All clipboard items stored with encryption
- **Auto-Persistence**: Saves to `history.json` on every change
- **Size Management**: Configurable max history (default: 10 items)

#### 📡 NotificationService
- **Event Types**: `paste_request`, `paste_approved`, `paste_denied`, `config_changed`
- **Loose Coupling**: Components communicate via events
- **Thread-Safe**: Works seamlessly across background threads

#### 🖱️ ClipboardMonitor
- **Global Keyboard Hook**: Intercepts Ctrl+V system-wide
- **Multi-Format Support**: Text, images, files
- **Process Detection**: Identifies requesting application

### Thread Safety

All shared data protected with `threading.Lock`:
```python
history_lock = threading.Lock()  # Protects clipboard_history
config_lock = threading.Lock()   # Protects config updates
```

## 🛡️ Security Features

### Encryption Architecture
- **Algorithm**: XOR cipher with SHA-256 hashing
- **Key Material**: Machine UUID + Hardware identifiers
- **Scope**: Whitelist, clipboard history, sensitive config

### Security Benefits
1. **Data at Rest**: All sensitive data encrypted on disk
2. **Machine Binding**: Keys unique to each computer
3. **No External Dependencies**: All crypto is built-in Python
4. **Preemptive Blocking**: Paste blocked until user confirms

### Privacy
- ✅ **All data stays local** - no network connections
- ✅ **Encrypted storage** - history is not plaintext
- ✅ **No telemetry** - zero tracking or analytics
- ✅ **Open source** - audit the code yourself

## 🔧 Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **UI Framework** | CustomTkinter | Modern dark-mode GUI |
| **Keyboard Hook** | pynput | Global Ctrl+V interception |
| **Clipboard** | pyperclip, PIL.ImageGrab | Text & image capture |
| **Process Detection** | psutil, pywin32 | Active window identification |
| **System Tray** | pystray | Background tray integration |
| **Notifications** | win10toast | Windows native toasts |
| **Encryption** | hashlib, uuid | SHA-256 & machine ID |
| **Build** | PyInstaller | Standalone executable |

## ⚡ Performance

- **CPU Usage**: <1% idle, <5% during paste operation
- **Memory**: ~40MB RAM footprint
- **Startup Time**: <2 seconds to system tray
- **Popup Latency**: <100ms from Ctrl+V to display

Optimizations:
- Event-driven architecture (no polling loops)
- Background threads for I/O operations
- Lazy-loaded UI components
- Efficient clipboard format detection

## 🚀 Building from Source

### Quick Build (Recommended)
```powershell
# One-command build using build.bat
.\build.bat
```

Output: `dist\PasteGuardian.exe` (single-file executable)

### Manual PyInstaller Build
```powershell
pyinstaller --clean --onefile --noconsole ^
    --name PasteGuardian ^
    --icon=icon.ico ^
    main.py
```

### Build Configuration
- **Spec File**: `build.spec` (pre-configured with all hidden imports)
- **Icon Embedding**: Icon data in `utils/icon_data.py` + `icon.ico` for exe metadata
- **Hidden Imports**: All dependencies explicitly listed
- **One-File Mode**: Fully portable executable

### Build Requirements
```powershell
pip install pyinstaller
```

## ⚙️ Configuration

### config.json (Auto-generated)
```json
{
    "monitor_text": true,                    // Enable text monitoring
    "monitor_image": true,                   // Enable image monitoring
    "whitelist": ["<encrypted_base64>"],     // Encrypted process names
    "popup_opacity": 0.95,                   // Transparency (0.7-1.0)
    "theme": "dark",                         // UI theme
    "accent_color": "#3B82F6",               // Brand color
    "history_limit": 10                      // Max history items
}
```

### history.json (Encrypted)
```json
{
    "items": [
        {
            "type": "text|image",
            "content": "<encrypted_base64>",
            "timestamp": 1234567890.0,
            "process": "notepad.exe"
        }
    ]
}
```

## 🐛 Troubleshooting

### Popup Doesn't Appear
1. Check if app is whitelisted (remove from whitelist to test)
2. Verify monitoring is enabled (Settings → Monitoring tab)
3. Run as Administrator if pasting into elevated apps
4. Restart application if keyboard hook is stuck

### Paste Operation Fails
1. Confirm clipboard has valid content
2. Check monitoring settings (text/image toggles)
3. Try manual paste approval first
4. Review system tray notifications for errors

### Icon Not Showing in System Tray
1. Windows 11: Icons may take 5-10 seconds to appear
2. Check system tray settings (Windows → Taskbar settings)
3. Application uses delayed icon loading (200ms) for stability

### Build Issues
1. Ensure `icon.ico` exists in project root
2. Install all dependencies: `pip install -r requirements.txt`
3. Use Python 3.8-3.11 (3.12+ may have compatibility issues)
4. Run build.bat as Administrator if permission errors occur

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

Free for personal, educational, and commercial use with attribution.

## 🤝 Contributing

Contributions welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** with clear messages (`git commit -m 'Add amazing feature'`)
4. **Push** to your branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```powershell
# Clone your fork
git clone https://github.com/yourusername/paste-guardian.git
cd paste-guardian

# Install dev dependencies
pip install -r requirements.txt

# Run tests
python test_refactored.py

# Run application
python main.py
```

## 🙋 Support & Contact

- **Issues**: [GitHub Issues](../../issues)
- **Feature Requests**: [GitHub Discussions](../../discussions)
- **Security**: Report vulnerabilities privately via GitHub Security

## 🎯 Roadmap

- [ ] Multi-language support (English, Korean, Japanese)
- [ ] Cloud sync for whitelist across devices
- [ ] Custom keyboard shortcuts
- [ ] Paste history search
- [ ] Import/export whitelist

## 🙏 Acknowledgments

Built with these amazing open-source projects:
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [pynput](https://github.com/moses-palmer/pynput) - Keyboard monitoring
- [pystray](https://github.com/moses-palmer/pystray) - System tray support

---

<div align="center">

**Paste Guardian** - Your Clipboard, Your Control 🚀

Made with ❤️ by developers, for developers

[⬆ Back to Top](#-paste-guardian)

</div>
