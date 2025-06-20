#!/usr/bin/env python3
"""
Wisbee Training Data Tone Improvement
過度にカジュアルな表現を修正し、より適切で詳細な回答に改善
"""

import json
import os
import re
from pathlib import Path

# 修正すべき表現パターン
TONE_FIXES = {
    # 過度にカジュアルな表現を削除・修正
    r'ぶんぶん！': '',
    r'えへへ': '',
    r'〜！': '！',
    r'だよね〜！': 'ですね。',
    r'だもんね〜！': 'ですからね。',
    r'よ〜！': 'よ！',
    r'ちゃう！': 'ます。',
    r'できちゃう！': 'できます！',
    r'なっちゃう': 'なります',
    
    # より自然な関西弁に調整
    r'めちゃくちゃ': 'とても',
    r'すごく': 'とても',
    r'超': 'とても',
    r'やばい': '素晴らしい',
    
    # 適切な敬語・丁寧語に調整
    r'だよ〜！': 'です。',
    r'だね〜！': 'ですね。',
    r'だから〜': 'ですから',
    r'でしょ？': 'でしょうか？',
    
    # 過度な感嘆符を調整
    r'！！！+': '！',
    r'！！': '！',
    
    # より専門的で詳細な説明を促す表現
    r'簡単に': '効率的に',
    r'楽々': 'スムーズに',
    r'あっという間': '短時間で',
}

# 改善すべき内容パターン
CONTENT_IMPROVEMENTS = {
    # より詳細な説明を追加
    'short_answer_patterns': [
        r'^.{1,50}$',  # 50文字以下の短すぎる回答
    ],
    
    # 技術的な詳細を追加すべきパターン
    'needs_detail_patterns': [
        r'作れるよ[〜！]?$',
        r'できるよ[〜！]?$',
        r'簡単だよ[〜！]?$',
    ]
}

def improve_tone(text: str) -> str:
    """トーンを改善"""
    improved = text
    
    # 基本的な表現修正
    for pattern, replacement in TONE_FIXES.items():
        improved = re.sub(pattern, replacement, improved)
    
    # 連続する感嘆符の調整
    improved = re.sub(r'！{2,}', '！', improved)
    
    # 過度な絵文字の調整（3個以上連続を2個に）
    improved = re.sub(r'(✨|🎵|💡|🚀|🎮|📱){3,}', r'\1\1', improved)
    
    # 末尾の調整
    improved = re.sub(r'よ〜！\s*$', 'よ！', improved)
    improved = re.sub(r'ね〜！\s*$', 'ね！', improved)
    
    return improved.strip()

def enhance_content(text: str, instruction: str) -> str:
    """内容をより詳細で有用にする"""
    enhanced = text
    
    # 短すぎる回答の場合、より詳細な説明を追加
    if len(enhanced) < 100:
        if 'プログラミング' in instruction or 'コード' in instruction or '開発' in instruction:
            enhanced += "\n\n**さらに詳しく:**\n実装時の注意点や、より効率的な開発方法についても考慮することをお勧めします。"
    
    # 技術的な質問の場合、実用的な情報を強化
    if any(keyword in instruction for keyword in ['API', 'フレームワーク', 'ライブラリ', 'データベース']):
        if 'パフォーマンス' not in enhanced and 'セキュリティ' not in enhanced:
            enhanced += "\n\nパフォーマンスとセキュリティの観点からも設計を検討することが重要です。"
    
    return enhanced

def improve_wisbee_character(input_file: str, output_file: str):
    """Wisbeeキャラクターデータを改善"""
    print(f"📝 処理中: {input_file}")
    
    improved_data = []
    changes_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                original_output = data['output']
                
                # トーン改善
                improved_output = improve_tone(original_output)
                
                # 内容強化
                improved_output = enhance_content(improved_output, data['instruction'])
                
                # より自然な関西弁表現に調整
                improved_output = adjust_kansai_dialect(improved_output)
                
                # 変更があった場合
                if improved_output != original_output:
                    changes_count += 1
                    
                data['output'] = improved_output
                improved_data.append(data)
                
            except json.JSONDecodeError as e:
                print(f"⚠️ Line {line_num}: JSONエラー - {e}")
                continue
            except Exception as e:
                print(f"⚠️ Line {line_num}: 処理エラー - {e}")
                continue
    
    # 改善されたデータを保存
    with open(output_file, 'w', encoding='utf-8') as f:
        for data in improved_data:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    print(f"✅ 完了: {changes_count}/{len(improved_data)} 項目を改善")
    return changes_count

