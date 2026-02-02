"""
History Service Module
Manages clipboard history with encryption support
"""
import json
import time
from typing import Dict, List, Any
from pathlib import Path

from services.security_service import SecurityService
from utils.path_utils import path_manager


class HistoryService:
    """Manages clipboard history with encryption"""
    
    def __init__(self, security_service: SecurityService):
        """
        Initialize HistoryService
        
        Args:
            security_service: SecurityService instance for encryption
        """
        self.security = security_service
        self.history_file = path_manager.get_data_path("history.json")
        self.max_history_items = 10
        self._history_cache: List[Dict[str, Any]] = []
    
    def load_history(self) -> List[Dict[str, Any]]:
        """
        Load clipboard history from file with decryption
        
        Returns:
            List of history items
        """
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                encrypted_history = json.load(f)
            
            # Decrypt sensitive fields
            decrypted_history = []
            for item in encrypted_history:
                decrypted_item = self._decrypt_history_item(item)
                decrypted_history.append(decrypted_item)
            
            self._history_cache = decrypted_history
            print(f"✓ Loaded {len(decrypted_history)} history items")
            return decrypted_history
            
        except Exception as e:
            print(f"History load error: {e}")
            return []
    
    def save_history(self, history_items: List[Dict[str, Any]]) -> bool:
        """
        Save clipboard history to file with encryption
        
        Args:
            history_items: List of history items to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Encrypt sensitive fields before saving
            encrypted_history = []
            for item in history_items:
                encrypted_item = self._encrypt_history_item(item)
                encrypted_history.append(encrypted_item)
            
            # Save to file
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(encrypted_history, f, indent=2, ensure_ascii=False)
            
            self._history_cache = history_items
            print(f"✓ Saved {len(history_items)} history items")
            return True
            
        except Exception as e:
            print(f"History save error: {e}")
            return False
    
    def add_history_item(
        self,
        content_type: str,
        content: Any,
        preview: str,
        process_name: str,
        is_sensitive: bool = False,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Add a new item to history
        
        Args:
            content_type: Type of content ('text' or 'image')
            content: The actual content
            preview: Preview text/thumbnail
            process_name: Name of the process
            is_sensitive: Whether content is sensitive
            metadata: Additional metadata
            
        Returns:
            Created history item
        """
        history_item = {
            "timestamp": time.time(),
            "type": content_type,
            "preview": preview,
            "content": content,
            "process": process_name,
            "app_name": process_name.replace('.exe', '').title(),
            "is_sensitive": is_sensitive,
            "metadata": metadata or {}
        }
        
        return history_item
    
    def cleanup_old_items(self, history_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keep only the most recent items
        
        Args:
            history_items: Current history items
            
        Returns:
            Cleaned up history list
        """
        if len(history_items) > self.max_history_items:
            # Sort by timestamp descending and keep only recent items
            sorted_items = sorted(
                history_items,
                key=lambda x: x.get("timestamp", 0),
                reverse=True
            )
            return sorted_items[:self.max_history_items]
        
        return history_items
    
    def get_recent_items(self, count: int = None) -> List[Dict[str, Any]]:
        """
        Get recent history items
        
        Args:
            count: Number of items to return (None = all)
            
        Returns:
            List of recent items
        """
        if count is None:
            return self._history_cache
        
        return self._history_cache[:count]
    
    def clear_history(self) -> bool:
        """
        Clear all history
        
        Returns:
            True if successful
        """
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            self._history_cache = []
            print("✓ History cleared")
            return True
        except Exception as e:
            print(f"History clear error: {e}")
            return False
    
    def _encrypt_history_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in a history item
        
        Args:
            item: History item to encrypt
            
        Returns:
            Encrypted history item
        """
        encrypted_item = item.copy()
        
        # Encrypt text content if marked as sensitive
        if item.get("is_sensitive") and item.get("type") == "text":
            content = item.get("content", "")
            if isinstance(content, str) and content:
                encrypted_item["content"] = self.security.encrypt_string(content)
                encrypted_item["_content_encrypted"] = True
            
            preview = item.get("preview", "")
            if isinstance(preview, str) and preview:
                encrypted_item["preview"] = self.security.encrypt_string(preview)
                encrypted_item["_preview_encrypted"] = True
        
        # Don't encrypt images, just encode as base64 (already handled elsewhere)
        
        return encrypted_item
    
    def _decrypt_history_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in a history item
        
        Args:
            item: Encrypted history item
            
        Returns:
            Decrypted history item
        """
        decrypted_item = item.copy()
        
        # Decrypt content if it was encrypted
        if item.get("_content_encrypted"):
            encrypted_content = item.get("content", "")
            if encrypted_content:
                decrypted_item["content"] = self.security.decrypt_string(encrypted_content)
            del decrypted_item["_content_encrypted"]
        
        # Decrypt preview if it was encrypted
        if item.get("_preview_encrypted"):
            encrypted_preview = item.get("preview", "")
            if encrypted_preview:
                decrypted_item["preview"] = self.security.decrypt_string(encrypted_preview)
            del decrypted_item["_preview_encrypted"]
        
        return decrypted_item
    
    def export_history(self, export_path: Path, include_sensitive: bool = False) -> bool:
        """
        Export history to a file
        
        Args:
            export_path: Path to export file
            include_sensitive: Whether to include sensitive items
            
        Returns:
            True if successful
        """
        try:
            items_to_export = self._history_cache
            
            if not include_sensitive:
                items_to_export = [
                    item for item in items_to_export
                    if not item.get("is_sensitive", False)
                ]
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(items_to_export, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Exported {len(items_to_export)} items to {export_path}")
            return True
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
