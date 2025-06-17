#!/usr/bin/env python3
"""
chatHMD Windows Installer Builder
Windows用のインストーラーを作成
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class WindowsBuilder:
    def __init__(self):
        self.app_name = "chatHMD"
        self.app_version = "1.0.0"
        self.build_dir = Path("build_windows")
        self.dist_dir = Path("dist_windows")
        
    def clean_build(self):
        """以前のビルドをクリーンアップ"""
        print("🧹 Cleaning previous builds...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
    def create_batch_launcher(self):
        """Windows用バッチファイルを作成"""
        launcher_content = '''@echo off
REM chatHMD Launcher for Windows

REM Get script directory
set "APP_DIR=%~dp0"

REM Set environment variables
set "PYTHONPATH=%APP_DIR%;%PYTHONPATH%"
set "PATH=%APP_DIR%\\llama.cpp\\build\\bin;%PATH%"

REM Change to app directory
cd /d "%APP_DIR%"

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
python -c "import streamlit" 2>nul || (
    echo Installing Python dependencies...
    python -m pip install -r requirements.txt --user
)

REM Launch Streamlit app
echo Starting chatHMD AI Assistant...
start "chatHMD" python -m streamlit run chatHMD_assistant.py --server.headless true --server.port 8501

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Open browser
start "" "http://localhost:8501"

echo chatHMD is now running at http://localhost:8501
echo Close this window to stop the application.
pause
'''
        
        launcher_path = self.build_dir / "chatHMD.bat"
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
            
        return launcher_path
        
    def create_powershell_launcher(self):
        """PowerShell起動スクリプトを作成"""
        ps_content = '''# chatHMD PowerShell Launcher

$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = "$AppDir;$env:PYTHONPATH"
$env:PATH = "$AppDir\\llama.cpp\\build\\bin;$env:PATH"

Set-Location $AppDir

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion"
} catch {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies if needed
try {
    python -c "import streamlit" 2>$null
} catch {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt --user
}

# Launch Streamlit app
Write-Host "Starting chatHMD AI Assistant..." -ForegroundColor Green
Start-Process python "-m streamlit run chatHMD_assistant.py --server.headless true --server.port 8501" -WindowStyle Hidden

# Wait for server to start
Start-Sleep -Seconds 3

# Open browser
Start-Process "http://localhost:8501"

Write-Host "chatHMD is now running at http://localhost:8501" -ForegroundColor Green
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
'''
        
        ps_path = self.build_dir / "chatHMD.ps1"
        with open(ps_path, 'w', encoding='utf-8') as f:
            f.write(ps_content)
            
        return ps_path
        
    def create_installer_script(self):
        """NSIS インストーラースクリプトを作成"""
        nsis_content = f'''# chatHMD NSIS Installer Script

!define APP_NAME "chatHMD"
!define APP_VERSION "{self.app_version}"
!define APP_PUBLISHER "chatHMD Team"
!define APP_URL "https://github.com/chathmd/chathmd"
!define APP_EXE "chatHMD.bat"

!include "MUI2.nsh"

Name "${{APP_NAME}} ${{APP_VERSION}}"
OutFile "chatHMD-${{APP_VERSION}}-windows-installer.exe"
Unicode True

InstallDir "$PROGRAMFILES64\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""

RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    File /r "build_windows\\*.*"
    
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "URLInfoAbout" "${{APP_URL}}"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir /r "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
SectionEnd
'''
        
        nsis_path = self.build_dir / "installer.nsi"
        with open(nsis_path, 'w', encoding='utf-8') as f:
            f.write(nsis_content)
            
        return nsis_path
        
    def copy_app_files(self):
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
                shutil.copy2(file_name, self.build_dir)
                
        # Scripts directory
        if Path("scripts").exists():
            shutil.copytree("scripts", self.build_dir / "scripts")
            
        # Create directories for Windows
        for dir_name in ["learning_data", "loras", "models"]:
            (self.build_dir / dir_name).mkdir(exist_ok=True)
            if Path(dir_name).exists():
                shutil.copytree(dir_name, self.build_dir / dir_name, dirs_exist_ok=True)
                
    def create_readme(self):
        """README.txtを作成"""
        readme_content = f"""chatHMD AI Assistant v{self.app_version}
================================

Thank you for downloading chatHMD AI Assistant!

SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- Python 3.8 or higher
- 8GB RAM (16GB recommended)
- 10GB free disk space

INSTALLATION:
1. Run the installer (chatHMD-{self.app_version}-windows-installer.exe)
2. Follow the installation wizard
3. Launch from Start Menu or Desktop shortcut

FIRST TIME SETUP:
1. The app will automatically download required AI models (may take a few minutes)
2. Python dependencies will be installed automatically
3. Your browser will open to http://localhost:8501

FEATURES:
- Privacy-first AI assistant
- Local AI model execution
- Learning from your feedback
- No data sent to external servers
- Text-to-LoRA technology

TROUBLESHOOTING:
- If Python is not installed, download from: https://python.org
- Make sure to add Python to your PATH during installation
- For support, visit: https://github.com/chathmd/chathmd

USAGE:
1. Open the chatHMD application
2. Start chatting with the AI
3. Provide feedback to improve responses
4. Enjoy your personal AI assistant!

For more information, visit: https://chathmd.com
"""
        
        readme_path = self.build_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
    def build(self):
        """メインビルドプロセス"""
        print(f"🚀 Building {self.app_name} for Windows...")
        
        try:
            self.clean_build()
            
            # Create launchers
            self.create_batch_launcher()
            self.create_powershell_launcher()
            
            # Copy files
            self.copy_app_files()
            self.create_readme()
            
            # Create installer script
            nsis_path = self.create_installer_script()
            
            # Create simple ZIP distribution
            zip_name = f"{self.app_name}-{self.app_version}-windows-portable.zip"
            zip_path = self.dist_dir / zip_name
            
            import zipfile
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.build_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arc_name = file_path.relative_to(self.build_dir)
                        zipf.write(file_path, arc_name)
                        
            print(f"""
🎉 Windows build completed!

📦 Portable Version: {zip_path}
📄 NSIS Script: {nsis_path}

PORTABLE INSTALLATION:
1. Extract the ZIP file to any folder
2. Run chatHMD.bat to start the application

INSTALLER CREATION:
To create a Windows installer (.exe):
1. Install NSIS (https://nsis.sourceforge.io/)
2. Right-click installer.nsi and select "Compile NSIS Script"

REQUIREMENTS:
- Python 3.8+ must be installed on target system
- Internet connection for first-time model download
""")
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    builder = WindowsBuilder()
    builder.build()