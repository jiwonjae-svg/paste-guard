"""
설정 관리 모듈
사용자 설정을 저장하고 불러오는 기능 제공
"""
import json
import os
from typing import Dict, List, Any


class ConfigManager:
    """애플리케이션 설정을 관리하는 클래스"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
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
