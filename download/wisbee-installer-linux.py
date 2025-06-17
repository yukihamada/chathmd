#!/usr/bin/env python3
"""
Wisbee Desktop Installer
Downloads and sets up Wisbee AI with jan-nano model
"""

import os
import sys
import json
import hashlib
import requests
import subprocess
from pathlib import Path
from urllib.request import urlretrieve

class WisbeeInstaller:
    def __init__(self):
        self.home_dir = Path.home()
        self.wisbee_dir = self.home_dir / ".wisbee"
        self.models_dir = self.wisbee_dir / "models"
        self.app_dir = self.wisbee_dir / "app"
        
        # Model info
        self.model_name = "jan-nano-4b-iQ4_XS.gguf"
        self.model_url = "https://huggingface.co/Menlo/Jan-nano-gguf/resolve/main/jan-nano-4b-iQ4_XS.gguf"
        self.model_size = 2.27 * 1024 * 1024 * 1024  # 2.27GB in bytes
        
    def setup_directories(self):
        """Create necessary directories"""
        print("📁 Setting up directories...")
        self.wisbee_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.app_dir.mkdir(exist_ok=True)
        print("✅ Directories created")
        
    def download_model(self):
        """Download the jan-nano model"""
        model_path = self.models_dir / self.model_name
        
        if model_path.exists():
            print(f"✅ Model already exists at {model_path}")
            return model_path
            
        print(f"📥 Downloading jan-nano model (2.27GB)...")
        print(f"   This may take a few minutes depending on your internet speed...")
        
        try:
            # Download with progress
            def download_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(100, (downloaded / total_size) * 100)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                
                sys.stdout.write(f'\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}MB / {mb_total:.1f}MB)')
                sys.stdout.flush()
            
            urlretrieve(self.model_url, model_path, reporthook=download_progress)
            print("\n✅ Model downloaded successfully!")
            
            return model_path
            
        except Exception as e:
            print(f"\n❌ Error downloading model: {e}")
            if model_path.exists():
                model_path.unlink()
            return None
    
    def setup_llama_cpp(self):
        """Setup llama.cpp for model inference"""
        llama_dir = self.app_dir / "llama.cpp"
        
        if llama_dir.exists():
            print("✅ llama.cpp already installed")
            return llama_dir
            
        print("🔧 Setting up llama.cpp...")
        
        try:
            # Clone llama.cpp
            subprocess.run([
                "git", "clone",
                "https://github.com/ggerganov/llama.cpp.git",
                str(llama_dir)
            ], check=True)
            
            # Build llama.cpp
            os.chdir(llama_dir)
            
            # Check for Metal support (macOS)
            if sys.platform == "darwin":
                print("🍎 Building with Metal support for macOS...")
                subprocess.run(["make", "LLAMA_METAL=1"], check=True)
            else:
                print("🔨 Building llama.cpp...")
                subprocess.run(["make"], check=True)
            
            print("✅ llama.cpp setup complete!")
            return llama_dir
            
        except Exception as e:
            print(f"❌ Error setting up llama.cpp: {e}")
            return None
    
    def create_launcher(self):
        """Create launcher script"""
        launcher_path = self.wisbee_dir / "wisbee.py"
        
        launcher_content = f'''#!/usr/bin/env python3
"""
Wisbee AI Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

# Paths
WISBEE_DIR = Path.home() / ".wisbee"
MODEL_PATH = WISBEE_DIR / "models" / "jan-nano-4b-iQ4_XS.gguf"
LLAMA_PATH = WISBEE_DIR / "app" / "llama.cpp" / "main"

def run_wisbee():
    """Run Wisbee with llama.cpp"""
    
    if not MODEL_PATH.exists():
        print("❌ Model not found! Please run the installer first.")
        return
    
    if not LLAMA_PATH.exists():
        print("❌ llama.cpp not found! Please run the installer first.")
        return
    
    print("🐝 Starting Wisbee AI...")
    print("💡 Tip: Type 'exit' to quit\\n")
    
    # Run llama.cpp with the model
    cmd = [
        str(LLAMA_PATH),
        "-m", str(MODEL_PATH),
        "-n", "512",  # Max tokens
        "-c", "2048",  # Context size
        "--interactive",
        "--interactive-first",
        "-r", "User:",
        "--in-prefix", " ",
        "--in-suffix", "Assistant:",
        "-p", "You are Wisbee, a helpful AI assistant. You prioritize user privacy and provide accurate, helpful responses.\\n\\nUser: "
    ]
    
    # Add GPU acceleration flags
    if sys.platform == "darwin":
        cmd.extend(["-ngl", "1"])  # Metal GPU layers
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")

if __name__ == "__main__":
    run_wisbee()
'''
        
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        os.chmod(launcher_path, 0o755)
        print(f"✅ Created launcher: {launcher_path}")
        
        # Create desktop shortcut
        if sys.platform == "darwin":
            self.create_macos_app()
        elif sys.platform == "win32":
            self.create_windows_shortcut()
        else:
            self.create_linux_desktop()
    
    def create_macos_app(self):
        """Create macOS .app bundle"""
        app_path = Path("/Applications/Wisbee.app")
        contents_dir = app_path / "Contents"
        macos_dir = contents_dir / "MacOS"
        
        # Create directories
        macos_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Info.plist
        info_plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>wisbee</string>
    <key>CFBundleIdentifier</key>
    <string>ai.wisbee.desktop</string>
    <key>CFBundleName</key>
    <string>Wisbee</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleIconFile</key>
    <string>wisbee.icns</string>
