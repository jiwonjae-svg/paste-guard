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
        self._allow_next_paste = False  # 다음 붙여넣기 허용 플래그 (무한 루프 방지)
        self._processing = False  # 처리 중 플래그
        
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
        
        # 무한 루프 방지: 승인된 붙여넣기면 통과
        if self._allow_next_paste:
            print("✓ 승인된 붙여넣기 통과")
            self._allow_next_paste = False
            # suppress=True에도 불구하고 이미 차단되었으므로 여기서는 아무것도 하지 않음
            return
        
        # 중복 처리 방지
        if self._processing:
            print("⚠️ 이미 처리 중...")
            return
        
        self._processing = True
        print("Ctrl+V 감지됨! (차단됨)")
        
        try:
            # 붙여넣기 시도 처리
            self._handle_paste_attempt()
        finally:
            self._processing = False
    
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
                    "preview": self._create_image_preview(image),
                    "is_sensitive": False
                }
            
            # 텍스트 확인
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
            print(f"클립보드 데이터 가져오기 실패: {e}")
        
        return None
    
    def _check_sensitive_data(self, text: str) -> bool:
        """민감 정보 패턴 감지 (이메일, 전화번호, 카드번호)"""
        import re
        
        patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 이메일
            r'\b\d{2,4}[-.]?\d{3,4}[-.]?\d{4}\b',  # 전화번호
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # 카드번호
            r'\b\d{6}[-]?\d{7}\b',  # 주민등록번호
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                print(f"⚠️ 민감 정보 감지: {pattern}")
                return True
        
        return False
    
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
    
    @staticmethod
    def perform_paste_with_focus(content: str, content_type: str = "text", image_data=None):
        """포커스 복원을 통한 실제 붙여넣기 수행 (텍스트 및 이미지 지원)"""
        try:
            # 1. 클립보드에 내용 설정
            if content_type == "text":
                pyperclip.copy(content)
            elif content_type == "image" and image_data:
                # win32clipboard를 사용한 이미지 처리
                ClipboardMonitor._set_clipboard_image(image_data)
            
            # 2. 현재 활성 윈도우 가져오기 (붙여넣기 대상)
            target_hwnd = win32gui.GetForegroundWindow()
            
            # 3. 팝업이 닫히고 포커스가 복원될 시간 대기
            time.sleep(0.15)
            
            # 4. 타겟 윈도우에 강제 포커스 설정
            if target_hwnd:
                try:
                    win32gui.SetForegroundWindow(target_hwnd)
                    time.sleep(0.05)  # 포커스 안정화
                except:
                    pass
            
            # 5. 실제 붙여넣기 명령 전송
            keyboard.press_and_release('ctrl+v')
            
            print(f"✓ 포커스 복원 붙여넣기 실행됨 ({content_type})")
            
        except Exception as e:
            print(f"포커스 복원 붙여넣기 실패: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def _set_clipboard_image(image):
        """이미지를 win32clipboard를 사용하여 클립보드에 안정적으로 설정 (DIB 포맷)"""
        try:
            from PIL import Image
            import io
            
            # PIL 이미지를 BMP 포맷으로 변환
            output = io.BytesIO()
            
            # RGBA면 RGB로 변환 (투명도 제거)
            if image.mode == 'RGBA':
                # 흰색 배경으로 합성
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # 알파 채널 사용
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # BMP 포맷으로 저장
            image.save(output, 'BMP')
            data = output.getvalue()[14:]  # BMP 헤더 제거 (14 바이트)
            output.close()
            
            # 클립보드 열기 시도 (최대 3회)
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
            
            # 클립보드 비우기 및 DIB 포맷으로 설정
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_DIB, data)
            win32clipboard.CloseClipboard()
            
            print("✓ 이미지를 클립보드에 안정적으로 설정했습니다")
            
        except Exception as e:
            print(f"이미지 클립보드 설정 실패: {e}")
            import traceback
            traceback.print_exc()
            # 실패 시 클립보드 닫기
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
