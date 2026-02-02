"""
Paste Guardian - Main Application
Clipboard paste security program
"""
import customtkinter as ctk
import threading
import sys
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import queue
from config_manager import ConfigManager
from clipboard_monitor import ClipboardMonitor
from confirmation_popup import ConfirmationPopup
from settings_window import SettingsWindow


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
        
        # Start clipboard monitoring
        self.monitor.start()
        
        # Start system tray icon (in separate thread)
        tray_thread = threading.Thread(target=self._start_tray_icon, daemon=True)
        tray_thread.start()
        
        # Process UI queue
        self._process_ui_queue()
        
        # Auto-show settings window on first run (after slight delay)
        self.root.after(500, lambda: self._show_settings())
        
        # Main loop
        self.root.mainloop()
    
    def _start_tray_icon(self):
        """Start system tray icon"""
        # Create icon image
        icon_image = self._create_tray_icon()
        
        # Create menu
        menu = Menu(
            MenuItem("Settings", self._show_settings),
            MenuItem("Exit", self._quit_application)
        )
        
        # Create tray icon
        self.tray_icon = Icon(
            "PasteGuardian",
            icon_image,
            "Paste Guardian - Active",
            menu
        )
        
        # Run tray icon
        self.tray_icon.run()
    
    def _create_tray_icon(self):
        """Create tray icon image"""
        # Create simple icon (64x64)
        img = Image.new('RGB', (64, 64), color='#3B82F6')
        draw = ImageDraw.Draw(img)
        
        # Draw lock icon (simple version)
        draw.rectangle([20, 28, 44, 50], fill='white', outline='white')
        draw.ellipse([24, 20, 40, 36], fill='#3B82F6', outline='white', width=3)
        
        return img
    
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
        if process_name in self.config.get_whitelist():
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
        
        # Show confirmation popup (add to UI queue)
        def show_popup():
            self._show_confirmation_popup(clipboard_data, process_name)
        
        self.ui_queue.put(show_popup)
    
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
        
        # Add to whitelist
        self.config.add_to_whitelist(process_name)
        
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


if __name__ == "__main__":
    main()
