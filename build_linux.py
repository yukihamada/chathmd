#!/usr/bin/env python3
"""
chatHMD Linux Package Builder
Linux用のパッケージ（AppImage、deb、rpm）を作成
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class LinuxBuilder:
    def __init__(self):
        self.app_name = "chatHMD"
        self.app_version = "1.0.0"
        self.build_dir = Path("build_linux")
        self.dist_dir = Path("dist_linux")
        
    def clean_build(self):
        """以前のビルドをクリーンアップ"""
        print("🧹 Cleaning previous builds...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
    def create_shell_launcher(self):
        """Linux用シェルスクリプトを作成"""
        launcher_content = '''#!/bin/bash
# chatHMD Launcher for Linux

# Get script directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set environment variables
export PYTHONPATH="$APP_DIR:$PYTHONPATH"
export PATH="$APP_DIR/llama.cpp/build/bin:$PATH"

# Change to app directory
cd "$APP_DIR"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    exit 1
fi

# Check if dependencies are installed
python3 -c "import streamlit" 2>/dev/null || {
    echo "Installing Python dependencies..."
    python3 -m pip install -r requirements.txt --user
}

# Launch Streamlit app
echo "Starting chatHMD AI Assistant..."
python3 -m streamlit run chatHMD_assistant.py --server.headless true --server.port 8501 &
STREAMLIT_PID=$!

# Wait for server to start
sleep 3

# Try to open browser
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8501"
elif command -v firefox &> /dev/null; then
    firefox "http://localhost:8501" &
elif command -v chromium &> /dev/null; then
    chromium "http://localhost:8501" &
elif command -v google-chrome &> /dev/null; then
    google-chrome "http://localhost:8501" &
else
    echo "Please open your browser and go to: http://localhost:8501"
fi

echo "chatHMD is now running at http://localhost:8501"
echo "Press Ctrl+C to stop the application"

# Wait for Streamlit process
wait $STREAMLIT_PID
'''
        
        launcher_path = self.build_dir / "chatHMD.sh"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        os.chmod(launcher_path, 0o755)
        
        return launcher_path
        
    def create_desktop_file(self):
        """Linux .desktop ファイルを作成"""
        desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=chatHMD AI Assistant
Comment=Privacy-first AI assistant with learning capabilities
Exec={self.app_name}.sh
Icon={self.app_name}
Terminal=false
Categories=Office;Education;Development;
StartupWMClass=chatHMD
'''
        
        desktop_path = self.build_dir / f"{self.app_name}.desktop"
        with open(desktop_path, 'w') as f:
            f.write(desktop_content)
            
        return desktop_path
        
    def create_appimage_structure(self):
        """AppImage用の構造を作成"""
        appdir = self.build_dir / f"{self.app_name}.AppDir"
        
        # AppDir structure
        dirs = [
            appdir,
            appdir / "usr" / "bin",
            appdir / "usr" / "share" / "applications",
            appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps",
            appdir / "usr" / "share" / "chatHMD"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        return appdir
        
    def create_deb_structure(self):
        """Debian パッケージ構造を作成"""
        deb_dir = self.build_dir / "deb"
        
        # Debian package structure
        dirs = [
            deb_dir / "DEBIAN",
            deb_dir / "usr" / "bin",
            deb_dir / "usr" / "share" / "applications",
            deb_dir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps",
            deb_dir / "usr" / "share" / "chatHMD"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Control file
        control_content = f'''Package: {self.app_name.lower()}
Version: {self.app_version}
Section: utils
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-pip
Maintainer: chatHMD Team <team@chathmd.com>
Description: Privacy-first AI assistant with learning capabilities
 chatHMD is an AI assistant that learns from your feedback while keeping
 all data local. Features include Text-to-LoRA learning technology and
 complete privacy protection.
'''
        
        with open(deb_dir / "DEBIAN" / "control", 'w') as f:
            f.write(control_content)
            
        return deb_dir
        
    def create_rpm_spec(self):
        """RPM spec ファイルを作成"""
        spec_content = f'''Name:           {self.app_name.lower()}
Version:        {self.app_version}
Release:        1%{{?dist}}
Summary:        Privacy-first AI assistant with learning capabilities

License:        MIT
URL:            https://github.com/chathmd/chathmd
Source0:        %{{name}}-%{{version}}.tar.gz

BuildArch:      noarch
Requires:       python3 >= 3.8, python3-pip

%description
chatHMD is an AI assistant that learns from your feedback while keeping
all data local. Features include Text-to-LoRA learning technology and
complete privacy protection.

%prep
%setup -q

%build
# Nothing to build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/chatHMD
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
mkdir -p $RPM_BUILD_ROOT/usr/share/icons/hicolor/256x256/apps

cp -r * $RPM_BUILD_ROOT/usr/share/chatHMD/
ln -s /usr/share/chatHMD/chatHMD.sh $RPM_BUILD_ROOT/usr/bin/chatHMD
cp chatHMD.desktop $RPM_BUILD_ROOT/usr/share/applications/

%files
/usr/share/chatHMD
/usr/bin/chatHMD
/usr/share/applications/chatHMD.desktop

%changelog
* Wed Jan 01 2025 chatHMD Team <team@chathmd.com> - {self.app_version}-1
- Initial release
'''
        
        spec_path = self.build_dir / f"{self.app_name.lower()}.spec"
        with open(spec_path, 'w') as f:
            f.write(spec_content)
            
        return spec_path
        
    def copy_app_files(self, target_dir):
        """アプリケーションファイルをコピー"""
        print("📁 Copying application files...")
        
        # Python files
        python_files = [
            "chatHMD_assistant.py",
            "learning_data_manager.py",
            "requirements.txt"
        ]
        
        for file_name in python_files:
            if Path(file_name).exists():
                shutil.copy2(file_name, target_dir)
                
        # Scripts directory
        if Path("scripts").exists():
            shutil.copytree("scripts", target_dir / "scripts")
            
        # Create directories
        for dir_name in ["learning_data", "loras", "models"]:
            (target_dir / dir_name).mkdir(exist_ok=True)
            if Path(dir_name).exists():
                shutil.copytree(dir_name, target_dir / dir_name, dirs_exist_ok=True)
                
    def create_install_script(self):
        """インストールスクリプトを作成"""
        install_content = '''#!/bin/bash
# chatHMD Linux Installation Script

set -e

APP_NAME="chatHMD"
INSTALL_DIR="/opt/chatHMD"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"

echo "Installing chatHMD AI Assistant..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "Installing system-wide..."
    SUDO=""
else
    echo "Installing for current user..."
    SUDO="sudo"
    INSTALL_DIR="$HOME/.local/share/chatHMD"
    BIN_DIR="$HOME/.local/bin"
    DESKTOP_DIR="$HOME/.local/share/applications"
    
    # Create directories
    mkdir -p "$BIN_DIR" "$DESKTOP_DIR"
fi

# Install Python dependencies
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Please install it first:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    exit 1
fi

# Copy files
echo "Copying application files..."
$SUDO mkdir -p "$INSTALL_DIR"
$SUDO cp -r * "$INSTALL_DIR/"
$SUDO chmod +x "$INSTALL_DIR/chatHMD.sh"

# Create symlink
echo "Creating executable link..."
$SUDO ln -sf "$INSTALL_DIR/chatHMD.sh" "$BIN_DIR/chatHMD"

# Install desktop file
echo "Installing desktop entry..."
$SUDO cp "$INSTALL_DIR/chatHMD.desktop" "$DESKTOP_DIR/"
$SUDO sed -i "s|Exec=chatHMD.sh|Exec=$INSTALL_DIR/chatHMD.sh|" "$DESKTOP_DIR/chatHMD.desktop"

echo "Installation completed!"
echo "You can now run 'chatHMD' from the command line or find it in your applications menu."
'''
        
        install_path = self.build_dir / "install.sh"
        with open(install_path, 'w') as f:
            f.write(install_content)
        os.chmod(install_path, 0o755)
        
        return install_path
        
    def build(self):
        """メインビルドプロセス"""
        print(f"🚀 Building {self.app_name} for Linux...")
        
        try:
            self.clean_build()
            
            # Create basic files
            self.create_shell_launcher()
            self.create_desktop_file()
            self.create_install_script()
            
            # Copy application files
            self.copy_app_files(self.build_dir)
            
            # Create different package formats
            
            # 1. Portable tar.gz
            print("📦 Creating portable package...")
            tar_name = f"{self.app_name}-{self.app_version}-linux-portable.tar.gz"
            tar_path = self.dist_dir / tar_name
            
            subprocess.run([
                "tar", "-czf", str(tar_path),
                "-C", str(self.build_dir.parent),
                self.build_dir.name
            ], check=True)
            
            # 2. Debian package
            print("📦 Creating Debian package...")
            deb_dir = self.create_deb_structure()
            
            # Copy files to deb structure
            self.copy_app_files(deb_dir / "usr" / "share" / "chatHMD")
            shutil.copy2(self.build_dir / "chatHMD.sh", deb_dir / "usr" / "bin" / "chatHMD")
            shutil.copy2(self.build_dir / "chatHMD.desktop", deb_dir / "usr" / "share" / "applications")
            
            # Build deb package
            deb_name = f"{self.app_name.lower()}_{self.app_version}_amd64.deb"
            subprocess.run([
                "dpkg-deb", "--build", str(deb_dir), str(self.dist_dir / deb_name)
            ], check=False)  # May not be available on all systems
            
            print(f"""
🎉 Linux build completed!

📦 Portable Version: {tar_path}
🐧 Debian Package: {self.dist_dir / deb_name} (if dpkg-deb available)

PORTABLE INSTALLATION:
1. Extract: tar -xzf {tar_name}
2. Run: cd {self.build_dir.name} && ./install.sh

DEBIAN INSTALLATION:
1. Install: sudo dpkg -i {deb_name}
2. Fix dependencies: sudo apt install -f

MANUAL INSTALLATION:
1. Extract the portable version anywhere
2. Run ./chatHMD.sh directly

REQUIREMENTS:
- Python 3.8+
- Internet connection for first-time setup
""")
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    builder = LinuxBuilder()
    builder.build()