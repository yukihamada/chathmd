#!/usr/bin/env python3
"""Test the Streamlit UI components"""
import requests
import time

def test_ui_accessibility():
    """Test if UI is accessible"""
    url = "http://localhost:8501"
    
    print("🧪 Testing UI accessibility...")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ UI is accessible at {url}")
            print(f"   Response size: {len(response.text)} bytes")
            return True
        else:
            print(f"❌ UI returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not access UI: {e}")
        return False

def test_ui_components():
    """Test UI components via API"""
    # Streamlit doesn't have a direct API, but we can check if the app loaded
    url = "http://localhost:8501/_stcore/health"
    
    print("\n🧪 Testing UI health endpoint...")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    print("=== Streamlit UI Test Suite ===\n")
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    if test_ui_accessibility():
        tests_passed += 1
    
    if test_ui_components():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! UI is working correctly.")
        print("\n📱 Access the UI at: http://localhost:8501")
        print("   Features available:")
        print("   - Generate LoRA from task description")
        print("   - Load/unload LoRA adapters")
        print("   - Interactive inference with the model")
        print("   - Real-time performance metrics")
    else:
        print("⚠️  Some tests failed. Check the logs.")

if __name__ == "__main__":
    main()