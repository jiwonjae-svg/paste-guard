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
        print(f"[Resource] Using PyInstaller temp path: {base_path}")
    except AttributeError:
        # Development mode: use the directory containing the script
        # Go up one level from utils/ to get project root
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        print(f"[Resource] Using development path: {base_path}")
    
    full_path = os.path.join(base_path, relative_path)
    print(f"[Resource] Full resource path: {full_path}")
    print(f"[Resource] File exists: {os.path.exists(full_path)}")
    
    return full_path
