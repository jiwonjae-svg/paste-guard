"""
클립보드 모니터링 모듈
클립보드 변경 감지 및 붙여넣기 키 이벤트 가로채기
"""
import threading
import time
import pyperclip
import win32clipboard
import win32con
from PIL import Image, ImageGrab
from io import BytesIO
from typing import Callable, Optional, Tuple
import keyboard  # pynput 대신 keyboard 사용
import psutil
import win32gui
import win32process


class ClipboardMonitor:
    """클립보드를 모니터링하고 붙여넣기 이벤트를 처리하는 클래스"""
    
    def __init__(self, on_paste_request: Callable):
        self.on_paste_request = on_paste_request
        self.running = False
        self.monitor_thread = None
        self.last_clipboard_content = None
        self.paste_pending = False  # 붙여넣기 대기 중
        self.pending_data = None    # 대기 중인 데이터
        
    def start(self):
        """모니터링 시작"""
        if not self.running:
            self.running = True
            
            # keyboard 라이브러리로 Ctrl+V 후킹
            keyboard.add_hotkey('ctrl+v', self._on_paste_hotkey, suppress=True)
            
            print("클립보드 모니터링 시작")
    
    def stop(self):
        """모니터링 중지"""
        self.running = False
        
        # 모든 후킹 해제
        try:
            keyboard.unhook_all_hotkeys()
            keyboard.unhook_all()
        except:
            pass
        
        print("클립보드 모니터링 중지")
    
    def _on_paste_hotkey(self):
        """Ctrl+V 핫키 콜백 - 붙여넣기 차단 및 확인 요청"""
        if not self.running:
            return
            
        print("Ctrl+V 감지됨! (차단됨)")
        self._handle_paste_attempt()
    
    def _handle_paste_attempt(self):
        """붙여넣기 시도 처리"""
        if not self.running:
            print("모니터링이 실행 중이 아닙니다")
            return
        
        print("붙여넣기 시도 감지 - 처리 시작")
        
        # 현재 활성 프로세스 가져오기
        active_process = self._get_active_process()
        print(f"활성 프로세스: {active_process}")
        
        # 클립보드 내용 가져오기
        clipboard_data = self._get_clipboard_data()
        
        if clipboard_data:
            print(f"클립보드 데이터 타입: {clipboard_data.get('type')}")
            # 콜백 호출 (확인 팝업 표시)
            self.on_paste_request(clipboard_data, active_process)
        else:
            print("클립보드에 데이터가 없습니다")
    
    def _get_active_process(self) -> str:
        """현재 활성화된 프로세스 이름 가져오기"""
        try:
            # 활성 윈도우 핸들 가져오기
            hwnd = win32gui.GetForegroundWindow()
            # 프로세스 ID 가져오기
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            # 프로세스 이름 가져오기
            process = psutil.Process(pid)
            return process.name()
        except Exception as e:
            print(f"프로세스 정보 가져오기 실패: {e}")
            return "unknown"
    
    def _get_clipboard_data(self) -> Optional[dict]:
        """클립보드 데이터 가져오기"""
        try:
            # 이미지 확인
            image = ImageGrab.grabclipboard()
            if image:
                return {
                    "type": "image",
                    "content": image,
                    "preview": self._create_image_preview(image)
                }
            
            # 텍스트 확인
            text = pyperclip.paste()
            if text:
                return {
                    "type": "text",
                    "content": text,
                    "preview": text[:200] + ("..." if len(text) > 200 else "")
                }
            
        except Exception as e:
            print(f"클립보드 데이터 가져오기 실패: {e}")
        
        return None
    
    def _create_image_preview(self, image: Image.Image) -> Image.Image:
        """이미지 미리보기 생성 (썸네일)"""
        try:
            thumbnail = image.copy()
            thumbnail.thumbnail((150, 150), Image.Resampling.LANCZOS)
            return thumbnail
        except Exception as e:
            print(f"이미지 미리보기 생성 실패: {e}")
            return image
    
    @staticmethod
    def perform_paste(content: str):
        """실제 붙여넣기 수행"""
        try:
            # 승인된 내용으로 클립보드 업데이트
            pyperclip.copy(content)
            
            # 짧은 대기
            time.sleep(0.1)
            
            # keyboard 라이브러리로 Ctrl+V 시뮬레이션
            keyboard.press_and_release('ctrl+v')
            
            print("✓ 붙여넣기 실행됨")
            
        except Exception as e:
            print(f"붙여넣기 수행 실패: {e}")