</dict>
</plist>'''
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(info_plist)
        
        # Create launcher script
        launcher_script = f'''#!/bin/bash
cd {self.wisbee_dir}
/usr/bin/python3 wisbee.py
'''
        
        launcher_path = macos_dir / "wisbee"
        with open(launcher_path, 'w') as f:
            f.write(launcher_script)
        
        os.chmod(launcher_path, 0o755)
        print("✅ Created macOS app bundle")
    
    def create_windows_shortcut(self):
        """Create Windows shortcut"""
        # This would create a .lnk file on Windows
        print("✅ Windows shortcut creation (implement with pywin32)")
    
    def create_linux_desktop(self):
        """Create Linux .desktop file"""
        desktop_file = f'''[Desktop Entry]
Name=Wisbee
Comment=Privacy-first AI Assistant
Exec=python3 {self.wisbee_dir}/wisbee.py
Icon=wisbee
Terminal=true
Type=Application
Categories=Utility;AI;
'''
        
        desktop_path = self.home_dir / ".local/share/applications/wisbee.desktop"
        desktop_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(desktop_path, 'w') as f:
            f.write(desktop_file)
        
        os.chmod(desktop_path, 0o755)
        print("✅ Created Linux desktop entry")
    
    def install(self):
        """Run the complete installation"""
        print("🐝 Wisbee AI Installer")
        print("=" * 50)
        
        # Setup directories
        self.setup_directories()
        
        # Download model
        model_path = self.download_model()
        if not model_path:
            print("❌ Installation failed: Could not download model")
            return False
        
        # Setup llama.cpp
        llama_path = self.setup_llama_cpp()
        if not llama_path:
            print("❌ Installation failed: Could not setup llama.cpp")
            return False
        
        # Create launcher
        self.create_launcher()
        
        print("\n" + "=" * 50)
        print("✅ Wisbee installation complete!")
        print(f"\n📍 Installation directory: {self.wisbee_dir}")
        print(f"📊 Model: {model_path}")
        print(f"\n🚀 To start Wisbee:")
        print(f"   python3 {self.wisbee_dir}/wisbee.py")
        
        if sys.platform == "darwin":
            print(f"\n   Or open /Applications/Wisbee.app")
        
        return True

if __name__ == "__main__":
    installer = WisbeeInstaller()
    success = installer.install()
    
    if success:
        print("\n🎉 Enjoy Wisbee AI!")
    else:
        print("\n😞 Installation failed. Please check the errors above.")
        sys.exit(1)