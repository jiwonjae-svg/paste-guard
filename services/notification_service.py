"""
Notification Service Module
Handles all notification and alert logic
"""
from typing import Callable, Optional, Dict, Any
from enum import Enum


class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class NotificationService:
    """Manages application notifications and alerts"""
    
    def __init__(self):
        """Initialize NotificationService"""
        self._listeners: Dict[str, list] = {
            "paste_request": [],
            "paste_approved": [],
            "paste_denied": [],
            "whitelist_added": [],
            "config_changed": [],
            "error": []
        }
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to an event
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Unsubscribe from an event
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove
        """
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
    
    def notify(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Notify all subscribers of an event
        
        Args:
            event_type: Type of event that occurred
            data: Optional data to pass to callbacks
        """
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    if data:
                        callback(data)
                    else:
                        callback()
                except Exception as e:
                    print(f"Notification callback error: {e}")
    
    def notify_paste_request(
        self,
        clipboard_data: Dict[str, Any],
        process_name: str,
        auto_approved: bool = False
    ) -> None:
        """
        Notify about a paste request
        
        Args:
            clipboard_data: Clipboard data
            process_name: Name of requesting process
            auto_approved: Whether auto-approved
        """
        self.notify("paste_request", {
            "clipboard_data": clipboard_data,
            "process_name": process_name,
            "auto_approved": auto_approved,
            "timestamp": __import__('time').time()
        })
        
        print(f"\n[Paste Request]")
        print(f"- Process: {process_name}")
        print(f"- Type: {clipboard_data.get('type')}")
        if auto_approved:
            print(f"- Status: Auto-approved")
    
    def notify_paste_approved(
        self,
        clipboard_data: Dict[str, Any],
        process_name: str,
        added_to_whitelist: bool = False
    ) -> None:
        """
        Notify about paste approval
        
        Args:
            clipboard_data: Clipboard data
            process_name: Name of process
            added_to_whitelist: Whether added to whitelist
        """
        self.notify("paste_approved", {
            "clipboard_data": clipboard_data,
            "process_name": process_name,
            "added_to_whitelist": added_to_whitelist
        })
        
        print(f"✓ Paste approved for {process_name}")
        if added_to_whitelist:
            print(f"✓ Added to whitelist: {process_name}")
    
    def notify_paste_denied(self, process_name: str) -> None:
        """
        Notify about paste denial
        
        Args:
            process_name: Name of process
        """
        self.notify("paste_denied", {"process_name": process_name})
        print(f"✗ Paste denied for {process_name}")
    
    def notify_whitelist_added(self, process_name: str) -> None:
        """
        Notify about whitelist addition
        
        Args:
            process_name: Name of process added
        """
        self.notify("whitelist_added", {"process_name": process_name})
        print(f"✓ Whitelist updated: {process_name}")
    
    def notify_config_changed(self, setting: str, value: Any) -> None:
        """
        Notify about configuration change
        
        Args:
            setting: Name of setting changed
            value: New value
        """
        self.notify("config_changed", {"setting": setting, "value": value})
        print(f"✓ Config updated: {setting} = {value}")
    
    def notify_error(self, error_type: str, message: str, exception: Exception = None) -> None:
        """
        Notify about an error
        
        Args:
            error_type: Type of error
            message: Error message
            exception: Optional exception object
        """
        self.notify("error", {
            "error_type": error_type,
            "message": message,
            "exception": exception
        })
        
        print(f"✗ Error ({error_type}): {message}")
        if exception:
            print(f"  Details: {str(exception)}")
    
    def log_info(self, message: str) -> None:
        """
        Log an informational message
        
        Args:
            message: Message to log
        """
        print(f"ℹ {message}")
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message
        
        Args:
            message: Warning message
        """
        print(f"⚠ {message}")
    
    def log_success(self, message: str) -> None:
        """
        Log a success message
        
        Args:
            message: Success message
        """
        print(f"✓ {message}")


# Global instance
notification_service = NotificationService()
