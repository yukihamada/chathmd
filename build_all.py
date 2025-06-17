#!/usr/bin/env python3
"""
chatHMD Universal Builder
全プラットフォーム向けのビルドを管理
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_platform():
    """現在のプラットフォームを取得"""
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def check_requirements():
    """ビルド要件をチェック"""
    print("🔍 Checking build requirements...")
    
    # Python version check
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
        
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Required files check
    required_files = [
        "chatHMD_assistant.py",
        "learning_data_manager.py",
        "requirements.txt"
    ]
    
    for file_name in required_files:
        if not Path(file_name).exists():
            print(f"❌ Required file missing: {file_name}")
            return False
        print(f"✅ Found {file_name}")
        
    return True

def build_platform(platform_name):
    """指定されたプラットフォーム用にビルド"""
    print(f"\n🚀 Building for {platform_name}...")
    
    if platform_name == "mac":
        subprocess.run([sys.executable, "build_mac_app.py"], check=True)
    elif platform_name == "windows":
        subprocess.run([sys.executable, "build_windows.py"], check=True)
    elif platform_name == "linux":
        subprocess.run([sys.executable, "build_linux.py"], check=True)
    else:
        print(f"❌ Unknown platform: {platform_name}")
        return False
        
    return True

def main():
    """メインビルド関数"""
    print("🏗️  chatHMD Universal Builder")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Build requirements not met")
        sys.exit(1)
        
    current_platform = get_platform()
    print(f"\n💻 Current platform: {current_platform}")
    
    if len(sys.argv) > 1:
        # 特定プラットフォームを指定
        target_platforms = sys.argv[1:]
    else:
        # 対話的にプラットフォームを選択
        print("\nSelect platforms to build for:")
        print("1. Current platform only")
        print("2. All platforms")
        print("3. Custom selection")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            target_platforms = [current_platform]
        elif choice == "2":
            target_platforms = ["mac", "windows", "linux"]
        elif choice == "3":
            print("\nAvailable platforms:")
            all_platforms = ["mac", "windows", "linux"]
            for i, platform_name in enumerate(all_platforms, 1):
                print(f"{i}. {platform_name}")
                
            selections = input("\nEnter platform numbers (comma-separated): ").strip()
            try:
                indices = [int(x.strip()) - 1 for x in selections.split(",")]
                target_platforms = [all_platforms[i] for i in indices if 0 <= i < len(all_platforms)]
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                sys.exit(1)
        else:
            print("❌ Invalid choice")
            sys.exit(1)
    
    print(f"\n🎯 Building for platforms: {', '.join(target_platforms)}")
    
    # Build each platform
    success_count = 0
    total_count = len(target_platforms)
    
    for platform_name in target_platforms:
        try:
            if build_platform(platform_name):
                success_count += 1
                print(f"✅ {platform_name} build completed")
            else:
                print(f"❌ {platform_name} build failed")
        except Exception as e:
            print(f"❌ {platform_name} build failed: {e}")
    
    # Summary
    print(f"\n📊 Build Summary:")
    print(f"✅ Successful: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 All builds completed successfully!")
        
        # Show distribution files
        print("\n📦 Distribution files:")
        for dist_dir in ["dist", "dist_windows", "dist_linux"]:
            if Path(dist_dir).exists():
                print(f"\n{dist_dir}/:")
                for file_path in Path(dist_dir).iterdir():
                    if file_path.is_file():
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        print(f"  {file_path.name} ({size_mb:.1f} MB)")
    else:
        print(f"\n⚠️  {total_count - success_count} builds failed")
        sys.exit(1)

if __name__ == "__main__":
    main()