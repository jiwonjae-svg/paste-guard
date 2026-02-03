"""
Icon utilities for embedded icon handling
Creates temporary icon file from Base64 data
"""
import base64
import os
import tempfile
import atexit
from utils.icon_data import ICON_DATA

# Global variable to store temp icon path
_temp_icon_path = None


def get_icon_path() -> str:
    """
    Get path to icon file.
    Creates temporary .ico file from embedded Base64 data.
    File is automatically cleaned up on program exit.
    
    Returns:
        str: Path to temporary icon file
    """
    global _temp_icon_path
    
    # Return existing path if already created
    if _temp_icon_path and os.path.exists(_temp_icon_path):
        return _temp_icon_path
    
    try:
        # Decode Base64 data
        icon_bytes = base64.b64decode(ICON_DATA)
        
        # Create temporary file
        fd, _temp_icon_path = tempfile.mkstemp(suffix='.ico', prefix='paste_guardian_')
        
        # Write icon data
        with os.fdopen(fd, 'wb') as f:
            f.write(icon_bytes)
        
        # Register cleanup on exit
        atexit.register(_cleanup_temp_icon)
        
        print(f"[Icon] Temporary icon created: {_temp_icon_path}")
        return _temp_icon_path
        
    except Exception as e:
        print(f"[Icon] Failed to create temporary icon: {e}")
        return None


def _cleanup_temp_icon():
    """Clean up temporary icon file on program exit"""
    global _temp_icon_path
    
    if _temp_icon_path and os.path.exists(_temp_icon_path):
        try:
            os.remove(_temp_icon_path)
            print(f"[Icon] Temporary icon cleaned up: {_temp_icon_path}")
        except:
            pass


def get_icon_image():
    """
    Get PIL Image object from embedded icon data.
    Useful for pystray and other libraries requiring Image objects.
    
    Returns:
        PIL.Image: Icon as PIL Image object
    """
    try:
        from PIL import Image
        import io
        
        # Decode Base64 data
        icon_bytes = base64.b64decode(ICON_DATA)
        
        # Create Image from bytes
        img = Image.open(io.BytesIO(icon_bytes))
        
        return img
        
    except Exception as e:
        print(f"[Icon] Failed to create PIL Image: {e}")
        return None
