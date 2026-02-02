"""
Confirmation popup UI
Floating confirmation window displayed on paste request
"""
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Callable, Optional
import tkinter as tk
import re

class ConfirmationPopup:
    """Paste confirmation popup window"""
    
    def __init__(self, clipboard_data: dict, process_name: str, 
                 on_confirm: Callable, on_always_allow: Callable, on_cancel: Callable, opacity: float = 0.95):
        self.clipboard_data = clipboard_data
        self.process_name = process_name
        self.on_confirm = on_confirm
        self.on_always_allow = on_always_allow
        self.on_cancel = on_cancel
        self.opacity = opacity
        self.window = None
        self.result = None
        # Detect sensitive information (get directly from clipboard data)
        self.is_security_risk = clipboard_data.get("is_sensitive", False) or self._check_security_risk()
    
    def _check_security_risk(self) -> bool:
        """Detect security risk patterns"""
        if self.clipboard_data.get("type") != "text":
            return False
        
        content = self.clipboard_data.get("content", "")
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # Card number pattern (16 digits, hyphens allowed)
        card_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        
        if re.search(email_pattern, content) or re.search(card_pattern, content):
            return True
        
        return False
        
    def show(self):
        """Show popup window"""
        self.window = ctk.CTkToplevel()
        self.window.title("Paste Confirmation")
        
        # Window settings
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.0)  # Initially transparent
        self.window.overrideredirect(True)  # Remove title bar
        
        # Background color
        self.window.configure(fg_color="#1E1E1E")
        
        # Get mouse position
        x, y = self.window.winfo_pointerx(), self.window.winfo_pointery()
        
        # Red border when security risk detected
        border_color = "#DC2626" if self.is_security_risk else "#3B82F6"
        
        # Main frame
        main_frame = ctk.CTkFrame(
            self.window,
            fg_color="#1E1E1E",
            corner_radius=10,
            border_width=2,
            border_color=border_color
        )
        main_frame.pack(padx=0, pady=0, fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#2D2D2D",
            corner_radius=10,
            height=50
        )
        header_frame.pack(padx=15, pady=(15, 10), fill="x")
        header_frame.pack_propagate(False)
        
        # Icon and title (warning shown on security risk)
        if self.is_security_risk:
            title_text = "⚠️ Sensitive Data Detected!"
            title_color = "#DC2626"
        else:
            title_text = "🔒 Paste Request"
            title_color = "#3B82F6"
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=("Segoe UI", 16, "bold"),
            text_color=title_color
        )
        title_label.pack(side="left", padx=15, pady=10)
        
        # Additional security warning message
        if self.is_security_risk:
            warning_label = ctk.CTkLabel(
                main_frame,
                text="⚠️ This content may contain sensitive information (email, phone, card number)",
                font=("Segoe UI", 10),
                text_color="#EF4444",
                wraplength=400
            )
            warning_label.pack(padx=15, pady=(5, 0), anchor="w")
        
        # Process information (large on top right)
        process_label = ctk.CTkLabel(
            header_frame,
            text=f"Target: {self.process_name}",
            font=("Segoe UI", 13, "bold"),
            text_color="#10B981"
        )
        process_label.pack(side="right", padx=15, pady=10)
        
        # Content frame
        content_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#252525",
            corner_radius=10
        )
        content_frame.pack(padx=15, pady=10, fill="both", expand=True)
        
        # Preview based on content type
        if self.clipboard_data["type"] == "text":
            self._create_text_preview(content_frame)
        elif self.clipboard_data["type"] == "image":
            self._create_image_preview(content_frame)
        
        # Button frame (perfectly balanced layout)
        button_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        button_frame.pack(padx=20, pady=(10, 20), fill="x")
        
        # 3-column grid layout (each button expands equally)
        button_frame.grid_columnconfigure(0, weight=1, uniform="button")
        button_frame.grid_columnconfigure(1, weight=1, uniform="button")
        button_frame.grid_columnconfigure(2, weight=1, uniform="button")
        
        # Cancel button (Deny)
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="✖ Deny",
            command=self._on_cancel_click,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            corner_radius=10,
            height=45,
            font=("Segoe UI", 12, "bold")
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Always Allow Button
        always_btn = ctk.CTkButton(
            button_frame,
            text="✓✓ Always Allow",
            command=self._on_always_allow_click,
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=10,
            height=45,
            font=("Segoe UI", 11, "bold")
        )
        always_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Confirm button (Allow Once)
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="✓ Allow Once",
            command=self._on_confirm_click,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=10,
            height=45,
            font=("Segoe UI", 12, "bold")
        )
        confirm_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        # Adjust window size and position
        self.window.update_idletasks()
        width = 450
        height = self.window.winfo_reqheight()
        
        # Check screen boundaries
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = min(x + 20, screen_width - width - 20)
        y = min(y + 20, screen_height - height - 20)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Cancel with ESC key
        self.window.bind("<Escape>", lambda e: self._on_cancel_click())
        
        # Cancel when clicking outside window (optional)
        # self.window.bind("<FocusOut>", lambda e: self._on_cancel_click())
        
        # Set focus
        self.window.focus_force()
        
        # Fade-in animation
        self._animate_show()
        
    def _create_text_preview(self, parent):
        """Generate text preview"""
        label = ctk.CTkLabel(
            parent,
            text="📄 Text Content:",
            font=("Segoe UI", 12, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        label.pack(padx=15, pady=(15, 5), anchor="w")
        
        # Text box
        textbox = ctk.CTkTextbox(
            parent,
            fg_color="#1E1E1E",
            corner_radius=8,
            height=120,
            font=("Segoe UI", 11),
            wrap="word",
            activate_scrollbars=True
        )
        textbox.pack(padx=15, pady=(0, 15), fill="both", expand=True)
        textbox.insert("1.0", self.clipboard_data["preview"])
        textbox.configure(state="disabled")
        
        # Length information
        full_length = len(self.clipboard_data["content"])
        if full_length > 200:
            info_label = ctk.CTkLabel(
                parent,
                text=f"Total length: {full_length} characters",
                font=("Segoe UI", 10),
                text_color="#888888"
            )
            info_label.pack(padx=15, pady=(0, 10))
    
    def _create_image_preview(self, parent):
        """Generate image preview"""
        label = ctk.CTkLabel(
            parent,
            text="🖼️ Image Content:",
            font=("Segoe UI", 12, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        label.pack(padx=15, pady=(15, 5), anchor="w")
        
        # Image frame
        image_frame = ctk.CTkFrame(
            parent,
            fg_color="#1E1E1E",
            corner_radius=8
        )
        image_frame.pack(padx=15, pady=(0, 15), fill="both", expand=True)
        
        try:
            # Convert PIL image to CTkImage
            preview_img = self.clipboard_data["preview"]
            
            # Create CTkImage
            ctk_image = ctk.CTkImage(
                light_image=preview_img,
                dark_image=preview_img,
                size=(150, 150)
            )
            
            # Image label
            img_label = ctk.CTkLabel(
                image_frame,
                image=ctk_image,
                text=""
            )
            img_label.pack(padx=20, pady=20)
            
            # Image size information
            original_img = self.clipboard_data["content"]
            size_label = ctk.CTkLabel(
                parent,
                text=f"Size: {original_img.width} × {original_img.height} pixels",
                font=("Segoe UI", 10),
                text_color="#888888"
            )
            size_label.pack(padx=15, pady=(0, 10))
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                image_frame,
                text=f"Failed to display image: {str(e)}",
                font=("Segoe UI", 11),
                text_color="#DC2626"
            )
            error_label.pack(padx=20, pady=20)
    
    def _on_confirm_click(self):
        """Confirm button clicked"""
        self.result = "confirm"
        self.on_confirm(self.clipboard_data)
        self.close()
    
    def _on_always_allow_click(self):
        """Always Allow button clicked"""
        self.result = "always_allow"
        self.on_always_allow(self.clipboard_data)
        self.close()
    
    def _on_cancel_click(self):
        """Cancel button clicked"""
        self.result = "cancel"
        self.on_cancel()
        self.close()
    
    def _animate_show(self):
        """Popup fade-in animation (0.15 seconds)"""
        steps = 15
        delay = 10  # ms (total 150ms = 0.15 seconds)
        increment = self.opacity / steps
        
        def fade_step(current_alpha, step):
            if step < steps and self.window and self.window.winfo_exists():
                new_alpha = min(current_alpha + increment, self.opacity)
                self.window.attributes('-alpha', new_alpha)
                self.window.after(delay, lambda: fade_step(new_alpha, step + 1))
        
        fade_step(0.0, 0)
    
    def close(self):
        """Close popup window"""
        if self.window:
            self.window.destroy()
            self.window = None
