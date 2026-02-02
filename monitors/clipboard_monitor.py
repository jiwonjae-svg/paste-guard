"""
Clipboard monitoring module
Detects clipboard changes and intercepts paste key events
"""
import threading
import time
import pyperclip
import win32clipboard
import win32con
from PIL import Image, ImageGrab
from io import BytesIO
from typing import Callable, Optional, Tuple
import keyboard  # Use keyboard instead of pynput
import psutil
import win32gui
import win32process


class ClipboardMonitor:
    """Class for monitoring clipboard and handling paste events"""
    
    def __init__(self, on_paste_request: Callable):
        self.on_paste_request = on_paste_request
        self.running = False
        self.monitor_thread = None
        self.last_clipboard_content = None
        self.paste_pending = False  # Waiting for paste
        self.pending_data = None    # Pending data
        self._allow_next_paste = False  # Flag to allow next paste (prevent infinite loop)
        self._processing = False  # Processing flag
        
    def start(self):
        """Start monitoring"""
        if not self.running:
            self.running = True
            
            # Hook Ctrl+V with keyboard library
            keyboard.add_hotkey('ctrl+v', self._on_paste_hotkey, suppress=True)
            
            print("Clipboard Start monitoring")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        
        # Release all hooks
        try:
            keyboard.unhook_all_hotkeys()
            keyboard.unhook_all()
        except:
            pass
        
        print("Clipboard Stop monitoring")
    
    def _on_paste_hotkey(self):
        """Ctrl+V hotkey callback - Block paste and request confirmation"""
        if not self.running:
            return
        
        # Prevent infinite loop: Allow approved paste
        if self._allow_next_paste:
            print("✓ Approved paste passed")
            self._allow_next_paste = False
            # Already blocked despite suppress=True, so do nothing here
            return
        
        # Prevent duplicate processing
        if self._processing:
            print("⚠️ Already processing...")
            return
        
        self._processing = True
        print("Ctrl+V detected! (Blocked)")
        
        try:
            # Handle paste attempt
            self._handle_paste_attempt()
        finally:
            self._processing = False
    
    def _handle_paste_attempt(self):
        """Handle paste attempt"""
        if not self.running:
            print("Monitoring is not running")
            return
        
        print("Paste attempt detected - Starting processing")
        
        # Get currently active process
        active_process = self._get_active_process()
        print(f"Active process: {active_process}")
        
        # Get clipboard content
        clipboard_data = self._get_clipboard_data()
        
        if clipboard_data:
            print(f"Clipboard data type: {clipboard_data.get('type')}")
            # Call callback (Show confirmation popup)
            self.on_paste_request(clipboard_data, active_process)
        else:
            print("No data in clipboard")
    
    def _get_active_process(self) -> str:
        """Get currently active process name"""
        try:
            # Get active window handle
            hwnd = win32gui.GetForegroundWindow()
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            # Get process name
            process = psutil.Process(pid)
            return process.name()
        except Exception as e:
            print(f"Failed to get process info: {e}")
            return "unknown"
    
    def _get_clipboard_data(self) -> Optional[dict]:
        """Get clipboard data"""
        try:
            # Check image
            image = ImageGrab.grabclipboard()
            if image:
                return {
                    "type": "image",
                    "content": image,
                    "preview": self._create_image_preview(image),
                    "is_sensitive": False
                }
            
            # Check text
            text = pyperclip.paste()
            if text:
                is_sensitive = self._check_sensitive_data(text)
                return {
                    "type": "text",
                    "content": text,
                    "preview": text[:200] + ("..." if len(text) > 200 else ""),
                    "is_sensitive": is_sensitive
                }
            
        except Exception as e:
            print(f"Failed to get clipboard data: {e}")
        
        return None
    
    def _check_sensitive_data(self, text: str) -> bool:
        """Detect sensitive information patterns (email, phone, card number)"""
        import re
        
        patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{2,4}[-.]?\d{3,4}[-.]?\d{4}\b',  # Phone number
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Card number
            r'\b\d{6}[-]?\d{7}\b',  # ID number
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                print(f"⚠️ Sensitive information detected: {pattern}")
                return True
        
        return False
    
    def _create_image_preview(self, image: Image.Image) -> Image.Image:
        """Generate image preview (thumbnail)"""
        try:
            thumbnail = image.copy()
            thumbnail.thumbnail((150, 150), Image.Resampling.LANCZOS)
            return thumbnail
        except Exception as e:
            print(f"Failed to generate image preview: {e}")
            return image
    
    @staticmethod
    def perform_paste(content: str):
        """Perform actual paste"""
        try:
            # Update clipboard with approved content
            pyperclip.copy(content)
            
            # Short delay
            time.sleep(0.1)
            
            # Simulate Ctrl+V with keyboard library
            keyboard.press_and_release('ctrl+v')
            
            print("✓ Paste executed")
            
        except Exception as e:
            print(f"Failed to perform paste: {e}")
    
    @staticmethod
    def perform_paste_with_focus(content: str, content_type: str = "text", image_data=None):
        """Perform actual paste through focus restoration (text and image support)"""
        try:
            # 1. Set content to clipboard
            if content_type == "text":
                pyperclip.copy(content)
            elif content_type == "image" and image_data:
                # Process image using win32clipboard
                ClipboardMonitor._set_clipboard_image(image_data)
            
            # 2. Get currently active window (paste target)
            target_hwnd = win32gui.GetForegroundWindow()
            
            # 3. Wait for popup to close and focus to be restored
            time.sleep(0.15)
            
            # 4. Force focus on target window
            if target_hwnd:
                try:
                    win32gui.SetForegroundWindow(target_hwnd)
                    time.sleep(0.05)  # Stabilize focus
                except:
                    pass
            
            # 5. Send actual paste command
            keyboard.press_and_release('ctrl+v')
            
            print(f"✓ Focus restore paste executed ({content_type})")
            
        except Exception as e:
            print(f"Failed to perform focus restore paste: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def _set_clipboard_image(image):
        """Reliably set image to clipboard using win32clipboard (DIB format)"""
        try:
            from PIL import Image
            import io
            
            # Convert PIL image to BMP format
            output = io.BytesIO()
            
            # Convert RGBA to RGB (remove transparency)
            if image.mode == 'RGBA':
                # Composite with white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # Use alpha channel
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save as BMP format
            image.save(output, 'BMP')
            data = output.getvalue()[14:]  # Remove BMP header (14 bytes)
            output.close()
            
            # Try to open clipboard (max 3 attempts)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    win32clipboard.OpenClipboard()
                    break
                except:
                    if attempt < max_retries - 1:
                        time.sleep(0.05)
                    else:
                        raise
            
            # Clear clipboard and set as DIB format
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_DIB, data)
            win32clipboard.CloseClipboard()
            
            print("✓ Image reliably set to clipboard")
            
        except Exception as e:
            print(f"Failed to set image to clipboard: {e}")
            import traceback
            traceback.print_exc()
            # Close clipboard on failure
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
