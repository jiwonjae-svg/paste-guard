"""
Paste Guardian - 메인 애플리케이션
클립보드 붙여넣기 보안 프로그램
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
    """메인 애플리케이션 클래스"""
    
    def __init__(self):
        # 설정 관리자
        self.config = ConfigManager()
        
        # 클립보드 모니터
        self.monitor = ClipboardMonitor(self.on_paste_request)
        
        # UI 큐 (백그라운드 스레드에서 UI 업데이트용)
        self.ui_queue = queue.Queue()
        
        # 시스템 트레이 아이콘
        self.tray_icon = None
        
        # 설정 창
        self.settings_window = None
        
        # 현재 표시 중인 확인 팝업
        self.current_popup = None
        
        # 메인 이벤트 루프 (숨겨진 창)
        self.root = None
        
    def start(self):
        """애플리케이션 시작"""
        print("=" * 50)
        print("🔒 Paste Guardian 시작")
        print("=" * 50)
        print("✓ 클립보드 모니터링 활성화됨")
        print("✓ 시스템 트레이 아이콘 생성 중...")
        print("\n[안내]")
        print("- 시스템 트레이(작업 표시줄 오른쪽 하단)에서 아이콘을 확인하세요")
        print("- 아이콘을 우클릭하여 'Settings'를 선택하세요")
        print("- Ctrl+V를 누르면 확인 팝업이 나타납니다")
        print("=" * 50)
        
        # customtkinter 숨겨진 루트 창 생성
        self.root = ctk.CTk()
        self.root.withdraw()  # 창 숨기기
        
        # 클립보드 모니터링 시작
        self.monitor.start()
        
        # 시스템 트레이 아이콘 시작 (별도 스레드)
        tray_thread = threading.Thread(target=self._start_tray_icon, daemon=True)
        tray_thread.start()
        
        # UI 큐 처리
        self._process_ui_queue()
        
        # 첫 실행 시 설정 창 자동 표시 (약간의 지연 후)
        self.root.after(500, lambda: self._show_settings())
        
        # 메인 루프
        self.root.mainloop()
    
    def _start_tray_icon(self):
        """시스템 트레이 아이콘 시작"""
        # 아이콘 이미지 생성
        icon_image = self._create_tray_icon()
        
        # 메뉴 생성
        menu = Menu(
            MenuItem("Settings", self._show_settings),
            MenuItem("Exit", self._quit_application)
        )
        
        # 트레이 아이콘 생성
        self.tray_icon = Icon(
            "PasteGuardian",
            icon_image,
            "Paste Guardian - Active",
            menu
        )
        
        # 트레이 아이콘 실행
        self.tray_icon.run()
    
    def _create_tray_icon(self):
        """트레이 아이콘 이미지 생성"""
        # 간단한 아이콘 생성 (64x64)
        img = Image.new('RGB', (64, 64), color='#3B82F6')
        draw = ImageDraw.Draw(img)
        
        # 잠금 아이콘 그리기 (간단한 버전)
        draw.rectangle([20, 28, 44, 50], fill='white', outline='white')
        draw.ellipse([24, 20, 40, 36], fill='#3B82F6', outline='white', width=3)
        
        return img
    
    def _process_ui_queue(self):
        """UI 큐 처리 (주기적으로 체크)"""
        try:
            while not self.ui_queue.empty():
                callback = self.ui_queue.get_nowait()
                callback()
        except queue.Empty:
            pass
        
        # 100ms마다 다시 체크
        if self.root:
            self.root.after(100, self._process_ui_queue)
    
    def on_paste_request(self, clipboard_data: dict, process_name: str):
        """붙여넣기 요청 콜백"""
        print(f"\n[붙여넣기 요청 수신]")
        print(f"- 프로세스: {process_name}")
        print(f"- 데이터 타입: {clipboard_data.get('type')}")
        
        # 화이트리스트 확인
        if process_name in self.config.get_whitelist():
            print(f"✓ 화이트리스트 프로세스: {process_name} - 자동 허용")
            self._allow_paste(clipboard_data)
            return
        
        # 콘텐츠 타입별 모니터링 확인
        content_type = clipboard_data.get("type")
        if not self.config.is_monitoring_enabled(content_type):
            print(f"✓ {content_type} 모니터링 비활성화 - 자동 허용")
            self._allow_paste(clipboard_data)
            return
        
        print("→ 확인 팝업 표시 중...")
        
        # 확인 팝업 표시 (UI 큐에 추가)
        def show_popup():
            self._show_confirmation_popup(clipboard_data, process_name)
        
        self.ui_queue.put(show_popup)
    
    def _show_confirmation_popup(self, clipboard_data: dict, process_name: str):
        """확인 팝업 표시"""
        print("확인 팝업 생성 중...")
        
        if self.current_popup:
            self.current_popup.close()
        
        opacity = self.config.get("popup_opacity", 0.95)
        
        try:
            self.current_popup = ConfirmationPopup(
                clipboard_data=clipboard_data,
                process_name=process_name,
                on_confirm=lambda data: self._on_popup_confirm(data),
                on_cancel=self._on_popup_cancel,
                opacity=opacity
            )
            
            self.current_popup.show()
            print("✓ 확인 팝업 표시 완료")
        except Exception as e:
            print(f"✗ 팝업 표시 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_popup_confirm(self, clipboard_data: dict):
        """팝업 확인 버튼 클릭"""
        print("붙여넣기 승인")
        self._allow_paste(clipboard_data)
        self.current_popup = None
    
    def _on_popup_cancel(self):
        """팝업 취소 버튼 클릭"""
        print("붙여넣기 거부")
        self.current_popup = None
    
    def _allow_paste(self, clipboard_data: dict):
        """붙여넣기 허용"""
        if clipboard_data["type"] == "text":
            # 텍스트 붙여넣기 수행
            threading.Thread(
                target=ClipboardMonitor.perform_paste,
                args=(clipboard_data["content"],),
                daemon=True
            ).start()
    
    def _show_settings(self, icon=None, item=None):
        """설정 창 표시"""
        def show():
            if not self.settings_window or not self.settings_window.window or not self.settings_window.window.winfo_exists():
                self.settings_window = SettingsWindow(self.config, parent=self.root)
                self.settings_window.show()
            else:
                self.settings_window.window.focus()
                self.settings_window.window.lift()
        
        # 메인 스레드에서 직접 실행하거나 큐에 추가
        if self.root and threading.current_thread() == threading.main_thread():
            show()
        else:
            self.ui_queue.put(show)
    
    def _quit_application(self, icon=None, item=None):
        """애플리케이션 종료"""
        print("애플리케이션 종료 중...")
        
        # 모니터링 중지
        self.monitor.stop()
        
        # 트레이 아이콘 중지
        if self.tray_icon:
            self.tray_icon.stop()
        
        # 설정 저장
        self.config.save_config()
        
        # 메인 루프 종료
        if self.root:
            self.root.quit()
        
        sys.exit(0)


def main():
    """메인 함수"""
    # customtkinter 기본 설정
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # 애플리케이션 생성 및 실행
    app = PasteGuardian()
    
    try:
        app.start()
    except KeyboardInterrupt:
        print("\n키보드 인터럽트 감지")
        app._quit_application()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
