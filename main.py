"""
Paste Guardian - Main Application
Clipboard paste security program
"""
import customtkinter as ctk
import threading
import sys
import os
import win32event
import win32api
import winerror
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import queue
from win10toast import ToastNotifier
from config.config_manager import ConfigManager
from monitors.clipboard_monitor import ClipboardMonitor
from ui.confirmation_popup import ConfirmationPopup
from ui.settings_window import SettingsWindow
from utils.icon_utils import get_icon_path, get_icon_image


class PasteGuardian:
    """Main application class"""
    
    def __init__(self):
        # Configuration manager
        self.config = ConfigManager()
        
        # Clipboard monitor
        self.monitor = ClipboardMonitor(self.on_paste_request)
        
        # UI queue (for UI updates from background threads)
        self.ui_queue = queue.Queue()
        
        # System tray icon
        self.tray_icon = None
        
        # Settings window
        self.settings_window = None
        
        # Currently displayed confirmation popup
        self.current_popup = None
        
        # Main event loop (hidden window)
        self.root = None
        
        # Clipboard history (stores recent 10 items)
        self.clipboard_history = []
        
        # Thread synchronization locks
        self.history_lock = threading.Lock()
        self.config_lock = threading.Lock()
        
        # Toast notifier for Windows notifications
        self.toast = ToastNotifier()
        
        # Load saved history
        self._load_history()
        
    def start(self):
        """Start the application"""
        print("=" * 50)
        print("🔒 Paste Guardian Starting")
        print("=" * 50)
        print("✓ Clipboard monitoring activated")
        print("✓ Creating system tray icon...")
        print("\n[Instructions]")
        print("- Check the icon in system tray (bottom right of taskbar)")
        print("- Right-click the icon and select 'Settings'")
        print("- Press Ctrl+V to see confirmation popup")
        print("=" * 50)
        
        # Create hidden customtkinter root window
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide the window
        
        # Set window icon with delayed application for Windows 11 stability
        self.root.after(200, self._apply_window_icon)
        
        # Start clipboard monitoring
        self.monitor.start()
        
        # Start system tray icon (in separate thread)
        tray_thread = threading.Thread(target=self._start_tray_icon, daemon=True)
        tray_thread.start()
        
        # Process UI queue
        self._process_ui_queue()
        
        # Check and show first run welcome dialog
        self.root.after(1000, self._check_first_run)
        
        # Main loop
        self.root.mainloop()
    
    def _start_tray_icon(self):
        """Start system tray icon"""
        # Load icon from embedded data
        icon_image = get_icon_image()
        
        # Use embedded icon if available, otherwise create default
        if icon_image is None:
            print("[Tray] Using fallback icon")
            icon_image = self._create_tray_icon()
        else:
            # Resize to 64x64 for tray icon
            try:
                icon_image = icon_image.resize((64, 64), Image.Resampling.LANCZOS)
                print("[Tray] ✓ Embedded icon loaded successfully")
            except Exception as e:
                print(f"[Tray] Resize failed: {e}, using fallback")
                icon_image = self._create_tray_icon()
        
        # Create dynamic menu with whitelist count
        menu = self._create_tray_menu()
        
        # Create tray icon
        self.tray_icon = Icon(
            "PasteGuardian",
            icon_image,
            "Paste Guardian - Active",
            menu
        )
        
        # Run tray icon
        self.tray_icon.run()
    
    def _create_tray_menu(self):
        """Create dynamic tray menu with whitelist count"""
        with self.config_lock:
            whitelist_count = len(self.config.get_whitelist())
        
        return Menu(
            MenuItem(f"Whitelist: {whitelist_count} apps", None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Settings", self._show_settings),
            MenuItem("Exit", self._quit_application)
        )
    
    def _update_tray_menu(self):
        """Update tray menu dynamically (e.g., when whitelist changes)"""
        if self.tray_icon:
            self.tray_icon.menu = self._create_tray_menu()
            self.tray_icon.update_menu()
    
    def _create_tray_icon(self):
        """Create tray icon image (fallback)"""
        # Create simple icon (64x64)
        img = Image.new('RGB', (64, 64), color='#3B82F6')
        draw = ImageDraw.Draw(img)
        
        # Draw lock icon (simple version)
        draw.rectangle([20, 28, 44, 50], fill='white', outline='white')
        draw.ellipse([24, 20, 40, 36], fill='#3B82F6', outline='white', width=3)
        
        return img
    
    def _check_first_run(self):
        """Check if this is the first run and show welcome dialog"""
        try:
            is_first_run = self.config.get("first_run", True)
            
            if is_first_run:
                print("[First Run] Showing welcome dialog...")
                self._show_welcome_dialog()
                # Mark as not first run
                self.config.set("first_run", False)
                print("[First Run] Marked as completed")
        except Exception as e:
            print(f"[First Run] Error checking first run: {e}")
    
    def _show_welcome_dialog(self):
        """Show welcome dialog for first-time users"""
        try:
            # Create welcome dialog window
            welcome = ctk.CTkToplevel(self.root)
            welcome.title("Welcome to Paste Guardian")
            welcome.geometry("480x320")
            welcome.resizable(False, False)
            
            # Apply icon
            try:
                icon_path = get_icon_path()
                if icon_path and os.path.exists(icon_path):
                    welcome.iconbitmap(icon_path)
            except:
                pass
            
            # Center window on screen
            welcome.update_idletasks()
            width = welcome.winfo_width()
            height = welcome.winfo_height()
            x = (welcome.winfo_screenwidth() // 2) - (width // 2)
            y = (welcome.winfo_screenheight() // 2) - (height // 2)
            welcome.geometry(f"{width}x{height}+{x}+{y}")
            
            # Make window always on top
            welcome.attributes('-topmost', True)
            
            # Main container
            container = ctk.CTkFrame(welcome, fg_color="#1E1E1E")
            container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title with icon emoji
            title = ctk.CTkLabel(
                container,
                text="🔒 Welcome to Paste Guardian!",
                font=("Segoe UI", 24, "bold"),
                text_color="#3B82F6"
            )
            title.pack(pady=(10, 20))
            
            # Message content
            messages = [
                "✓ Running in System Tray",
                "   Look for the 🔒 icon in your taskbar",
                "",
                "✓ Press Ctrl+V Anywhere",
                "   Preview clipboard content before pasting",
                "",
                "✓ Customize Settings",
                "   Right-click tray icon → Settings",
                "",
                "🔐 Your data is encrypted and stays local"
            ]
            
            message_frame = ctk.CTkFrame(container, fg_color="#2A2A2A", corner_radius=10)
            message_frame.pack(fill="both", expand=True, pady=(0, 15))
            
            for msg in messages:
                msg_label = ctk.CTkLabel(
                    message_frame,
                    text=msg,
                    font=("Segoe UI", 13 if msg.startswith(("✓", "🔐")) else 12),
                    text_color="#FFFFFF" if msg.startswith(("✓", "🔐")) else "#A0A0A0",
                    anchor="w"
                )
                msg_label.pack(anchor="w", padx=20, pady=2)
            
            # Button frame
            button_frame = ctk.CTkFrame(container, fg_color="transparent")
            button_frame.pack(fill="x", pady=(10, 0))
            
            # Got it button
            def close_dialog():
                welcome.destroy()
                print("[First Run] Welcome dialog closed")
            
            got_it_btn = ctk.CTkButton(
                button_frame,
                text="Got it! ✓",
                font=("Segoe UI", 14, "bold"),
                fg_color="#3B82F6",
                hover_color="#2563EB",
                height=40,
                command=close_dialog
            )
            got_it_btn.pack(side="right")
            
            # Bind ESC key to close
            welcome.bind("<Escape>", lambda e: close_dialog())
            
            # Focus window
            welcome.focus_force()
            
        except Exception as e:
            print(f"[First Run] Error showing welcome dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def _apply_window_icon(self):
        """Apply icon to window with error handling (Windows 11 compatible)"""
        try:
            # Get icon path from embedded data
            icon_path = get_icon_path()
            
            if not icon_path:
                print("[Icon] ✗ Failed to get icon path")
                return
            
            # Verify file existence
            if not os.path.exists(icon_path):
                print(f"[Icon] ✗ Temporary icon file not found: {icon_path}")
                return
            
            # Check file size
            file_size = os.path.getsize(icon_path)
            if file_size == 0:
                print(f"[Icon] ✗ Empty icon file: {icon_path}")
                return
            
            print(f"[Icon] ✓ Icon file verified ({file_size} bytes)")
            
            # Apply icon to root window
            self.root.iconbitmap(icon_path)
            print(f"[Icon] ✓ Successfully applied to main window")
            
        except Exception as e:
            print(f"[Icon] ✗ Failed to apply icon: {e}")
            import traceback
            traceback.print_exc()
    
    def _process_ui_queue(self):
        """Process UI queue (check periodically)"""
        try:
            while not self.ui_queue.empty():
                callback = self.ui_queue.get_nowait()
                callback()
        except queue.Empty:
            pass
        
        # Check again every 100ms
        if self.root:
            self.root.after(100, self._process_ui_queue)
    
    def on_paste_request(self, clipboard_data: dict, process_name: str):
        """Paste request callback"""
        print(f"\n[Paste Request Received]")
        print(f"- Process: {process_name}")
        print(f"- Data Type: {clipboard_data.get('type')}")
        
        # Check whitelist
        with self.config_lock:
            is_whitelisted = process_name in self.config.get_whitelist()
        
        if is_whitelisted:
            print(f"✓ Whitelisted process: {process_name} - Auto allowed")
            # Record whitelisted paste to history
            self._add_to_history(clipboard_data, process_name)
            self._allow_paste(clipboard_data)
            return
        
        # Check monitoring status by content type
        content_type = clipboard_data.get("type")
        if not self.config.is_monitoring_enabled(content_type):
            print(f"✓ {content_type} monitoring disabled - Auto allowed")
            # Record to history even when monitoring is disabled
            self._add_to_history(clipboard_data, process_name)
            self._allow_paste(clipboard_data)
            return
        
        print("→ Showing confirmation popup...")
        
        # Show toast notification for blocked paste attempt
        self._show_toast_notification(process_name, content_type)
        
        # Show confirmation popup (add to UI queue)
        def show_popup():
            self._show_confirmation_popup(clipboard_data, process_name)
        
        self.ui_queue.put(show_popup)
    
    def _show_toast_notification(self, process_name: str, content_type: str):
        """Show Windows toast notification for paste detection"""
        def show_toast():
            try:
                app_name = process_name.replace('.exe', '').title()
                icon_path = get_icon_path()
                
                self.toast.show_toast(
                    "Paste Guardian",
                    f"Paste detected in {app_name}\nType: {content_type}",
                    icon_path=icon_path,
                    duration=3,
                    threaded=True
                )
            except Exception as e:
                print(f"Toast notification error: {e}")
        
        # Run in separate thread to avoid blocking
        threading.Thread(target=show_toast, daemon=True).start()
    
    def _show_confirmation_popup(self, clipboard_data: dict, process_name: str):
        """Show confirmation popup (must run in main thread)"""
        print("Creating confirmation popup...")
        
        # Add to UI queue if not in main thread
        if threading.current_thread() != threading.main_thread():
            print("Called from background thread - forwarding to UI queue")
            self.ui_queue.put(lambda: self._show_confirmation_popup(clipboard_data, process_name))
            return
        
        if self.current_popup:
            self.current_popup.close()
        
        opacity = self.config.get("popup_opacity", 0.95)
        
        try:
            self.current_popup = ConfirmationPopup(
                clipboard_data=clipboard_data,
                process_name=process_name,
                on_confirm=lambda data: self._on_popup_confirm(data, process_name),
                on_always_allow=lambda data: self._on_popup_always_allow(data, process_name),
                on_cancel=self._on_popup_cancel,
                opacity=opacity
            )
            
            self.current_popup.show()
            print("✓ Confirmation popup displayed")
        except Exception as e:
            print(f"✗ Popup display error: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_popup_confirm(self, clipboard_data: dict, process_name: str):
        """Popup confirm button clicked"""
        print("Paste approved")
        
        # Add to history (at actual paste time)
        self._add_to_history(clipboard_data, process_name)
        
        # Close popup and perform paste
        self._allow_paste_with_focus(clipboard_data)
        self.current_popup = None
    
    def _on_popup_always_allow(self, clipboard_data: dict, process_name: str):
        """Popup 'Always Allow' button clicked - add to whitelist"""
        print(f"Added to whitelist: {process_name}")
        
        # Add to whitelist (thread-safe)
        with self.config_lock:
            self.config.add_to_whitelist(process_name)
        
        # Update tray menu to reflect new whitelist count
        self._update_tray_menu()
        
        # Add to history
        self._add_to_history(clipboard_data, process_name)
        
        # Perform paste
        self._allow_paste_with_focus(clipboard_data)
        self.current_popup = None
    
    def _on_popup_cancel(self):
        """Popup cancel button clicked"""
        print("Paste denied")
        self.current_popup = None
    
    def _allow_paste(self, clipboard_data: dict, process_name: str = None):
        """Allow paste (for whitelisted processes)"""
        # Already added to history in on_paste_request, so don't add here
        
        if clipboard_data["type"] == "text":
            # Perform text paste
            threading.Thread(
                target=ClipboardMonitor.perform_paste,
                args=(clipboard_data["content"],),
                daemon=True
            ).start()
        elif clipboard_data["type"] == "image":
            # Perform image paste
            image_data = clipboard_data.get("content")
            if image_data:
                threading.Thread(
                    target=ClipboardMonitor.perform_paste_with_focus,
                    args=("", "image", image_data),
                    daemon=True
                ).start()
    
    def _allow_paste_with_focus(self, clipboard_data: dict):
        """Allow paste with focus restoration (for popup approval)"""
        content_type = clipboard_data.get("type")
        
        if content_type == "text":
            # Text paste
            threading.Thread(
                target=ClipboardMonitor.perform_paste_with_focus,
                args=(clipboard_data["content"], "text", None),
                daemon=True
            ).start()
        elif content_type == "image":
            # Image paste
            threading.Thread(
                target=ClipboardMonitor.perform_paste_with_focus,
                args=("", "image", clipboard_data.get("content")),
                daemon=True
            ).start()
    
    def _add_to_history(self, clipboard_data: dict, process_name: str):
        """Add to clipboard history (keep recent 10 items, memory management optimized)"""
        import time
        
        with self.history_lock:  # Thread-safe access
            content_type = clipboard_data.get("type")
            content = clipboard_data.get("content")
            
            # For images, save only thumbnails for memory management
            if content_type == "image" and content:
                try:
                    # Create thumbnail (150x150 or use preview)
                    thumbnail = clipboard_data.get("preview")
                    if not thumbnail and content:
                        from PIL import Image
                        thumbnail = content.copy()
                        thumbnail.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    
                    full_content = thumbnail  # Replace with thumbnail
                except:
                    full_content = None
            else:
                full_content = content
            
            history_item = {
                "timestamp": time.time(),
                "type": content_type,
                "preview": clipboard_data.get("preview", ""),
                "content": content,  # Original content (text) or thumbnail (image)
                "full_content": full_content,  # Full content
                "process": process_name,
                "app_name": process_name.replace('.exe', '').title(),  # Program name
                "is_sensitive": clipboard_data.get("is_sensitive", False)
            }
            
            # Keep maximum 10 items
            if len(self.clipboard_history) >= 10:
                # Remove oldest item
                old_item = self.clipboard_history.pop(0)
                # Free image memory
                if old_item.get("type") == "image" and old_item.get("full_content"):
                    try:
                        del old_item["full_content"]
                        del old_item["content"]
                    except:
                        pass
            
            self.clipboard_history.append(history_item)
        
        # Save history
        self._save_history()
        
        # Refresh settings history if settings window is open and history tab is active
        self._refresh_settings_history()
    
    def get_clipboard_history(self):
        """Return clipboard history"""
        with self.history_lock:  # Thread-safe access
            return list(reversed(self.clipboard_history))  # Latest first
    
    def _save_history(self):
        """Save history to file"""
        try:
            self.config.save_history(self.clipboard_history)
        except Exception as e:
            print(f"History save failed: {e}")
    
    def _load_history(self):
        """Load saved history"""
        try:
            self.clipboard_history = self.config.load_history()
            print(f"✓ {len(self.clipboard_history)} history items loaded")
        except Exception as e:
            print(f"History load failed: {e}")
            self.clipboard_history = []
    
    def _refresh_settings_history(self):
        """Refresh history tab in settings window in real-time"""
        def refresh():
            if (self.settings_window and 
                self.settings_window.window and 
                self.settings_window.window.winfo_exists() and
                hasattr(self.settings_window, 'current_tab') and
                self.settings_window.current_tab == 'history'):
                # Refresh if history tab is active
                self.settings_window.show_history_settings()
        
        # Execute in main thread
        if self.root:
            try:
                self.root.after(0, refresh)
            except:
                pass
    
    def _show_settings(self, icon=None, item=None):
        """Show settings window"""
        def show():
            if not self.settings_window or not self.settings_window.window or not self.settings_window.window.winfo_exists():
                self.settings_window = SettingsWindow(self.config, parent=self.root, app=self)
                self.settings_window.show()
            else:
                self.settings_window.window.focus()
                self.settings_window.window.lift()
        
        # Execute directly in main thread or add to queue
        if self.root and threading.current_thread() == threading.main_thread():
            show()
        else:
            self.ui_queue.put(show)
    
    def _quit_application(self, icon=None, item=None):
        """Quit application"""
        print("Quitting application...")
        
        # Stop monitoring
        self.monitor.stop()
        
        # Stop tray icon
        if self.tray_icon:
            self.tray_icon.stop()
        
        # Save configuration and history
        self.config.save_config()
        self._save_history()
        
        # Exit main loop
        if self.root:
            self.root.quit()
        
        sys.exit(0)


def main():
    """Main function"""
    # Check for duplicate instance (single instance only)
    # Skip check if DEV_MODE environment variable is set
    dev_mode = os.environ.get('PASTE_GUARDIAN_DEV_MODE', '').lower() in ('1', 'true', 'yes')
    
    if not dev_mode:
        mutex_name = "Global\\PasteGuardian_SingleInstance_Mutex"
        mutex = win32event.CreateMutex(None, False, mutex_name)
        last_error = win32api.GetLastError()
        
        if last_error == winerror.ERROR_ALREADY_EXISTS:
            print("✗ Paste Guardian is already running!")
            print("Check the system tray icon.")
            print("\nTip: Set PASTE_GUARDIAN_DEV_MODE=1 to allow multiple instances during development")
            
            # Show toast notification
            try:
                toast = ToastNotifier()
                icon_path = get_icon_path()
                toast.show_toast(
                    "Paste Guardian",
                    "Application is already running!\nCheck the system tray.",
                    icon_path=icon_path,
                    duration=5
                )
            except:
                pass
            
            win32api.CloseHandle(mutex)
            sys.exit(1)
    else:
        print("⚠ Development mode: Multiple instances allowed")
        mutex = None
    
    # customtkinter default settings
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run application
    app = PasteGuardian()
    
    try:
        app.start()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected")
        app._quit_application()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Release mutex
        if not dev_mode and mutex:
            try:
                win32api.CloseHandle(mutex)
            except:
                pass


if __name__ == "__main__":
    main()
