"""
설정 관리 모듈
사용자 설정을 저장하고 불러오는 기능 제공
"""
import json
import os
import base64
from typing import Dict, List, Any
from io import BytesIO


class ConfigManager:
    """애플리케이션 설정을 관리하는 클래스"""
    
    def __init__(self, config_file: str = "config.json", history_file: str = "history.json"):
        self.config_file = config_file
        self.history_file = history_file
        self.default_config = {
            "monitor_text": True,
            "monitor_image": True,
            "whitelist": [],
            "popup_opacity": 0.95,
            "theme": "dark",
            "accent_color": "#3B82F6"
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일을 불러옵니다"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 기본 설정과 병합 (새로운 설정 항목 추가 대응)
                    return {**self.default_config, **loaded_config}
            except Exception as e:
                print(f"설정 파일 로드 실패: {e}")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self) -> bool:
        """현재 설정을 파일에 저장합니다"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"설정 파일 저장 실패: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값을 가져옵니다"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """설정 값을 변경합니다"""
        self.config[key] = value
        self.save_config()
    
    def get_whitelist(self) -> List[str]:
        """화이트리스트를 가져옵니다"""
        return self.config.get("whitelist", [])
    
    def add_to_whitelist(self, process_name: str) -> None:
        """화이트리스트에 프로세스를 추가합니다"""
        whitelist = self.get_whitelist()
        if process_name not in whitelist:
            whitelist.append(process_name)
            self.set("whitelist", whitelist)
    
    def remove_from_whitelist(self, process_name: str) -> None:
        """화이트리스트에서 프로세스를 제거합니다"""
        whitelist = self.get_whitelist()
        if process_name in whitelist:
            whitelist.remove(process_name)
            self.set("whitelist", whitelist)
    
    def is_monitoring_enabled(self, content_type: str) -> bool:
        """특정 콘텐츠 타입의 모니터링이 활성화되어 있는지 확인합니다"""
        if content_type == "text":
            return self.config.get("monitor_text", True)
        elif content_type == "image":
            return self.config.get("monitor_image", True)
        return True
    
    def save_history(self, history_list: List[Dict[str, Any]]) -> bool:
        """클립보드 히스토리를 파일에 저장합니다"""
        try:
            # 이미지를 Base64로 인코딩하여 저장
            serializable_history = []
            for item in history_list:
                history_item = item.copy()
                
                # 이미지 데이터 처리
                if history_item.get("type") == "image":
                    # full_content 인코딩
                    if history_item.get("full_content"):
                        try:
                            from PIL import Image
                            img = history_item["full_content"]
                            buffer = BytesIO()
                            img.save(buffer, format="PNG")
                            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                            history_item["full_content"] = img_base64
                        except Exception as e:
                            print(f"이미지 인코딩 실패: {e}")
                            history_item["full_content"] = None
                    
                    # content 인코딩
                    if history_item.get("content"):
                        try:
                            from PIL import Image
                            img = history_item["content"]
                            buffer = BytesIO()
                            img.save(buffer, format="PNG")
                            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                            history_item["content"] = img_base64
                        except Exception as e:
                            print(f"이미지 인코딩 실패: {e}")
                            history_item["content"] = None
                
                serializable_history.append(history_item)
            
            # JSON 파일로 저장
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_history, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"히스토리 저장 실패: {e}")
            return False
    
    def load_history(self) -> List[Dict[str, Any]]:
        """저장된 클립보드 히스토리를 불러옵니다"""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            # Base64로 인코딩된 이미지 복원
            restored_history = []
            for item in history_data:
                history_item = item.copy()
                
                if history_item.get("type") == "image":
                    # full_content 디코딩
                    if history_item.get("full_content"):
                        try:
                            from PIL import Image
                            img_data = base64.b64decode(history_item["full_content"])
                            img = Image.open(BytesIO(img_data))
                            history_item["full_content"] = img
                        except Exception as e:
                            print(f"이미지 디코딩 실패: {e}")
                            history_item["full_content"] = None
                    
                    # content 디코딩
                    if history_item.get("content"):
                        try:
                            from PIL import Image
                            img_data = base64.b64decode(history_item["content"])
                            img = Image.open(BytesIO(img_data))
                            history_item["content"] = img
                        except Exception as e:
                            print(f"이미지 디코딩 실패: {e}")
                            history_item["content"] = None
                
                restored_history.append(history_item)
            
            return restored_history
        except Exception as e:
            print(f"히스토리 로드 실패: {e}")
            return []
