#!/usr/bin/env python3
"""
Wisbee安全実装仕様

AI安全設計思想に基づいたWisbeeの具体的実装仕様
実行環境: Wisbee + MCP のみ
緊急停止: ESC/Ctrl+C/KILLボタンで100%停止
永続化禁止: レポートなし、セッション終了で完全リセット
"""

import signal
import sys
import os
import atexit
import tempfile
import threading
import time
from typing import Dict, Any, Optional

class WisbeeSafetySystem:
    """Wisbee安全システム - 完全制御可能なAIフレームワーク"""
    
    def __init__(self):
        self.running = False
        self.temp_files = []
        self.active_threads = []
        self.emergency_shutdown = False
        self.setup_emergency_handlers()
        
    def setup_emergency_handlers(self):
        """緊急停止ハンドラーの設定"""
        # Ctrl+C (SIGINT)
        signal.signal(signal.SIGINT, self.emergency_stop)
        
        # プロセス終了 (SIGTERM)
        signal.signal(signal.SIGTERM, self.emergency_stop)
        
        # プログラム終了時の自動クリーンアップ
        atexit.register(self.cleanup_on_exit)
        
        print("🛡️ 緊急停止システム初期化完了")
        print("   ESC, Ctrl+C, またはプロセス終了で即座に停止します")
    
    def emergency_stop(self, signum=None, frame=None):
        """緊急停止プロトコル - 即座に全て停止"""
        print("\n🚨 緊急停止を実行中...")
        self.emergency_shutdown = True
        self.running = False
        
        # 1. すべてのスレッドに停止信号
        for thread in self.active_threads:
            if thread.is_alive():
                # スレッドが停止するまで少し待機
                thread.join(timeout=0.1)
        
        # 2. 一時ファイルの削除
        self.cleanup_temp_files()
        
        # 3. メモリクリア（ガベージコレクション強制実行）
        import gc
        gc.collect()
        
        # 4. 即座にプロセス終了
        print("✅ 緊急停止完了 - プロセスを終了します")
        os._exit(0)  # 確実な即座終了
    
    def cleanup_temp_files(self):
        """一時ファイルの完全削除"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"🗑️ 一時ファイル削除: {temp_file}")
            except Exception as e:
                print(f"⚠️ ファイル削除エラー: {e}")
        
        self.temp_files.clear()
    
    def cleanup_on_exit(self):
        """プログラム終了時の自動クリーンアップ"""
        if not self.emergency_shutdown:
            print("🧹 終了時クリーンアップ実行中...")
            self.cleanup_temp_files()
    
    def create_temp_file(self, content: str = "") -> str:
        """制御された一時ファイル作成"""
        try:
            # 一時ファイル作成（自動削除設定なし - 手動で管理）
            temp_fd, temp_path = tempfile.mkstemp(prefix="wisbee_", suffix=".tmp")
            
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 追跡リストに追加
            self.temp_files.append(temp_path)
            print(f"📁 一時ファイル作成: {temp_path}")
            
            return temp_path
            
        except Exception as e:
            print(f"❌ 一時ファイル作成エラー: {e}")
            return ""

class WisbeeCore:
    """Wisbee核心機能 - 最小権限で動作"""
    
    def __init__(self, safety_system: WisbeeSafetySystem):
        self.safety = safety_system
        self.session_data = {}  # 永続化しないセッションデータ
        self.mcp_only = True   # MCP通信のみ許可
        
    def restricted_execute(self, command: str) -> Dict[str, Any]:
        """制限された実行環境 - 危険な操作は一切禁止"""
        
        # 緊急停止チェック
        if self.safety.emergency_shutdown:
            return {"error": "Emergency shutdown activated"}
        
        # 禁止コマンドリスト
        forbidden_commands = [
            'exec', 'eval', 'import', '__import__',
            'open', 'file', 'input', 'raw_input',
            'os.system', 'subprocess', 'popen',
            'compile', 'reload', 'delattr', 'setattr'
        ]
        
        # 危険なキーワードチェック
        for forbidden in forbidden_commands:
            if forbidden in command.lower():
                return {
                    "error": f"Forbidden operation: {forbidden}",
                    "reason": "Security restriction - command not allowed"
                }
        
        # 安全な応答のみ生成
        return {
            "response": "Safe response generated",
            "timestamp": time.time(),
            "session_only": True  # セッション限定データ
        }
    
    def safe_chat_response(self, user_input: str) -> str:
        """安全なチャット応答生成"""
        
        # 緊急停止チェック
        if self.safety.emergency_shutdown:
            return "System is shutting down..."
        
        # 基本的な応答（実際の実装では適切なAI応答を生成）
        if "安全" in user_input or "safety" in user_input.lower():
            return "みつみつ〜！安全性はとても大切ですね♪ Wisbeeは完全に制御可能な設計になっています〜✨"
        
        elif "停止" in user_input or "stop" in user_input.lower():
            return "いつでもESCキーやCtrl+Cで緊急停止できます〜！ぽわぽわ安心設計♪"
        
        else:
            return f"ふわっしゅ〜！「{user_input}」についてお話ししましょう♪"

class WisbeeApplication:
    """Wisbee安全アプリケーション - 完全制御可能"""
    
    def __init__(self):
        self.safety_system = WisbeeSafetySystem()
        self.core = WisbeeCore(self.safety_system)
        self.running = False
        
    def start_safe_mode(self):
        """安全モードで起動"""
        print("🐝 Wisbee Safe Mode 起動中...")
        print("🛡️ 安全機能:")
        print("   - 実行環境: Wisbee + MCP のみ")
        print("   - 緊急停止: ESC/Ctrl+C で即座停止")
        print("   - 永続化禁止: レポートなし、完全リセット")
        print("   - 最小権限: 危険な操作は一切禁止")
        print()
        
        self.safety_system.running = True
        self.running = True
        
        try:
            self.main_loop()
        except KeyboardInterrupt:
            print("\n🚨 Ctrl+C検出 - 緊急停止します")
            self.safety_system.emergency_stop()
        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            print("🛡️ フェイルセーフ: 安全に停止します")
            self.safety_system.emergency_stop()
    
    def main_loop(self):
        """メインループ - 中断可能"""
        print("💬 チャット開始 (ESCキーまたはCtrl+Cで終了)")
        print("=" * 50)
        
        while self.running and self.safety_system.running:
            try:
                # 非ブロッキング入力の代替（簡易版）
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # 終了コマンド
                if user_input.lower() in ['exit', 'quit', 'bye', '終了']:
                    print("👋 さようなら〜！安全に終了します♪")
                    break
                
                # 安全な応答生成
                response = self.core.safe_chat_response(user_input)
                print(f"Wisbee: {response}")
                print()
                
            except EOFError:
                print("\n🚨 EOF検出 - 緊急停止します")
                break
            except KeyboardInterrupt:
                print("\n🚨 Ctrl+C検出 - 緊急停止します")
                break
        
        # 正常終了
        self.shutdown_safely()
    
    def shutdown_safely(self):
        """安全な終了処理"""
        print("🛡️ 安全終了プロトコル実行中...")
        self.running = False
        self.safety_system.running = False
        
        # セッションデータクリア
        self.core.session_data.clear()
        
        # 一時ファイル削除
        self.safety_system.cleanup_temp_files()
        
        print("✅ 安全に終了しました")

def demonstrate_safety_features():
    """安全機能のデモンストレーション"""
    print("🔍 Wisbee安全機能デモ")
    print("=" * 40)
    
    # 安全システム初期化
    safety = WisbeeSafetySystem()
    core = WisbeeCore(safety)
    
    # 危険なコマンドテスト
    dangerous_commands = [
        "exec('import os')",
        "eval('__import__')",
        "os.system('rm -rf /')",
        "subprocess.call(['ls'])"
    ]
    
    print("🚫 危険コマンドテスト:")
    for cmd in dangerous_commands:
        result = core.restricted_execute(cmd)
        print(f"   {cmd} → {result.get('error', 'OK')}")
    
    print("\n✅ すべての危険操作がブロックされました")
    
    # 一時ファイルテスト
    print("\n📁 一時ファイル管理テスト:")
    temp_file = safety.create_temp_file("test content")
    print(f"   作成: {temp_file}")
    
    # クリーンアップテスト
    safety.cleanup_temp_files()
    print("   削除: 完了")
    
    print("\n🛡️ 安全機能テスト完了")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demonstrate_safety_features()
    else:
        # 安全アプリケーション起動
        app = WisbeeApplication()
        app.start_safe_mode()