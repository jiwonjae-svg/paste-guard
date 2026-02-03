"""
Resource utilities for handling file paths in both development and PyInstaller environments
"""
import sys
import os


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource file.
    Works for both development and PyInstaller executable environments.
    
    Args:
        relative_path: Relative path from project root (e.g., 'icon.ico')
    
    Returns:
        Absolute path to the resource file
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Development mode: use the directory containing the script
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    return os.path.join(base_path, relative_path)
