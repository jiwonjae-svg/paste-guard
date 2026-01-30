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
    
    def __init__(self, config_manager: ConfigManager, parent=None, on_close: Callable = None):
        self.config = config_manager
        self.parent = parent
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
    
    def show_appearance_settings(self):
        """외관 설정 탭"""
        self._clear_content()
        
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
        """화이트리스트 항목 생성 (앱 아이콘 포함)"""
        item_frame = ctk.CTkFrame(
            self.whitelist_container,
            fg_color="#2D2D2D",
            corner_radius=8,
            height=50
        )
        item_frame.pack(fill="x", padx=5, pady=5)
        item_frame.pack_propagate(False)
        
        # 아이콘 추출 시도
        icon_label = None
        try:
            icon_image = self._extract_process_icon(process_name)
            if icon_image:
                ctk_image = ctk.CTkImage(
                    light_image=icon_image,
                    dark_image=icon_image,
                    size=(24, 24)
                )
                icon_label = ctk.CTkLabel(
                    item_frame,
                    image=ctk_image,
                    text=""
                )
                icon_label.pack(side="left", padx=(15, 5), pady=10)
        except:
            pass
        
        # 프로세스 이름
        prefix = "" if icon_label else "📦 "
        name_label = ctk.CTkLabel(
            item_frame,
            text=f"{prefix}{process_name}",
            font=("Segoe UI", 12),
            text_color="#FFFFFF",
            anchor="w"
        )
        name_label.pack(side="left", padx=(5 if icon_label else 15, 10), pady=10)
        
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