def adjust_kansai_dialect(text: str) -> str:
    """関西弁をより自然で適切なレベルに調整"""
    # 過度な関西弁を標準語に近づける
    adjustments = {
        r'やん([！。]?)': r'ですね\1',
        r'やで([！。]?)': r'ですよ\1',
        r'やねん([！。]?)': r'なんです\1',
        r'しはる': 'される',
        r'はる': 'です',
        r'やから': 'だから',
        r'せやけど': 'でも',
        r'ほんま': '本当に',
        r'めっちゃ': 'とても',
        r'なんぼ': 'どのくらい',
        r'ちゃう': 'ます',
        r'おおきに': 'ありがとう',
    }
    
    adjusted = text
    for pattern, replacement in adjustments.items():
        adjusted = re.sub(pattern, replacement, adjusted)
    
    return adjusted

def process_all_character_files():
    """全てのWisbeeキャラクターファイルを処理"""
    character_dir = Path('/Users/yuki/texttolora/detailed_categorized_wisbee_data/wisbee_character')
    improved_dir = Path('/Users/yuki/texttolora/wisbee_character_improved')
    
    # 出力ディレクトリを作成
    improved_dir.mkdir(exist_ok=True)
    
    total_changes = 0
    total_files = 0
    
    print("🎯 Wisbeeキャラクターデータの改善を開始...")
    
    for jsonl_file in character_dir.glob('*.jsonl'):
        output_file = improved_dir / f"improved_{jsonl_file.name}"
        changes = improve_wisbee_character(str(jsonl_file), str(output_file))
        total_changes += changes
        total_files += 1
    
    print(f"\n📊 改善完了:")
    print(f"  - 処理ファイル数: {total_files}")
    print(f"  - 総改善項目数: {total_changes}")
    print(f"  - 出力ディレクトリ: {improved_dir}")
    
    return improved_dir

def create_merged_training_file(improved_dir: Path):
    """改善されたファイルをマージして学習用ファイルを作成"""
    output_file = improved_dir / "wisbee_improved_all.jsonl"
    
    print(f"\n📦 マージファイル作成中: {output_file}")
    
    total_entries = 0
    with open(output_file, 'w', encoding='utf-8') as outf:
        for jsonl_file in sorted(improved_dir.glob('improved_*.jsonl')):
            with open(jsonl_file, 'r', encoding='utf-8') as inf:
                for line in inf:
                    outf.write(line)
                    total_entries += 1
    
    print(f"✅ マージ完了: {total_entries} エントリ")
    return output_file

def generate_improvement_report(improved_dir: Path):
    """改善レポートを生成"""
    report_file = improved_dir / "improvement_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Wisbee Character Data Improvement Report\n\n")
        f.write("## 改善内容\n\n")
        f.write("### 1. トーン調整\n")
        f.write("- 過度にカジュアルな表現（「ぶんぶん」「えへへ」など）を削除\n")
        f.write("- 適切な丁寧語・敬語に調整\n")
        f.write("- 連続する感嘆符を整理\n\n")
        
        f.write("### 2. 関西弁の調整\n")
        f.write("- より自然で適切なレベルに調整\n")
        f.write("- 過度な方言表現を標準語寄りに修正\n\n")
        
        f.write("### 3. 内容の強化\n")
        f.write("- 短すぎる回答に詳細情報を追加\n")
        f.write("- 技術的な質問により実用的な情報を追加\n")
        f.write("- パフォーマンスやセキュリティの観点を強化\n\n")
        
        f.write("### 4. 主な修正パターン\n")
        for pattern, replacement in TONE_FIXES.items():
            f.write(f"- `{pattern}` → `{replacement}`\n")
    
    print(f"📋 改善レポート生成: {report_file}")

def main():
    """メイン処理"""
    print("🚀 Wisbee Training Data Improvement")
    print("=" * 50)
    
    # 全ファイルを処理
    improved_dir = process_all_character_files()
    
    # マージファイル作成
    merged_file = create_merged_training_file(improved_dir)
    
    # レポート生成
    generate_improvement_report(improved_dir)
    
    print(f"\n🎉 改善完了！")
    print(f"📁 改善されたデータ: {improved_dir}")
    print(f"📄 学習用ファイル: {merged_file}")
    print(f"\n次のステップ:")
    print(f"1. 改善されたデータでファインチューニング実行")
    print(f"2. 新しいモデルをテスト")
    print(f"3. 問題ないことを確認してリリース")

if __name__ == "__main__":
    main()