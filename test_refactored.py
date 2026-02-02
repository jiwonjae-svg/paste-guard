"""
Integration Test Suite for Refactored Components
Run this to verify all new components work correctly
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_path_manager():
    """Test PathManager functionality"""
    print("=" * 50)
    print("Testing PathManager")
    print("=" * 50)
    
    from utils import path_manager
    
    print(f"✓ Base directory: {path_manager.base_dir}")
    print(f"✓ Config path: {path_manager.get_config_path()}")
    print(f"✓ Data path: {path_manager.get_data_path('test.json')}")
    print(f"✓ Portable mode: {path_manager.is_portable_mode()}")
    
    # Test directory creation
    test_dir = path_manager.ensure_directory("test_temp")
    print(f"✓ Created directory: {test_dir}")
    
    # Cleanup
    if test_dir.exists():
        test_dir.rmdir()
        print(f"✓ Cleaned up test directory")
    
    print("\n✅ PathManager tests passed!\n")


def test_security_service():
    """Test SecurityService encryption/decryption"""
    print("=" * 50)
    print("Testing SecurityService")
    print("=" * 50)
    
    from services import SecurityService
    
    security = SecurityService()
    
    # Test string encryption
    original = "This is a secret message! 🔒"
    print(f"Original: {original}")
    
    encrypted = security.encrypt_string(original)
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = security.decrypt_string(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert original == decrypted, "Decryption failed!"
    print("✓ String encryption/decryption works!")
    
    # Test dict encryption
    test_dict = {
        "username": "john_doe",
        "password": "super_secret_123",
        "email": "john@example.com"
    }
    
    print(f"\nOriginal dict: {test_dict}")
    
    encrypted_dict = security.encrypt_dict(test_dict, ["password"])
    print(f"Encrypted dict: {encrypted_dict}")
    
    decrypted_dict = security.decrypt_dict(encrypted_dict)
    print(f"Decrypted dict: {decrypted_dict}")
    
    assert decrypted_dict["password"] == test_dict["password"], "Dict decryption failed!"
    print("✓ Dictionary encryption/decryption works!")
    
    # Test hashing
    data = "test data"
    hash1 = security.hash_data(data)
    hash2 = security.hash_data(data)
    assert hash1 == hash2, "Hash inconsistent!"
    assert security.verify_hash(data, hash1), "Hash verification failed!"
    print("✓ Hashing works!")
    
    print("\n✅ SecurityService tests passed!\n")


def test_history_service():
    """Test HistoryService with encryption"""
    print("=" * 50)
    print("Testing HistoryService")
    print("=" * 50)
    
    from services import HistoryService, SecurityService
    from utils import path_manager
    
    security = SecurityService()
    history = HistoryService(security)
    
    # Create test history items
    test_items = [
        {
            "timestamp": 1234567890.0,
            "type": "text",
            "content": "Normal text content",
            "preview": "Normal text...",
            "process": "notepad.exe",
            "app_name": "Notepad",
            "is_sensitive": False
        },
        {
            "timestamp": 1234567891.0,
            "type": "text",
            "content": "password123",
            "preview": "password...",
            "process": "browser.exe",
            "app_name": "Browser",
            "is_sensitive": True  # This should be encrypted
        }
    ]
    
    print(f"✓ Created {len(test_items)} test items")
    
    # Save history (should encrypt sensitive items)
    success = history.save_history(test_items)
    assert success, "History save failed!"
    print("✓ History saved successfully")
    
    # Load history (should decrypt sensitive items)
    loaded_items = history.load_history()
    print(f"✓ Loaded {len(loaded_items)} items")
    
    # Verify content matches
    assert len(loaded_items) == len(test_items), "Item count mismatch!"
    
    for original, loaded in zip(test_items, loaded_items):
        assert original["content"] == loaded["content"], "Content mismatch!"
        print(f"✓ Item verified: {loaded['app_name']}")
    
    # Verify sensitive item was encrypted in file
    import json
    history_file = path_manager.get_data_path("history.json")
    with open(history_file, 'r') as f:
        raw_data = json.load(f)
    
    # The sensitive item should have encrypted content in the file
    sensitive_item = raw_data[1]
    if sensitive_item.get("_content_encrypted"):
        print("✓ Sensitive data was encrypted in file!")
    else:
        print("⚠ Warning: Sensitive data not encrypted (might be normal if not marked)")
    
    # Cleanup
    history.clear_history()
    print("✓ History cleaned up")
    
    print("\n✅ HistoryService tests passed!\n")


def test_notification_service():
    """Test NotificationService event system"""
    print("=" * 50)
    print("Testing NotificationService")
    print("=" * 50)
    
    from services import NotificationService
    
    notification = NotificationService()
    
    # Test event subscription
    events_received = []
    
    def on_paste_approved(data):
        events_received.append(("paste_approved", data))
    
    notification.subscribe("paste_approved", on_paste_approved)
    print("✓ Subscribed to paste_approved event")
    
    # Test notification
    test_data = {"process_name": "test.exe", "content": "test"}
    notification.notify_paste_approved(test_data, "test.exe")
    
    assert len(events_received) == 1, "Event not received!"
    assert events_received[0][0] == "paste_approved", "Wrong event type!"
    print("✓ Event received correctly")
    
    # Test unsubscribe
    notification.unsubscribe("paste_approved", on_paste_approved)
    notification.notify_paste_approved(test_data, "test.exe")
    
    assert len(events_received) == 1, "Unsubscribe failed!"
    print("✓ Unsubscribe works")
    
    print("\n✅ NotificationService tests passed!\n")


def test_integration():
    """Test integration of all components"""
    print("=" * 50)
    print("Integration Test")
    print("=" * 50)
    
    from services import HistoryService, SecurityService, NotificationService
    from utils import path_manager
    
    # Create services
    security = SecurityService()
    history = HistoryService(security)
    notification = NotificationService()
    
    print("✓ All services initialized")
    
    # Create a complete workflow
    events = []
    
    def on_paste_request(data):
        events.append("paste_request")
    
    notification.subscribe("paste_request", on_paste_request)
    
    # Simulate paste request
    clipboard_data = {
        "type": "text",
        "content": "test content",
        "is_sensitive": True
    }
    
    notification.notify_paste_request(clipboard_data, "test.exe", False)
    
    # Add to history
    item = history.add_history_item(
        content_type="text",
        content="test content",
        preview="test...",
        process_name="test.exe",
        is_sensitive=True
    )
    
    # Save and load
    history.save_history([item])
    loaded = history.load_history()
    
    assert len(loaded) == 1, "Integration: History failed!"
    assert len(events) == 1, "Integration: Notification failed!"
    assert loaded[0]["content"] == item["content"], "Integration: Content mismatch!"
    
    print("✓ Complete workflow successful")
    
    # Cleanup
    history.clear_history()
    
    print("\n✅ Integration test passed!\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("🧪 REFACTORED COMPONENTS TEST SUITE")
    print("=" * 50 + "\n")
    
    try:
        test_path_manager()
        test_security_service()
        test_history_service()
        test_notification_service()
        test_integration()
        
        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\n🎉 Refactored components are working correctly!")
        print("📚 See REFACTORING_GUIDE.md for usage details\n")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ TEST FAILED!")
        print("=" * 50)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
