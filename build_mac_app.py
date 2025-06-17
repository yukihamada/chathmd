#!/usr/bin/env python3
"""
chatHMD Mac App Builder
MacOS用のスタンドアロンアプリケーションを作成
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class MacAppBuilder:
    def __init__(self):
        self.app_name = "chatHMD"
        self.app_version = "1.0.0"
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.app_dir = self.dist_dir / f"{self.app_name}.app"
        
    def clean_build(self):
        """以前のビルドをクリーンアップ"""
        print("🧹 Cleaning previous builds...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
    def check_dependencies(self):
        """必要な依存関係をチェック"""
        print("🔍 Checking dependencies...")
        
        # Python依存関係チェック
        required_packages = ['streamlit', 'py2app']
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} found")
            except ImportError:
                print(f"❌ {package} not found. Installing...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package])
        
        # llama.cpp チェック
        llama_path = Path("llama.cpp/build/bin/llama-cli")
        if not llama_path.exists():
            print("⚠️  llama.cpp not built. Building...")
            self.build_llama_cpp()
        else:
            print("✅ llama.cpp found")
            
    def build_llama_cpp(self):
        """llama.cppをビルド"""
        print("🔨 Building llama.cpp...")
        llama_dir = Path("llama.cpp")
        build_dir = llama_dir / "build"
        
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir()
        
        # CMakeビルド
        subprocess.run([
            "cmake", "-B", str(build_dir), "-S", str(llama_dir),
            "-DCMAKE_BUILD_TYPE=Release",
            "-DGGML_METAL=ON"  # Metal acceleration for Mac
        ], check=True)
        
        subprocess.run([
            "cmake", "--build", str(build_dir), "--config", "Release", "-j"
        ], check=True)
        
    def create_launcher_script(self):
        """アプリ起動用スクリプトを作成"""
        launcher_content = '''#!/bin/bash
# chatHMD Launcher Script

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_DIR="$(dirname "$(dirname "$DIR")")"

# Set environment variables
export PYTHONPATH="$APP_DIR/Contents/Resources:$PYTHONPATH"
export PATH="$APP_DIR/Contents/Resources/llama.cpp/build/bin:$PATH"

# Change to app directory
cd "$APP_DIR/Contents/Resources"

# Launch Streamlit app
python3 -m streamlit run chatHMD_assistant.py --server.headless true --server.port 8501 &

# Wait a moment for server to start
sleep 3

# Open browser
open "http://localhost:8501"

# Keep script running
wait
'''
        
        launcher_path = self.build_dir / "launcher.sh"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        os.chmod(launcher_path, 0o755)
        
        return launcher_path
        
    def create_app_structure(self):
        """Mac アプリの構造を作成"""
        print("📦 Creating app structure...")
        
        # App bundle structure
        contents_dir = self.app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        for dir_path in [contents_dir, macos_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Info.plist作成
        info_plist = {
            "CFBundleName": self.app_name,
            "CFBundleDisplayName": "chatHMD AI Assistant",
            "CFBundleIdentifier": "com.chathmd.assistant",
            "CFBundleVersion": self.app_version,
            "CFBundleShortVersionString": self.app_version,
            "CFBundleExecutable": "chatHMD",
            "CFBundleIconFile": "icon.icns",
            "CFBundlePackageType": "APPL",
            "LSUIElement": False,
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False
        }
        
        with open(contents_dir / "Info.plist", 'w') as f:
            import plistlib
            plistlib.dump(info_plist, f)
            
        return macos_dir, resources_dir
        
    def copy_app_files(self, resources_dir):
        """アプリファイルをコピー"""
        print("📁 Copying application files...")
        
        # Python files
        python_files = [
            "chatHMD_assistant.py",
            "learning_data_manager.py",
            "requirements.txt"
        ]
        
        for file_name in python_files:
            if Path(file_name).exists():
                shutil.copy2(file_name, resources_dir)
                
        # Scripts directory
        if Path("scripts").exists():
            shutil.copytree("scripts", resources_dir / "scripts")
            
        # llama.cpp
        if Path("llama.cpp").exists():
            shutil.copytree("llama.cpp", resources_dir / "llama.cpp")
            
        # Models directory (if exists)
        if Path("models").exists():
            shutil.copytree("models", resources_dir / "models")
            
        # Learning data directories
        for dir_name in ["learning_data", "loras"]:
            if Path(dir_name).exists():
                shutil.copytree(dir_name, resources_dir / dir_name)
            else:
                (resources_dir / dir_name).mkdir(exist_ok=True)
                
    def create_executable(self, macos_dir):
        """実行可能ファイルを作成"""
        print("⚙️ Creating executable...")
        
        executable_content = '''#!/bin/bash
# chatHMD Main Executable

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
RESOURCES_DIR="$DIR/../Resources"

# Set environment variables
export PYTHONPATH="$RESOURCES_DIR:$PYTHONPATH"
export PATH="$RESOURCES_DIR/llama.cpp/build/bin:$PATH"

# Change to resources directory
cd "$RESOURCES_DIR"

# Check if Python dependencies are installed
python3 -c "import streamlit" 2>/dev/null || {
    echo "Installing Python dependencies..."
    python3 -m pip install -r requirements.txt --user
}

# Launch Streamlit app
python3 -m streamlit run chatHMD_assistant.py --server.headless true --server.port 8501 &
STREAMLIT_PID=$!

# Wait a moment for server to start
sleep 3

# Open browser
open "http://localhost:8501"

# Wait for Streamlit process
wait $STREAMLIT_PID
'''
        
        executable_path = macos_dir / "chatHMD"
        with open(executable_path, 'w') as f:
            f.write(executable_content)
        os.chmod(executable_path, 0o755)
        
    def create_dmg(self):
        """DMGファイルを作成"""
        print("💿 Creating DMG installer...")
        
        dmg_name = f"{self.app_name}-{self.app_version}-mac.dmg"
        dmg_path = self.dist_dir / dmg_name
        
        # 一時的なDMGボリューム作成
        temp_dmg = self.build_dir / "temp.dmg"
        
        # DMG作成コマンド
        subprocess.run([
            "hdiutil", "create", "-srcfolder", str(self.dist_dir),
            "-volname", f"{self.app_name} {self.app_version}",
            "-format", "UDZO", "-o", str(temp_dmg)
        ], check=True)
        
        # 最終DMGに移動
        shutil.move(str(temp_dmg), str(dmg_path))
        
        print(f"✅ DMG created: {dmg_path}")
        return dmg_path
        
    def build(self):
        """メインビルドプロセス"""
        print(f"🚀 Building {self.app_name} for macOS...")
        
        try:
            self.clean_build()
            self.check_dependencies()
            
            macos_dir, resources_dir = self.create_app_structure()
            self.copy_app_files(resources_dir)
            self.create_executable(macos_dir)
            
            dmg_path = self.create_dmg()
            
            print(f"""
🎉 Build completed successfully!

📦 App Bundle: {self.app_dir}
💿 Installer: {dmg_path}

To install:
1. Double-click the DMG file
2. Drag {self.app_name}.app to Applications folder
3. Launch from Applications or Launchpad

Note: On first run, you may need to right-click the app and select "Open" 
to bypass macOS security restrictions for unsigned apps.
""")
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    builder = MacAppBuilder()
    builder.build()