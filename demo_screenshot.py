#!/usr/bin/env python3
"""Take a screenshot of the Streamlit UI"""
import subprocess
import time

def take_screenshot():
    """Take a screenshot using screencapture (macOS)"""
    print("📸 Taking screenshot of the UI...")
    
    # Open the browser first
    subprocess.run(["open", "http://localhost:8501"])
    
    # Wait for page to load
    time.sleep(3)
    
    # Take screenshot
    screenshot_path = "ui_screenshot.png"
    subprocess.run(["screencapture", "-x", screenshot_path])
    
    print(f"✅ Screenshot saved to: {screenshot_path}")
    return screenshot_path

if __name__ == "__main__":
    take_screenshot()