"""
설정 창 UI
SaaS 대시보드 스타일의 설정 인터페이스
"""
import customtkinter as ctk
from config_manager import ConfigManager
from typing import Callable
import os
import win32api
import win32con
import win32ui
import win32gui
from PIL import Image
import io

class SettingsWindow:
    """설정 창 클래스"""
    
    def __init__(self, config_manager: ConfigManager, parent=None, app=None, on_close: Callable = None):
        self.config = config_manager
        self.parent = parent
        self.app = app  # 메인 애플리케이션 참조
        self.on_close = on_close
        self.window = None
        self.whitelist_items = []
        
    def show(self):
        """설정 창 표시"""
        if self.window and self.window.winfo_exists():
            self.window.focus()
            self.window.lift()
            self.window.attributes('-topmost', True)
            self.window.attributes('-topmost', False)
            # 기존 창이 있으면 히스토리 새로고침
            if hasattr(self, 'current_tab') and self.current_tab == 'history':
                self.show_history_settings()
            return
            
        # 부모가 있으면 Toplevel, 없으면 CTk 사용
        if self.parent:
            self.window = ctk.CTkToplevel(self.parent)
        else:
            self.window = ctk.CTk()
            
        self.window.title("Paste Guardian - Settings")
        self.window.geometry("900x600")
        
        # 테마 설정
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 윈도우 배경
        self.window.configure(fg_color="#1E1E1E")
        
        # 메인 컨테이너
        main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 좌측 사이드바 (탭 메뉴)
        self._create_sidebar(main_container)
        
        # 우측 컨텐츠 영역
        self.content_frame = ctk.CTkFrame(
            main_container,
            fg_color="#252525",
            corner_radius=15
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # 기본 탭 표시
        self.show_general_settings()
        
        # 창 닫기 이벤트
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
    def _create_sidebar(self, parent):
        """좌측 사이드바 생성"""
        sidebar = ctk.CTkFrame(
            parent,
            width=200,
            fg_color="#2D2D2D",
            corner_radius=15
        )
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # 로고/타이틀
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
        
        # 구분선
        separator = ctk.CTkFrame(sidebar, height=2, fg_color="#3B82F6")
        separator.pack(fill="x", padx=20, pady=(0, 20))
        
        # 메뉴 버튼들
        self._create_menu_button(sidebar, "⚙️ General", self.show_general_settings)
        self._create_menu_button(sidebar, "📋 Monitoring", self.show_monitoring_settings)
        self._create_menu_button(sidebar, "✓ Whitelist", self.show_whitelist_settings)
        self._create_menu_button(sidebar, "📜 History", self.show_history_settings)
        self._create_menu_button(sidebar, "🎨 Appearance", self.show_appearance_settings)
        
        # 하단 정보
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
        """메뉴 버튼 생성"""
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
        """컨텐츠 영역 초기화"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_general_settings(self):
        """일반 설정 탭"""
        self._clear_content()
        self.current_tab = 'general'
        
        # 헤더
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
        
        # 설정 섹션
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
        """모니터링 설정 탭"""
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
        
        # 텍스트 모니터링
        self._create_setting_card(
            self.content_frame,
            "Text Content",
            "Monitor and confirm text paste operations",
            lambda p: self._create_toggle(p, "monitor_text", self.config.get("monitor_text"))
        )
        
        # 이미지 모니터링
        self._create_setting_card(
            self.content_frame,
            "Image Content",
            "Monitor and confirm image paste operations",
            lambda p: self._create_toggle(p, "monitor_image", self.config.get("monitor_image"))
        )
    
    def show_whitelist_settings(self):
        """화이트리스트 설정 탭"""
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
        
        # 화이트리스트 카드
        card = ctk.CTkFrame(
            self.content_frame,
            fg_color="#2D2D2D",
            corner_radius=10
        )
        card.pack(padx=30, pady=10, fill="both", expand=True)
        
        # 입력 프레임
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
        
        # 화이트리스트 목록
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
        """히스토리 설정 탭"""
        self._clear_content()
        self.current_tab = 'history'  # 현재 탭 표시
        
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
        
        # 히스토리 카드
        card = ctk.CTkFrame(
            self.content_frame,
            fg_color="#2D2D2D",
            corner_radius=10
        )
        card.pack(padx=30, pady=10, fill="both", expand=True)
        
        # 히스토리 목록
        list_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="#1E1E1E",
            corner_radius=10,
            height=400
        )
        list_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # 히스토리 데이터 가져오기
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
        """히스토리 항목 생성 - grid 레이아웃으로 완벽한 수평 정렬"""
        import time
        import pyperclip
        from PIL import ImageTk
        
        # 메인 항목 프레임 (가변 높이 - 내용에 따라 자동 조절)
        item_frame = ctk.CTkFrame(
            parent,
            fg_color="#2D2D2D",
            corner_radius=10
        )
        item_frame.pack(fill="x", padx=5, pady=3)
        # pack_propagate는 True로 유지 (기본값) - 내용물에 맞게 크기 조절
        
        # Grid 설정 (4컬럼: 아이콘 | 정보 | 콘텐츠 | 버튼) - minsize 제거하여 컴팩트하게
        item_frame.grid_columnconfigure(0, weight=0)  # 아이콘 - minsize 제거
        item_frame.grid_columnconfigure(1, weight=1)  # 앱 정보 - weight 조정
        item_frame.grid_columnconfigure(2, weight=2)  # 콘텐츠
        item_frame.grid_columnconfigure(3, weight=0)  # 버튼
        item_frame.grid_rowconfigure(0, weight=0)  # weight=0으로 수직 확장 방지
        
        # === 컬럼 0: 아이콘 (상단 정렬) ===
        type_icon = "📝" if history_item["type"] == "text" else "🖼️"
        is_sensitive = history_item.get("is_sensitive", False)
        
        icon_label = ctk.CTkLabel(
            item_frame,
            text=type_icon,
            font=("Segoe UI", 24),  # 폰트 크기 더 줄임 (28 -> 24)
            text_color="#EF4444" if is_sensitive else "#3B82F6"
        )
        icon_label.grid(row=0, column=0, padx=(8, 3), pady=(5, 5), sticky="n")  # pady 극도로 최소화, sticky="n"
        
        # === 컬럼 1: 앱 정보 (프로그램명 + 시간 + 타겟) - 상단 정렬 ===
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=5, pady=(5, 5), sticky="n")  # pady 극도로 최소화, sticky="n"
        
        app_name = history_item.get("app_name", history_item.get("process", "Unknown"))
        timestamp = history_item.get("timestamp", 0)
        time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
        target_app = history_item.get("target_app", history_item.get("process", "Unknown"))
        is_auto_approved = history_item.get("auto_approved", False)
        
        # 앱 이름
        app_label = ctk.CTkLabel(
            info_frame,
            text=f"📦 {app_name}",
            font=("Segoe UI", 11, "bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        app_label.pack(anchor="w", pady=(0, 2))
        
        # 타겟 앱 (더 눈에 띄게)
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
        
        # 시간 + 민감 정보 표시
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
        
        # === 컬럼 2: 콘텐츠 (텍스트 또는 이미지) - 직접 grid에 배치 ===
        if history_item["type"] == "text":
            # 텍스트 미리보기
            preview_text = history_item.get("preview", "")[:85]
            if len(history_item.get("preview", "")) > 85:
                preview_text += "..."
            
            preview_label = ctk.CTkLabel(
                item_frame,
                text=preview_text,
                font=("Segoe UI", 10),
                text_color="#CCCCCC",
                anchor="w",
                wraplength=240,
                justify="left"
            )
            preview_label.grid(row=0, column=2, padx=5, pady=(5, 5), sticky="nw")  # 직접 grid 배치
            
        elif history_item["type"] == "image":
            # 이미지 섬네일 - 직접 배치로 여백 제거
            try:
                thumbnail = history_item.get("full_content") or history_item.get("preview")
                if thumbnail:
                    ctk_image = ctk.CTkImage(
                        light_image=thumbnail,
                        dark_image=thumbnail,
                        size=(45, 45)  # 크기 더 축소 (48 -> 45)
                    )
                    
                    img_label = ctk.CTkLabel(
                        item_frame,
                        image=ctk_image,
                        text=""  # 텍스트 공간 제거
                    )
                    img_label.grid(row=0, column=2, padx=5, pady=(2, 2), sticky="n")  # 직접 grid 배치, pady 극소화
            except Exception as e:
                error_label = ctk.CTkLabel(
                    item_frame,
                    text="Image preview unavailable",
                    font=("Segoe UI", 9),
                    text_color="#666666"
                )
                error_label.grid(row=0, column=2, padx=5, pady=(5, 5), sticky="nw")
        
        # === 컬럼 3: Re-copy 버튼 (상단 정렬) ===
        def recopy():
            content = history_item.get("content")
            content_type = history_item.get("type")
            
            if content_type == "text" and content:
                # 텍스트 복사
                pyperclip.copy(content)
                print(f"✓ 텍스트 클립보드에 복사됨")
            elif content_type == "image" and content:
                # 이미지 복사 (클립보드에 설정)
                if self.app and hasattr(self.app.monitor, '_set_clipboard_image'):
                    import threading
                    threading.Thread(
                        target=self.app.monitor._set_clipboard_image,
                        args=(content,),
                        daemon=True
                    ).start()
                    print(f"✓ 이미지 클립보드에 복사됨")
        
        # 버튼을 grid로 배치하여 상단 정렬
        recopy_btn = ctk.CTkButton(
            item_frame,
            text="📋 Copy",  # 텍스트 축약
            width=80,  # width 더 줄임
            height=32,  # height 더 줄임 (36 -> 32)
            corner_radius=6,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            font=("Segoe UI", 9, "bold"),  # 폰트 크기 더 줄임
            command=recopy
        )
        recopy_btn.grid(row=0, column=3, padx=8, pady=(5, 5), sticky="n")  # pady 극도로 최소화
    
    def show_appearance_settings(self):
        """외관 설정 탭"""
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
        
        # 투명도 설정
        self._create_setting_card(
            self.content_frame,
            "Popup Opacity",
            "Adjust the transparency of confirmation popups",
            self._create_opacity_slider
        )
    
    def _create_setting_card(self, parent, title, description, content_creator):
        """설정 카드 생성"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#2D2D2D",
            corner_radius=10
        )
        card.pack(padx=30, pady=10, fill="x")
        
        # 상단 텍스트
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
        
        # 컨텐츠 영역
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(padx=20, pady=(10, 20), fill="x")
        
        content_creator(content_frame)
    
    def _create_toggle(self, parent, config_key, current_value):
        """토글 스위치 생성"""
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
        """설정 토글"""
        new_value = switch.get() == 1
        self.config.set(config_key, new_value)
        switch.configure(text="Enabled" if new_value else "Disabled")
    
    def _create_status_content(self, parent):
        """상태 컨텐츠 생성"""
        status_label = ctk.CTkLabel(
            parent,
            text="● Active",
            font=("Segoe UI", 13),
            text_color="#10B981"
        )
        status_label.pack(anchor="w")
    
    def _create_startup_content(self, parent):
        """시작 옵션 컨텐츠 생성"""
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
        """투명도 슬라이더 생성"""
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
        """투명도 업데이트"""
        self.config.set("popup_opacity", value)
        label.configure(text=f"{int(value * 100)}%")
    
    def _add_whitelist_item(self, entry):
        """화이트리스트 항목 추가"""
        process_name = entry.get().strip()
        if process_name:
            self.config.add_to_whitelist(process_name)
            entry.delete(0, 'end')
            self._refresh_whitelist()
    
    def _refresh_whitelist(self):
        """화이트리스트 목록 새로고침"""
        # 기존 항목 제거
        for widget in self.whitelist_container.winfo_children():
            widget.destroy()
        
        # 화이트리스트 가져오기
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
        """화이트리스트 항목 생성 (앱 아이콘 비동기 로드)"""
        item_frame = ctk.CTkFrame(
            self.whitelist_container,
            fg_color="#2D2D2D",
            corner_radius=8,
            height=50
        )
        item_frame.pack(fill="x", padx=5, pady=5)
        item_frame.pack_propagate(False)
        
        # 기본 아이콘 먼저 표시
        icon_label = ctk.CTkLabel(
            item_frame,
            text="📦",
            font=("Segoe UI", 18),
            text_color="#FFFFFF"
        )
        icon_label.pack(side="left", padx=(15, 5), pady=10)
        
        # 프로세스 이름
        name_label = ctk.CTkLabel(
            item_frame,
            text=process_name,
            font=("Segoe UI", 12),
            text_color="#FFFFFF",
            anchor="w"
        )
        name_label.pack(side="left", padx=(5, 10), pady=10)
        
        # 삭제 버튼
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
        
        # 비동기로 아이콘 추출 시도 (선택적)
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
        
        # 백그라운드에서 아이콘 로드
        threading.Thread(target=load_icon_async, daemon=True).start()
    
    def _extract_process_icon_simple(self, process_name: str) -> Image.Image:
        """프로세스 실행 파일에서 고품질 아이콘 추출 (LANCZOS 리사이징)"""
        try:
            # 주요 경로만 확인
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
            
            # 고해상도 아이콘 추출
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            
            # large 아이콘 사용 (더 고품질)
            icon_handle = large[0] if large else (small[0] if small else None)
            
            if icon_handle:
                # 아이콘 크기 가져오기
                ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
                ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
                
                # DC 생성
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                hdc_mem = hdc.CreateCompatibleDC()
                hdc_mem.SelectObject(hbmp)
                
                # 투명 배경으로 설정
                hdc_mem.FillSolidRect((0, 0, ico_x, ico_y), win32api.RGB(0, 0, 0))
                
                # 아이콘 그리기
                hdc_mem.DrawIcon((0, 0), icon_handle)
                
                # 비트맵 데이터 추출
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer(
                    'RGB',
                    (ico_x, ico_y),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                # LANCZOS 필터로 고품질 리사이징
                img_resized = img.resize((32, 32), Image.Resampling.LANCZOS)
                
                # 리소스 해제
                if large:
                    for icon in large:
                        win32gui.DestroyIcon(icon)
                if small:
                    for icon in small:
                        win32gui.DestroyIcon(icon)
                
                return img_resized
            
        except Exception as e:
            # 조용히 실패 처리
            pass
        
        return None
    
    def _extract_process_icon(self, process_name: str) -> Image.Image:
        """프로세스 실행 파일에서 아이콘 추출"""
        try:
            # 일반적인 프로그램 경로들
            search_paths = [
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), '**', process_name),
                os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), '**', process_name),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), '**', process_name),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', '**', process_name),
            ]
            
            # 실행 파일 찾기
            import glob
            exe_path = None
            for path_pattern in search_paths:
                matches = glob.glob(path_pattern, recursive=True)
                if matches:
                    exe_path = matches[0]
                    break
            
            if not exe_path:
                return None
            
            # 아이콘 추출
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
            print(f"아이콘 추출 실패 ({process_name}): {e}")
        
        return None
    
    def _remove_whitelist_item(self, process_name):
        """화이트리스트 항목 제거"""
        self.config.remove_from_whitelist(process_name)
        self._refresh_whitelist()
    
    def _on_window_close(self):
        """창 닫기 이벤트"""
        if self.on_close:
            self.on_close()
        self.window.destroy()
    
    def run(self):
        """설정 창 실행"""
        self.show()
        self.window.mainloop()
