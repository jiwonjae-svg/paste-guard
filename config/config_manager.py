"""
Configuration management module
Provides functionality to save and load user settings
"""
import json
import os
import base64
from typing import Dict, List, Any
from io import BytesIO


class ConfigManager:
    """Class to manage application settings"""
    
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
        """Load configuration file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with default config (handles new config items)
                    return {**self.default_config, **loaded_config}
            except Exception as e:
                print(f"Failed to load configuration file: {e}")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self) -> bool:
        """Save current settings to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save configuration file: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def get_whitelist(self) -> List[str]:
        """Get whitelist"""
        return self.config.get("whitelist", [])
    
    def add_to_whitelist(self, process_name: str) -> None:
        """Add process to whitelist"""
        whitelist = self.get_whitelist()
        if process_name not in whitelist:
            whitelist.append(process_name)
            self.set("whitelist", whitelist)
    
    def remove_from_whitelist(self, process_name: str) -> None:
        """Remove process from whitelist"""
        whitelist = self.get_whitelist()
        if process_name in whitelist:
            whitelist.remove(process_name)
            self.set("whitelist", whitelist)
    
    def is_monitoring_enabled(self, content_type: str) -> bool:
        """Check if monitoring is enabled for specific content type"""
        if content_type == "text":
            return self.config.get("monitor_text", True)
        elif content_type == "image":
            return self.config.get("monitor_image", True)
        return True
    
    def save_history(self, history_list: List[Dict[str, Any]]) -> bool:
        """Save clipboard history to file"""
        try:
            # Save images by encoding to Base64
            serializable_history = []
            for item in history_list:
                history_item = item.copy()
                
                # Process image data
                if history_item.get("type") == "image":
                    # Encode preview (if image object)
                    if history_item.get("preview"):
                        try:
                            from PIL import Image
                            preview = history_item["preview"]
                            if isinstance(preview, Image.Image):
                                buffer = BytesIO()
                                preview.save(buffer, format="PNG")
                                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                                history_item["preview"] = img_base64
                        except Exception as e:
                            print(f"preview encoding failed: {e}")
                            history_item["preview"] = None
                    
                    # Encode full_content
                    if history_item.get("full_content"):
                        try:
                            from PIL import Image
                            img = history_item["full_content"]
                            if isinstance(img, Image.Image):
                                buffer = BytesIO()
                                img.save(buffer, format="PNG")
                                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                                history_item["full_content"] = img_base64
                        except Exception as e:
                            print(f"full_content encoding failed: {e}")
                            history_item["full_content"] = None
                    
                    # Encode content
                    if history_item.get("content"):
                        try:
                            from PIL import Image
                            img = history_item["content"]
                            if isinstance(img, Image.Image):
                                buffer = BytesIO()
                                img.save(buffer, format="PNG")
                                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                                history_item["content"] = img_base64
                        except Exception as e:
                            print(f"content encoding failed: {e}")
                            history_item["content"] = None
                
                serializable_history.append(history_item)
            
            # Save to JSON file
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_history, f, indent=4, ensure_ascii=False)
            print(f"✓ {len(serializable_history)} history items saved")
            return True
        except Exception as e:
            import traceback
            print(f"History save failed: {e}")
            print(f"Detailed error: {traceback.format_exc()}")
            return False
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load saved clipboard history"""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            # Restore Base64 encoded images
            restored_history = []
            for item in history_data:
                history_item = item.copy()
                
                if history_item.get("type") == "image":
                    # Decode preview
                    if history_item.get("preview") and isinstance(history_item["preview"], str):
                        try:
                            from PIL import Image
                            img_data = base64.b64decode(history_item["preview"])
                            img = Image.open(BytesIO(img_data))
                            history_item["preview"] = img
                        except Exception as e:
                            print(f"preview decoding failed: {e}")
                            history_item["preview"] = None
                    
                    # Decode full_content
                    if history_item.get("full_content") and isinstance(history_item["full_content"], str):
                        try:
                            from PIL import Image
                            img_data = base64.b64decode(history_item["full_content"])
                            img = Image.open(BytesIO(img_data))
                            history_item["full_content"] = img
                        except Exception as e:
                            print(f"full_content decoding failed: {e}")
                            history_item["full_content"] = None
                    
                    # Decode content
                    if history_item.get("content") and isinstance(history_item["content"], str):
                        try:
                            from PIL import Image
                            img_data = base64.b64decode(history_item["content"])
                            img = Image.open(BytesIO(img_data))
                            history_item["content"] = img
                        except Exception as e:
                            print(f"content decoding failed: {e}")
                            history_item["content"] = None
                
                restored_history.append(history_item)
            
            return restored_history
        except Exception as e:
            print(f"History load failed: {e}")
            return []
