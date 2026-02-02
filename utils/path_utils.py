"""
Path Utility Module
Handles all file path operations with support for both development and production environments
"""
import os
import sys
from pathlib import Path
from typing import Union


class PathManager:
    """Manages file paths for development and production environments"""
    
    def __init__(self):
        """Initialize PathManager with base directory detection"""
        # Determine if running as a bundled executable or as a script
        if getattr(sys, 'frozen', False):
            # Running as compiled executable (PyInstaller)
            self._base_dir = Path(sys.executable).parent
        else:
            # Running as script
            self._base_dir = Path(__file__).parent.parent
    
    @property
    def base_dir(self) -> Path:
        """Get the base directory of the application"""
        return self._base_dir
    
    def get_config_path(self, filename: str = "config.json") -> Path:
        """Get the full path to a configuration file"""
        return self._base_dir / filename
    
    def get_data_path(self, filename: str) -> Path:
        """Get the full path to a data file"""
        return self._base_dir / filename
    
    def get_log_path(self, filename: str = "app.log") -> Path:
        """Get the full path to a log file"""
        logs_dir = self._base_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir / filename
    
    def ensure_directory(self, path: Union[str, Path]) -> Path:
        """Ensure a directory exists, create if it doesn't"""
        path = Path(path) if isinstance(path, str) else path
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_resource_path(self, relative_path: str) -> Path:
        """
        Get absolute path to resource, works for dev and for PyInstaller
        
        Args:
            relative_path: Relative path to the resource
            
        Returns:
            Absolute path to the resource
        """
        if getattr(sys, 'frozen', False):
            # Running in a bundle (PyInstaller)
            base_path = Path(sys._MEIPASS)
        else:
            # Running in normal Python environment
            base_path = self._base_dir
        
        return base_path / relative_path
    
    def get_user_data_dir(self) -> Path:
        """
        Get user-specific data directory
        
        Returns:
            Path to user data directory (AppData on Windows)
        """
        if sys.platform == 'win32':
            app_data = os.getenv('APPDATA')
            if app_data:
                user_dir = Path(app_data) / "PasteGuardian"
            else:
                user_dir = self._base_dir / "data"
        else:
            # For other platforms
            home = Path.home()
            user_dir = home / ".pasteguardian"
        
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def is_portable_mode(self) -> bool:
        """
        Check if running in portable mode (config.json in app directory)
        
        Returns:
            True if portable mode, False otherwise
        """
        return (self._base_dir / "config.json").exists()
    
    def resolve_path(self, path: Union[str, Path]) -> Path:
        """
        Resolve a path relative to base directory
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved absolute path
        """
        path = Path(path) if isinstance(path, str) else path
        
        if path.is_absolute():
            return path
        
        return self._base_dir / path


# Global instance
path_manager = PathManager()


def get_app_path(filename: str) -> Path:
    """
    Convenience function to get application file path
    
    Args:
        filename: Name of the file
        
    Returns:
        Full path to the file
    """
    return path_manager.get_data_path(filename)


def get_config_path(filename: str = "config.json") -> Path:
    """
    Convenience function to get configuration file path
    
    Args:
        filename: Name of the configuration file
        
    Returns:
        Full path to the configuration file
    """
    return path_manager.get_config_path(filename)


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Convenience function to ensure directory exists
    
    Args:
        path: Path to directory
        
    Returns:
        Path object to the directory
    """
    return path_manager.ensure_directory(path)
