"""
Settings window UI
SaaS dashboard style settings interface
"""
import customtkinter as ctk
from config.config_manager import ConfigManager
from typing import Callable
import os
import win32api
import win32con
import win32ui
import win32gui
from PIL import Image
import io

class SettingsWindow:
    """Settings window class"""
    
    def __init__(self, config_manager: ConfigManager, parent=None, app=None, on_close: Callable = None):
        self.config = config_manager
        self.parent = parent
        self.app = app  # Reference to main application
        self.on_close = on_close
        self.window = None
        self.whitelist_items = []
        
    def show(self):
        """Show settings window"""
        if self.window and self.window.winfo_exists():
            self.window.focus()
            self.window.lift()
            self.window.attributes('-topmost', True)
            self.window.attributes('-topmost', False)
            # Refresh history if existing window
            if hasattr(self, 'current_tab') and self.current_tab == 'history':
                self.show_history_settings()
            return
            
        # Use Toplevel if parent exists, otherwise CTk
        if self.parent:
            self.window = ctk.CTkToplevel(self.parent)
        else:
            self.window = ctk.CTk()
            
        self.window.title("Paste Guardian - Settings")
        self.window.geometry("900x600")
        
        # Theme settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Window background
        self.window.configure(fg_color="#1E1E1E")
        
        # Main container
        main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left sidebar (tab menu)
        self._create_sidebar(main_container)
        
        # Right content area
        self.content_frame = ctk.CTkFrame(
            main_container,
            fg_color="#252525",
            corner_radius=15
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Show default tab
        self.show_general_settings()
        
        # Window close event
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
    def _create_sidebar(self, parent):
        """Create left sidebar"""
        sidebar = ctk.CTkFrame(
            parent,
            width=200,
            fg_color="#2D2D2D",
            corner_radius=15
        )
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.pack(pady=(20, 30), padx=20)
        
        logo_label = ctk.CTkLabel(
            title_frame,
            text="🔒",
            font=("Segoe UI", 32)
        )
        logo_label.pack()
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Paste Guardian",
            font=("Segoe UI", 16, "bold"),
            text_color="#3B82F6"
        )
        title_label.pack()
        
        # Separator
        separator = ctk.CTkFrame(sidebar, height=2, fg_color="#3B82F6")
        separator.pack(fill="x", padx=20, pady=(0, 20))
        
        # Menu buttons
        self._create_menu_button(sidebar, "⚙️ General", self.show_general_settings)
        self._create_menu_button(sidebar, "📋 Monitoring", self.show_monitoring_settings)
        self._create_menu_button(sidebar, "✓ Whitelist", self.show_whitelist_settings)
        self._create_menu_button(sidebar, "📜 History", self.show_history_settings)
        self._create_menu_button(sidebar, "🎨 Appearance", self.show_appearance_settings)
        
        # Bottom info
        info_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        info_frame.pack(side="bottom", pady=20, padx=20)
        
        version_label = ctk.CTkLabel(
            info_frame,
            text="Version 1.0.0",
            font=("Segoe UI", 10),
            text_color="#666666"
        )
        version_label.pack()
    
    def _create_menu_button(self, parent, text, command):
        """Create menu button"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            hover_color="#3B82F6",
            anchor="w",
            height=45,
            corner_radius=10,
            font=("Segoe UI", 13)
        )
        btn.pack(padx=15, pady=5, fill="x")
        return btn
    
    def _clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_general_settings(self):
        """General settings tab"""
        self._clear_content()
        self.current_tab = 'general'
        
        # Header
        header = ctk.CTkLabel(
            self.content_frame,
            text="General Settings",
            font=("Segoe UI", 24, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        header.pack(padx=30, pady=(30, 10), anchor="w")
        
        subtitle = ctk.CTkLabel(
            self.content_frame,
            text="Configure general application behavior",
            font=("Segoe UI", 12),
            text_color="#888888",
            anchor="w"
        )
        subtitle.pack(padx=30, pady=(0, 30), anchor="w")
        
        # Settings section
        self._create_setting_card(
            self.content_frame,
            "Application Status",
            "Monitor clipboard and intercept paste operations",
            self._create_status_content
        )
        
        self._create_setting_card(
            self.content_frame,
            "Startup Options",
            "Launch application when Windows starts",
            self._create_startup_content
        )
    
    def show_monitoring_settings(self):
        """Monitoring settings tab"""
        self._clear_content()
        self.current_tab = 'monitoring'
        
        header = ctk.CTkLabel(
            self.content_frame,
            text="Monitoring Settings",
            font=("Segoe UI", 24, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        header.pack(padx=30, pady=(30, 10), anchor="w")
        
        subtitle = ctk.CTkLabel(
            self.content_frame,
            text="Choose what content types to monitor",
            font=("Segoe UI", 12),
            text_color="#888888",
            anchor="w"
        )
        subtitle.pack(padx=30, pady=(0, 30), anchor="w")
        
        # Text monitoring
        self._create_setting_card(
            self.content_frame,
            "Text Content",
            "Monitor and confirm text paste operations",
            lambda p: self._create_toggle(p, "monitor_text", self.config.get("monitor_text"))
        )
        
        # Image monitoring
        self._create_setting_card(
            self.content_frame,
            "Image Content",
            "Monitor and confirm image paste operations",
            lambda p: self._create_toggle(p, "monitor_image", self.config.get("monitor_image"))
        )
    
    def show_whitelist_settings(self):
        """Whitelist settings tab"""
        self._clear_content()
        self.current_tab = 'whitelist'
        
        header = ctk.CTkLabel(
            self.content_frame,
            text="Whitelist Management",
            font=("Segoe UI", 24, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        header.pack(padx=30, pady=(30, 10), anchor="w")
        
        subtitle = ctk.CTkLabel(
            self.content_frame,
            text="Applications that can paste without confirmation",
            font=("Segoe UI", 12),
            text_color="#888888",
            anchor="w"
        )
        subtitle.pack(padx=30, pady=(0, 20), anchor="w")
        
        # Whitelist card
        card = ctk.CTkFrame(
            self.content_frame,
            fg_color="#2D2D2D",
            corner_radius=10
        )
        card.pack(padx=30, pady=10, fill="both", expand=True)
        
        # Input frame
        input_frame = ctk.CTkFrame(card, fg_color="transparent")
        input_frame.pack(padx=20, pady=20, fill="x")
        
        entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter process name (e.g., notepad.exe)",
            height=40,
            corner_radius=10,
            font=("Segoe UI", 12)
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        add_btn = ctk.CTkButton(
            input_frame,
            text="+ Add",
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            font=("Segoe UI", 12, "bold"),
            command=lambda: self._add_whitelist_item(entry)
        )
        add_btn.pack(side="right")
        
        # Whitelist list
        list_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="#1E1E1E",
            corner_radius=10,
            height=300
        )
        list_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
        self.whitelist_container = list_frame
        self._refresh_whitelist()
    
    def show_history_settings(self):
        """History settings tab"""
        self._clear_content()
        self.current_tab = 'history'  # Mark current tab
        
        header = ctk.CTkLabel(
            self.content_frame,
            text="Clipboard History",
            font=("Segoe UI", 24, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        header.pack(padx=30, pady=(30, 10), anchor="w")
        
        subtitle = ctk.CTkLabel(
            self.content_frame,
            text="Recent clipboard activities (latest 10 items)",
            font=("Segoe UI", 12),
            text_color="#888888",
            anchor="w"
        )
        subtitle.pack(padx=30, pady=(0, 20), anchor="w")
        
        # History card
        card = ctk.CTkFrame(
            self.content_frame,
            fg_color="#2D2D2D",
            corner_radius=10
        )
        card.pack(padx=30, pady=10, fill="both", expand=True)
        
        # History list
        list_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="#1E1E1E",
            corner_radius=10,
            height=400
        )
        list_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Get history data
        if self.app:
            history = self.app.get_clipboard_history()
            if not history:
                empty_label = ctk.CTkLabel(
                    list_frame,
                    text="No clipboard history yet",
                    font=("Segoe UI", 12),
                    text_color="#666666"
                )
                empty_label.pack(pady=20)
            else:
                for item in history:
                    self._create_history_item(list_frame, item)
        else:
            error_label = ctk.CTkLabel(
                list_frame,
                text="History data unavailable",
                font=("Segoe UI", 12),
                text_color="#666666"
            )
            error_label.pack(pady=20)
    
    def _create_history_item(self, parent, history_item):
        """Create history item - identical structure for text and image"""
        import time
        import pyperclip
        from PIL import ImageTk
        
        # Main item frame
        item_frame = ctk.CTkFrame(
            parent,
            fg_color="#2D2D2D",
            corner_radius=10,
            height=80
        )
        item_frame.pack(fill="x", expand=False, padx=5, pady=5)
        item_frame.pack_propagate(False)
        
        # Grid settings - unified content start point with fixed width
        item_frame.grid_columnconfigure(0, weight=0, minsize=50)
        item_frame.grid_columnconfigure(1, weight=0, minsize=180)
        item_frame.grid_columnconfigure(2, weight=1)
        item_frame.grid_columnconfigure(3, weight=0, minsize=100)
        item_frame.grid_rowconfigure(0, weight=1)
        
        # Icon
        type_icon = "📦" if history_item["type"] == "text" else "📦"
        is_sensitive = history_item.get("is_sensitive", False)
        
        icon_label = ctk.CTkLabel(
            item_frame,
            text=type_icon,
            font=("Segoe UI", 20),
            text_color="#EF4444" if is_sensitive else "#3B82F6"
        )
        icon_label.grid(row=0, column=0, padx=(10, 0), pady=12, sticky="w")
        
        # App info frame
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=(5, 0), pady=12, sticky="w")
        
        app_name = history_item.get("app_name", history_item.get("process", "Unknown"))
        timestamp = history_item.get("timestamp", 0)
        time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
        target_app = history_item.get("target_app", history_item.get("process", "Unknown"))
        is_auto_approved = history_item.get("auto_approved", False)
        
        # Type display (Text or Image)
        type_text = "Text" if history_item["type"] == "text" else "Image"
        
        app_label = ctk.CTkLabel(
            info_frame,
            text=f"{type_text}",
            font=("Segoe UI", 11, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        app_label.pack(anchor="w", pady=(0, 2))
        
        target_text = f"→ Target: {target_app}"
        if is_auto_approved:
            target_text += " ✓"
        
        target_label = ctk.CTkLabel(
            info_frame,
            text=target_text,
            font=("Segoe UI", 10, "bold" if is_auto_approved else "normal"),
            text_color="#10B981" if is_auto_approved else "#3B82F6",
            anchor="w"
        )
        target_label.pack(anchor="w", pady=(0, 2))
        
        meta_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        meta_frame.pack(anchor="w", fill="x")
        
        time_label = ctk.CTkLabel(
            meta_frame,
            text=f"🕒 {time_str}",
            font=("Segoe UI", 9),
            text_color="#666666"
        )
        time_label.pack(side="left")
        
        if is_auto_approved:
            auto_label = ctk.CTkLabel(
                meta_frame,
                text="  👍 Auto",
                font=("Segoe UI", 9, "bold"),
                text_color="#10B981"
            )
            auto_label.pack(side="left")
        
        if is_sensitive:
            warning_label = ctk.CTkLabel(
                meta_frame,
                text="  ⚠️ Sensitive",
                font=("Segoe UI", 9, "bold"),
                text_color="#EF4444"
            )
            warning_label.pack(side="left")
        
        # Content frame (identical for text and image)
        content_container = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_container.grid(row=0, column=2, padx=(0, 5), pady=12, sticky="w")
        
        if history_item["type"] == "text":
            preview_text = history_item.get("preview", "")[:85]
            if len(history_item.get("preview", "")) > 85:
                preview_text += "..."
            
            text_label = ctk.CTkLabel(
                content_container,
                text=preview_text,
                font=("Segoe UI", 10),
                text_color="#CCCCCC",
                anchor="w",
                wraplength=240,
                justify="left"
            )
            text_label.pack(side="left", anchor="w", padx=0, pady=0)
            
        else:  # image
            try:
                thumbnail = history_item.get("full_content") or history_item.get("preview")
                if thumbnail:
                    ctk_image = ctk.CTkImage(
                        light_image=thumbnail,
                        dark_image=thumbnail,
                        size=(40, 40)
                    )
                    
                    image_label = ctk.CTkLabel(
                        content_container,
                        image=ctk_image,
                        text=""
                    )
                    image_label.pack(side="left", anchor="w", padx=0, pady=0)
                else:
                    raise Exception("No image")
            except:
                error_label = ctk.CTkLabel(
                    content_container,
                    text="Image preview unavailable",
                    font=("Segoe UI", 9),
                    text_color="#666666",
                    anchor="w"
                )
                error_label.pack(side="left", anchor="w", padx=0, pady=0)
        
        # Button
        def recopy():
            content = history_item.get("content")
            content_type = history_item.get("type")
            
            if content_type == "text" and content:
                pyperclip.copy(content)
                print(f"✓ Text copied to clipboard")
            elif content_type == "image" and content:
                if self.app and hasattr(self.app.monitor, '_set_clipboard_image'):
                    import threading
                    threading.Thread(
                        target=self.app.monitor._set_clipboard_image,
                        args=(content,),
                        daemon=True
                    ).start()
                    print(f"✓ Image copied to clipboard")
        
        copy_btn = ctk.CTkButton(
            item_frame,
            text="📋 Copy",
            width=75,
            height=32,
            corner_radius=6,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            font=("Segoe UI", 9, "bold"),
            command=recopy
        )
        copy_btn.grid(row=0, column=3, padx=(5, 10), pady=12, sticky="w")
    
    def show_appearance_settings(self):
        """Appearance settings tab"""
        self._clear_content()
        self.current_tab = 'appearance'
        
        header = ctk.CTkLabel(
            self.content_frame,
            text="Appearance Settings",
            font=("Segoe UI", 24, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        header.pack(padx=30, pady=(30, 10), anchor="w")
        
        subtitle = ctk.CTkLabel(
            self.content_frame,
            text="Customize the look and feel of confirmation popups",
            font=("Segoe UI", 12),
            text_color="#888888",
            anchor="w"
        )
        subtitle.pack(padx=30, pady=(0, 30), anchor="w")
        
        # Opacity settings
        self._create_setting_card(
            self.content_frame,
            "Popup Opacity",
            "Adjust the transparency of confirmation popups",
            self._create_opacity_slider
        )
    
    def _create_setting_card(self, parent, title, description, content_creator):
        """Create settings card"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#2D2D2D",
            corner_radius=10
        )
        card.pack(padx=30, pady=10, fill="x")
        
        # Top text
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.pack(padx=20, pady=(20, 10), fill="x")
        
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=("Segoe UI", 11),
            text_color="#888888",
            anchor="w"
        )
        desc_label.pack(anchor="w", pady=(5, 0))
        
        # Content area
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(padx=20, pady=(10, 20), fill="x")
        
        content_creator(content_frame)
    
    def _create_toggle(self, parent, config_key, current_value):
        """Create toggle switch"""
        switch = ctk.CTkSwitch(
            parent,
            text="Enabled" if current_value else "Disabled",
            command=lambda: self._toggle_setting(config_key, switch),
            progress_color="#3B82F6",
            button_color="#FFFFFF",
            button_hover_color="#E5E5E5",
            font=("Segoe UI", 12)
        )
        switch.pack(anchor="w")
        
        if current_value:
            switch.select()
        
        return switch
    
    def _toggle_setting(self, config_key, switch):
        """Toggle setting"""
        new_value = switch.get() == 1
        self.config.set(config_key, new_value)
        switch.configure(text="Enabled" if new_value else "Disabled")
    
    def _create_status_content(self, parent):
        """Create status content"""
        status_label = ctk.CTkLabel(
            parent,
            text="● Active",
            font=("Segoe UI", 13),
            text_color="#10B981"
        )
        status_label.pack(anchor="w")
    
    def _create_startup_content(self, parent):
        """Create startup content"""
        switch = ctk.CTkSwitch(
            parent,
            text="Launch on startup",
            progress_color="#3B82F6",
            button_color="#FFFFFF",
            button_hover_color="#E5E5E5",
            font=("Segoe UI", 12)
        )
        switch.pack(anchor="w")
    
    def _create_opacity_slider(self, parent):
        """Create opacity slider"""
        current_opacity = self.config.get("popup_opacity", 0.95)
        
        value_label = ctk.CTkLabel(
            parent,
            text=f"{int(current_opacity * 100)}%",
            font=("Segoe UI", 13, "bold"),
            text_color="#3B82F6"
        )
        value_label.pack(anchor="w", pady=(0, 10))
        
        slider = ctk.CTkSlider(
            parent,
            from_=0.5,
            to=1.0,
            number_of_steps=50,
            command=lambda v: self._update_opacity(v, value_label),
            progress_color="#3B82F6",
            button_color="#FFFFFF",
            button_hover_color="#E5E5E5"
        )
        slider.set(current_opacity)
        slider.pack(fill="x", pady=(0, 10))
        
        hint_label = ctk.CTkLabel(
            parent,
            text="Lower values make the popup more transparent",
            font=("Segoe UI", 10),
            text_color="#666666"
        )
        hint_label.pack(anchor="w")
    
    def _update_opacity(self, value, label):
        """Update opacity"""
        self.config.set("popup_opacity", value)
        label.configure(text=f"{int(value * 100)}%")
    
    def _add_whitelist_item(self, entry):
        """Add whitelist item"""
        process_name = entry.get().strip()
        if process_name:
            self.config.add_to_whitelist(process_name)
            entry.delete(0, 'end')
            self._refresh_whitelist()
    
    def _refresh_whitelist(self):
        """Refresh whitelist display"""
        # Remove existing items
        for widget in self.whitelist_container.winfo_children():
            widget.destroy()
        
        # Get whitelist
        whitelist = self.config.get_whitelist()
        
        if not whitelist:
            empty_label = ctk.CTkLabel(
                self.whitelist_container,
                text="No whitelisted applications",
                font=("Segoe UI", 12),
                text_color="#666666"
            )
            empty_label.pack(pady=20)
        else:
            for process in whitelist:
                self._create_whitelist_item(process)
    
    def _create_whitelist_item(self, process_name):
        """Create whitelist item with async icon loading"""
        item_frame = ctk.CTkFrame(
            self.whitelist_container,
            fg_color="#2D2D2D",
            corner_radius=8,
            height=50
        )
        item_frame.pack(fill="x", padx=5, pady=5)
        item_frame.pack_propagate(False)
        
        # Display default icon first
        icon_label = ctk.CTkLabel(
            item_frame,
            text="📦",
            font=("Segoe UI", 18),
            text_color="#FFFFFF"
        )
        icon_label.pack(side="left", padx=(15, 5), pady=10)
        
        # Process name
        name_label = ctk.CTkLabel(
            item_frame,
            text=process_name,
            font=("Segoe UI", 12),
            text_color="#FFFFFF",
            anchor="w"
        )
        name_label.pack(side="left", padx=(5, 10), pady=10)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            item_frame,
            text="✖",
            width=40,
            height=30,
            corner_radius=8,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            font=("Segoe UI", 14, "bold"),
            command=lambda: self._remove_whitelist_item(process_name)
        )
        delete_btn.pack(side="right", padx=10, pady=10)
        
        # Try to extract icon asynchronously (optional)
        import threading
        def load_icon_async():
            try:
                icon_image = self._extract_process_icon_simple(process_name)
                if icon_image and icon_label.winfo_exists():
                    ctk_image = ctk.CTkImage(
                        light_image=icon_image,
                        dark_image=icon_image,
                        size=(24, 24)
                    )
                    icon_label.configure(image=ctk_image, text="")
            except:
                pass
        
        # Load icon in background
        threading.Thread(target=load_icon_async, daemon=True).start()
    
    def _extract_process_icon_simple(self, process_name: str) -> Image.Image:
        """Extract high-quality icon from process executable (LANCZOS resizing)"""
        try:
            # Check only major paths
            common_paths = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32', process_name),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'SysWOW64', process_name),
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Common Files', process_name),
            ]
            
            exe_path = None
            for path in common_paths:
                if os.path.exists(path):
                    exe_path = path
                    break
            
            if not exe_path:
                return None
            
            # Extract high-resolution icon
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            
            # Use large icon (higher quality)
            icon_handle = large[0] if large else (small[0] if small else None)
            
            if icon_handle:
                # Get icon size
                ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
                ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
                
                # Create DC
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                hdc_mem = hdc.CreateCompatibleDC()
                hdc_mem.SelectObject(hbmp)
                
                # Set transparent background
                hdc_mem.FillSolidRect((0, 0, ico_x, ico_y), win32api.RGB(0, 0, 0))
                
                # Draw icon
                hdc_mem.DrawIcon((0, 0), icon_handle)
                
                # Extract bitmap data
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer(
                    'RGB',
                    (ico_x, ico_y),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                # High-quality resizing with LANCZOS filter
                img_resized = img.resize((32, 32), Image.Resampling.LANCZOS)
                
                # Release resources
                if large:
                    for icon in large:
                        win32gui.DestroyIcon(icon)
                if small:
                    for icon in small:
                        win32gui.DestroyIcon(icon)
                
                return img_resized
            
        except Exception as e:
            # Handle failure silently
            pass
        
        return None
    
    def _extract_process_icon(self, process_name: str) -> Image.Image:
        """Extract icon from process executable"""
        try:
            # Common program paths
            search_paths = [
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), '**', process_name),
                os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), '**', process_name),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), '**', process_name),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', '**', process_name),
            ]
            
            # Find executable file
            import glob
            exe_path = None
            for path_pattern in search_paths:
                matches = glob.glob(path_pattern, recursive=True)
                if matches:
                    exe_path = matches[0]
                    break
            
            if not exe_path:
                return None
            
            # Extract icon
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
            
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            if large:
                win32gui.DestroyIcon(large[0])
            if small:
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                hdc = hdc.CreateCompatibleDC()
                hdc.SelectObject(hbmp)
                hdc.DrawIcon((0, 0), small[0])
                
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer(
                    'RGB',
                    (ico_x, ico_y),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                win32gui.DestroyIcon(small[0])
                return img
            
        except Exception as e:
            print(f"Icon extraction failed ({process_name}): {e}")
        
        return None
    
    def _remove_whitelist_item(self, process_name):
        """Remove whitelist item"""
        self.config.remove_from_whitelist(process_name)
        self._refresh_whitelist()
    
    def _on_window_close(self):
        """Window close event"""
        if self.on_close:
            self.on_close()
        self.window.destroy()
    
    def run(self):
        """Run settings window"""
        self.show()
        self.window.mainloop()
