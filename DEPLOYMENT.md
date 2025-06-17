# chatHMD デプロイメントガイド

## 🚀 クイックスタート

### すべてのプラットフォーム用ビルド
```bash
python3 build_all.py
```

### 特定プラットフォーム用ビルド
```bash
# Mac用のみ
python3 build_mac_app.py

# Windows用のみ  
python3 build_windows.py

# Linux用のみ
python3 build_linux.py
```

## 📱 プラットフォーム別インストール方法

### 🍎 macOS

#### 配布形式
- **DMG**: `chatHMD-1.0.0-mac.dmg` (推奨)
- **App Bundle**: `chatHMD.app`

#### インストール手順
1. DMGファイルをダブルクリック
2. chatHMD.appをApplicationsフォルダにドラッグ
3. LaunchpadまたはApplicationsフォルダから起動
4. 初回起動時は右クリック→「開く」で許可

#### システム要件
- macOS 10.15以降
- Python 3.8以降
- 8GB RAM (16GB推奨)
- 10GB空き容量

### 🪟 Windows

#### 配布形式
- **Portable**: `chatHMD-1.0.0-windows-portable.zip`
- **Installer**: `chatHMD-1.0.0-windows-installer.exe` (NSIS必要)

#### インストール手順（Portable）
1. ZIPファイルを任意のフォルダに展開
2. `chatHMD.bat`をダブルクリックして起動
3. Pythonが未インストールの場合は自動で案内

#### インストール手順（Installer）
1. インストーラーを実行
2. ウィザードに従ってインストール
3. スタートメニューまたはデスクトップから起動

#### システム要件
- Windows 10/11 (64-bit)
- Python 3.8以降
- 8GB RAM (16GB推奨)
- 10GB空き容量

### 🐧 Linux

#### 配布形式
- **Portable**: `chatHMD-1.0.0-linux-portable.tar.gz`
- **Debian**: `chathmd_1.0.0_amd64.deb`
- **RPM**: `chathmd-1.0.0-1.noarch.rpm` (spec提供)

#### インストール手順（Portable）
```bash
# 展開
tar -xzf chatHMD-1.0.0-linux-portable.tar.gz
cd build_linux

# インストール
./install.sh

# 起動
chatHMD
```

#### インストール手順（Debian）
```bash
# インストール
sudo dpkg -i chathmd_1.0.0_amd64.deb
sudo apt install -f  # 依存関係修正

# 起動
chatHMD
```

#### システム要件
- Ubuntu 18.04以降、またはその他のLinuxディストリビューション
- Python 3.8以降
- 8GB RAM (16GB推奨)
- 10GB空き容量

## 🏗️ ビルド環境構築

### 必要なツール

#### macOS
```bash
# Xcode Command Line Tools
xcode-select --install

# Python依存関係
pip3 install py2app

# DMG作成用（システム標準）
# hdiutil, diskutil
```

#### Windows
```bash
# Python依存関係
pip install pyinstaller

# NSIS (インストーラー作成用)
# https://nsis.sourceforge.io/Download
```

#### Linux
```bash
# Debian/Ubuntu
sudo apt install python3-dev build-essential dpkg-dev

# RHEL/CentOS
sudo yum install python3-devel gcc rpm-build

# Python依存関係
pip3 install setuptools wheel
```

## 🔧 カスタマイズ

### アプリケーション設定
各ビルダースクリプトの先頭で設定を変更：

```python
class AppBuilder:
    def __init__(self):
        self.app_name = "chatHMD"        # アプリ名
        self.app_version = "1.0.0"       # バージョン
        # ...
```

### 署名・公証（macOS）
```bash
# 開発者IDで署名
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" chatHMD.app

# 公証
xcrun notarytool submit chatHMD-1.0.0-mac.dmg --keychain-profile "AC_PASSWORD"
```

### コード署名（Windows）
```bash
# SignToolを使用
signtool sign /f certificate.p12 /p password /t http://timestamp.verisign.com/scripts/timstamp.dll chatHMD-installer.exe
```

## 📦 配布戦略

### リリースチャネル
1. **Alpha**: 開発者向け早期版
2. **Beta**: テスター向けプレビュー版  
3. **Stable**: 一般ユーザー向け安定版

### 配布プラットフォーム
- **GitHub Releases**: 全プラットフォーム
- **Mac App Store**: macOS (審査後)
- **Microsoft Store**: Windows (審査後)
- **Snap Store**: Linux
- **公式サイト**: 直接ダウンロード

### 自動ビルド（CI/CD）
```yaml
# GitHub Actions例
name: Build Release
on:
  push:
    tags: ['v*']
jobs:
  build-mac:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - run: python3 build_mac_app.py
      
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - run: python build_windows.py
      
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python3 build_linux.py
```

## 🚨 トラブルシューティング

### よくある問題

#### macOS
- **"App can't be opened"**: 右クリック→開くで回避
- **依存関係エラー**: `pip3 install -r requirements.txt`

#### Windows  
- **Python not found**: PATH設定確認
- **アンチウイルス警告**: 例外設定に追加

#### Linux
- **Permission denied**: `chmod +x chatHMD.sh`
- **依存関係不足**: パッケージマネージャーで解決

### ログ確認
```bash
# アプリケーションログ
tail -f ~/.chatHMD/logs/app.log

# Streamlitログ  
tail -f ~/.streamlit/logs/streamlit.log
```

## 📈 配布指標

### 追跡すべきメトリクス
- ダウンロード数
- インストール成功率
- 初回起動率
- クラッシュレポート
- ユーザーフィードバック

### 分析ツール
- Google Analytics（Webサイト）
- Sentry（エラートラッキング）
- カスタムテレメトリー（オプトイン）

この配布戦略により、すべてのプラットフォームで統一された体験を提供しながら、各プラットフォームの特性を活かした最適なインストール方法を実現します。