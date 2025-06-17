#!/usr/bin/env python3
"""Test the new chat UI"""
import requests
import json

def test_chat_ui():
    """Test chat UI accessibility and features"""
    
    print("🧪 Testing Chat UI...\n")
    
    # Test 1: UI Accessibility
    print("1️⃣ Testing UI accessibility...")
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("   ✅ Chat UI is accessible")
            print(f"   📊 Response size: {len(response.text)} bytes")
        else:
            print(f"   ❌ UI returned status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Health Check
    print("\n2️⃣ Testing Streamlit health...")
    try:
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Streamlit is healthy")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # UI Feature Summary
    print("\n📱 Chat UI Features:")
    print("   ✨ ChatGPT-style conversation interface")
    print("   💭 Feedback system on each response")
    print("   ⭐ 5-star rating system")
    print("   📝 Improvement suggestions input")
    print("   🧠 LoRA training from collected feedback")
    print("   📊 Real-time metrics and stats")
    print("   🔄 Hot-swappable LoRA models")
    
    print("\n🎯 Usage Flow:")
    print("   1. Chat with the AI normally")
    print("   2. Click 'Give Feedback' on any response")
    print("   3. Rate and suggest improvements")
    print("   4. After collecting feedback, train LoRA")
    print("   5. AI adapts to your preferences!")
    
    print("\n🌐 Access the UI at: http://localhost:8501")

if __name__ == "__main__":
    test_chat_ui()