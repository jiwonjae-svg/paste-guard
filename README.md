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
├── main.py                      # Main application
├── config_manager.py            # Configuration management
├── clipboard_monitor.py         # Clipboard monitoring
├── confirmation_popup.py        # Confirmation popup UI
├── settings_window.py           # Settings window UI
├── requirements.txt             # Required libraries
├── config.json                  # Configuration file (auto-generated)
└── README.md                    # This file
```

## ⚙️ Configuration File (config.json)

Automatically created on first run.

```json
{
    "monitor_text": true,
    "monitor_image": true,
    "whitelist": [
        "notepad.exe",
        "code.exe"
    ],
    "popup_opacity": 0.95,
    "theme": "dark",
    "accent_color": "#3B82F6"
}
```

## 🔧 Technology Stack

- **UI Framework**: CustomTkinter
- **Keyboard Hooking**: pynput
- **Clipboard Access**: pyperclip, PIL (ImageGrab)
- **Process Management**: psutil, pywin32
- **System Tray**: pystray

## ⚡ Performance Optimization

- Minimized CPU usage with efficient event-driven architecture
- Non-blocking monitoring via background threads
- Safe multithreading using UI queue

## 🛡️ Security Features

- Preemptively blocks all paste attempts
- Performs actual paste only after user confirmation
- Manage trusted processes via whitelist
- Granular control by content type

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
