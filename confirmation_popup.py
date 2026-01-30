"""
확인 팝업 UI
붙여넣기 요청 시 표시되는 플로팅 확인 창
"""
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Callable, Optional
import tkinter as tk
import re

class ConfirmationPopup:
    """붙여넣기 확인 팝업 창"""
    
    def __init__(self, clipboard_data: dict, process_name: str, 
                 on_confirm: Callable, on_cancel: Callable, opacity: float = 0.95):
        self.clipboard_data = clipboard_data
        self.process_name = process_name
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.opacity = opacity
        self.window = None
        self.result = None
        # 민감 정보 감지 (클립보드 데이터에서 직접 가져오기)
        self.is_security_risk = clipboard_data.get("is_sensitive", False) or self._check_security_risk()
    
    def _check_security_risk(self) -> bool:
        """보안 위험 패턴 감지"""
        if self.clipboard_data.get("type") != "text":
            return False
        
        content = self.clipboard_data.get("content", "")
        
        # 이메일 패턴
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # 카드번호 패턴 (16자리 숫자, 하이픈 포함 가능)
        card_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        
        if re.search(email_pattern, content) or re.search(card_pattern, content):
            return True
        
        return False
        
    def show(self):
        """팝업 창 표시"""
        self.window = ctk.CTkToplevel()
        self.window.title("Paste Confirmation")
        
        # 창 설정
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.0)  # 초기에는 투명하게
        self.window.overrideredirect(True)  # 타이틀바 제거
        
        # 배경색
        self.window.configure(fg_color="#1E1E1E")
        
        # 마우스 위치 가져오기
        x, y = self.window.winfo_pointerx(), self.window.winfo_pointery()
        
        # 보안 위험 감지 시 빨간색 테두리
        border_color = "#DC2626" if self.is_security_risk else "#3B82F6"
        
        # 메인 프레임
        main_frame = ctk.CTkFrame(
            self.window,
            fg_color="#1E1E1E",
            corner_radius=10,
            border_width=2,
            border_color=border_color
        )
        main_frame.pack(padx=0, pady=0, fill="both", expand=True)
        
        # 헤더
        header_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#2D2D2D",
            corner_radius=10,
            height=50
        )
        header_frame.pack(padx=15, pady=(15, 10), fill="x")
        header_frame.pack_propagate(False)
        
        # 아이콘과 제목 (보안 위험 시 경고 표시)
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
        
        # 보안 경고 추가 메시지
        if self.is_security_risk:
            warning_label = ctk.CTkLabel(
                main_frame,
                text="⚠️ This content may contain sensitive information (email, phone, card number)",
                font=("Segoe UI", 10),
                text_color="#EF4444",
                wraplength=400
            )
            warning_label.pack(padx=15, pady=(5, 0), anchor="w")
        
        # 프로세스 정보
        process_label = ctk.CTkLabel(
            header_frame,
            text=f"From: {self.process_name}",
            font=("Segoe UI", 11),
            text_color="#888888"
        )
        process_label.pack(side="right", padx=15, pady=10)
        
        # 컨텐츠 프레임
        content_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#252525",
            corner_radius=10
        )
        content_frame.pack(padx=15, pady=10, fill="both", expand=True)
        
        # 컨텐츠 타입에 따른 미리보기
        if self.clipboard_data["type"] == "text":
            self._create_text_preview(content_frame)
        elif self.clipboard_data["type"] == "image":
            self._create_image_preview(content_frame)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        button_frame.pack(padx=15, pady=(10, 15), fill="x")
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="✖ Deny",
            command=self._on_cancel_click,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            corner_radius=10,
            height=40,
            font=("Segoe UI", 13, "bold")
        )
        cancel_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        # 확인 버튼
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="✓ Allow Paste",
            command=self._on_confirm_click,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=10,
            height=40,
            font=("Segoe UI", 13, "bold")
        )
        confirm_btn.pack(side="right", padx=(10, 0), expand=True, fill="x")
        
        # 창 크기 조정 및 위치 설정
        self.window.update_idletasks()
        width = 450
        height = self.window.winfo_reqheight()
        
        # 화면 경계 확인
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = min(x + 20, screen_width - width - 20)
        y = min(y + 20, screen_height - height - 20)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # ESC 키로 취소
        self.window.bind("<Escape>", lambda e: self._on_cancel_click())
        
        # 창 외부 클릭 시 취소 (선택사항)
        # self.window.bind("<FocusOut>", lambda e: self._on_cancel_click())
        
        # 포커스 설정
        self.window.focus_force()
        
        # 페이드인 애니메이션
        self._animate_show()
        
    def _create_text_preview(self, parent):
        """텍스트 미리보기 생성"""
        label = ctk.CTkLabel(
            parent,
            text="📄 Text Content:",
            font=("Segoe UI", 12, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        label.pack(padx=15, pady=(15, 5), anchor="w")
        
        # 텍스트박스
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
        
        # 길이 정보
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
        """이미지 미리보기 생성"""
        label = ctk.CTkLabel(
            parent,
            text="🖼️ Image Content:",
            font=("Segoe UI", 12, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        label.pack(padx=15, pady=(15, 5), anchor="w")
        
        # 이미지 프레임
        image_frame = ctk.CTkFrame(
            parent,
            fg_color="#1E1E1E",
            corner_radius=8
        )
        image_frame.pack(padx=15, pady=(0, 15), fill="both", expand=True)
        
        try:
            # PIL 이미지를 CTkImage로 변환
            preview_img = self.clipboard_data["preview"]
            
            # CTkImage 생성
            ctk_image = ctk.CTkImage(
                light_image=preview_img,
                dark_image=preview_img,
                size=(150, 150)
            )
            
            # 이미지 레이블
            img_label = ctk.CTkLabel(
                image_frame,
                image=ctk_image,
                text=""
            )
            img_label.pack(padx=20, pady=20)
            
            # 이미지 크기 정보
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
        """확인 버튼 클릭"""
        self.result = "confirm"
        self.on_confirm(self.clipboard_data)
        self.close()
    
    def _on_cancel_click(self):
        """취소 버튼 클릭"""
        self.result = "cancel"
        self.on_cancel()
        self.close()
    
    def _animate_show(self):
        """팝업 페이드인 애니메이션 (0.15초)"""
        steps = 15
        delay = 10  # ms (총 150ms = 0.15초)
        increment = self.opacity / steps
        
        def fade_step(current_alpha, step):
            if step < steps and self.window and self.window.winfo_exists():
                new_alpha = min(current_alpha + increment, self.opacity)
                self.window.attributes('-alpha', new_alpha)
                self.window.after(delay, lambda: fade_step(new_alpha, step + 1))
        
        fade_step(0.0, 0)
    
    def close(self):
        """팝업 창 닫기"""
        if self.window:
            self.window.destroy()
            self.window = None
