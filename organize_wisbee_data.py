#!/usr/bin/env python3
"""
Wisbeeトレーニングデータ整理スクリプト

既存のWisbeeトレーニングデータを収集し、カテゴリ別に分類して
100サンプルごとのチャンクに分割します。
"""

import json
import os
import re
from collections import defaultdict
import hashlib

def load_jsonl_file(file_path):
    """JSONLファイルを読み込み、データのリストを返す"""
    if not os.path.exists(file_path):
        print(f"ファイルが見つかりません: {file_path}")
        return []
    
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        item = json.loads(line)
                        data.append(item)
                    except json.JSONDecodeError as e:
                        print(f"JSONデコードエラー {file_path}:{line_num}: {e}")
    except Exception as e:
        print(f"ファイル読み込みエラー {file_path}: {e}")
    
    return data

def categorize_sample(sample):
    """サンプルをカテゴリに分類"""
    text = ""
    if 'conversations' in sample:
        for conv in sample['conversations']:
            text += conv.get('value', '') + " "
    elif 'instruction' in sample and 'output' in sample:
        text += sample['instruction'] + " " + sample['output']
    elif 'messages' in sample:
        for msg in sample['messages']:
            text += msg.get('content', '') + " "
    
    text = text.lower()
    
    # プログラミング関連
    programming_keywords = [
        'python', 'javascript', 'html', 'css', 'プログラミング', 'コード', 'バグ', 
        'デバッグ', 'アルゴリズム', 'データ構造', '関数', 'クラス', 'オブジェクト',
        'api', 'フレームワーク', 'ライブラリ', 'git', 'github', 'sql', 'database'
    ]
    
    # 科学・数学関連
    science_keywords = [
        '数学', '物理', '化学', '生物', '科学', '実験', '理論', '公式', '方程式',
        '統計', '確率', '微積分', '代数', '幾何', '量子', '相対性理論', 'dna'
    ]
    
    # アート・文化関連
    art_keywords = [
        'アート', '芸術', '美術', '音楽', '文学', '詩', '小説', '映画', '演劇',
        '絵画', '彫刻', 'デザイン', '文化', '歴史', '哲学', '宗教', '伝統'
    ]
    
    # Hamada関連（特定のキャラクター）
    hamada_keywords = ['hamada', 'ハマダ', '浜田']
    
    # キーワードチェック
    if any(keyword in text for keyword in hamada_keywords):
        return 'hamada'
    elif any(keyword in text for keyword in programming_keywords):
        return 'programming'
    elif any(keyword in text for keyword in science_keywords):
        return 'science_math'
    elif any(keyword in text for keyword in art_keywords):
        return 'art_culture'
    else:
        return 'general'

def create_chunks(data, chunk_size=100):
    """データを指定サイズのチャンクに分割"""
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i:i + chunk_size])
    return chunks

def save_chunks(category, chunks, base_dir):
    """チャンクをファイルに保存"""
    category_dir = os.path.join(base_dir, category)
    os.makedirs(category_dir, exist_ok=True)
    
    for i, chunk in enumerate(chunks, 1):
        filename = f"{category}_chunk_{i:03d}.jsonl"
        filepath = os.path.join(category_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in chunk:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"保存完了: {filepath} ({len(chunk)}サンプル)")

def remove_duplicates(data):
    """重複するサンプルを除去"""
    seen_hashes = set()
    unique_data = []
    
    for item in data:
        # サンプルの内容をハッシュ化
        content = json.dumps(item, sort_keys=True, ensure_ascii=False)
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_data.append(item)
    
    return unique_data

def main():
    """メイン処理"""
    print("🐝 Wisbeeトレーニングデータ整理開始")
    
    # 入力ファイルのリスト
    input_files = [
        'wisbee_final_training_data.jsonl',
        'wisbee_complete_training_data.jsonl',
        'wisbee_training_data.jsonl',
        'wisbee_extended_training_data.jsonl',
        'balanced_wisbee_training_data.jsonl',
        'wisbee_hamada_training_data.jsonl',
        'wisbee_model_nft_training_data.jsonl'
    ]
    
    # 全データを収集
    all_data = []
    file_stats = {}
    
    for file_path in input_files:
        print(f"\n📁 ファイル処理中: {file_path}")
        data = load_jsonl_file(file_path)
        file_stats[file_path] = len(data)
        all_data.extend(data)
        print(f"   読み込み完了: {len(data)}サンプル")
    
    print(f"\n📊 総データ数: {len(all_data)}サンプル")
    
    # 重複除去
    print("\n🔄 重複除去中...")
    unique_data = remove_duplicates(all_data)
    print(f"   重複除去後: {len(unique_data)}サンプル")
    print(f"   除去された重複: {len(all_data) - len(unique_data)}サンプル")
    
    # カテゴリ別分類
    print("\n📂 カテゴリ別分類中...")
    categorized_data = defaultdict(list)
    
    for sample in unique_data:
        category = categorize_sample(sample)
        categorized_data[category].append(sample)
    
    # 分類結果の表示
    print("\n📈 分類結果:")
    total_samples = 0
    for category, data in categorized_data.items():
        print(f"   {category}: {len(data)}サンプル")
        total_samples += len(data)
    
    print(f"   合計: {total_samples}サンプル")
    
    # 出力ディレクトリの準備
    output_dir = "organized_wisbee_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # カテゴリ別にチャンク分割して保存
    print(f"\n💾 データ保存中（{output_dir}ディレクトリ）...")
    chunk_info = {}
    
    for category, data in categorized_data.items():
        print(f"\n📝 {category}カテゴリ処理中...")
        chunks = create_chunks(data, chunk_size=100)
        save_chunks(category, chunks, output_dir)
        chunk_info[category] = {
            'total_samples': len(data),
            'total_chunks': len(chunks),
            'samples_per_chunk': 100
        }
    
    # 統計情報をJSONファイルに保存
    stats = {
        'input_files': file_stats,
        'total_original_samples': len(all_data),
        'total_unique_samples': len(unique_data),
        'duplicates_removed': len(all_data) - len(unique_data),
        'categories': chunk_info,
        'output_directory': output_dir
    }
    
    stats_file = os.path.join(output_dir, 'organization_stats.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 統計情報を保存: {stats_file}")
    print("\n✅ データ整理完了！")
    
    # サマリーの表示
    print("\n" + "="*50)
    print("📋 整理サマリー")
    print("="*50)
    print(f"入力ファイル数: {len(input_files)}")
    print(f"元データ総数: {len(all_data):,}サンプル")
    print(f"重複除去後: {len(unique_data):,}サンプル")
    print(f"出力ディレクトリ: {output_dir}")
    print("\nカテゴリ別内訳:")
    for category, info in chunk_info.items():
        print(f"  {category}: {info['total_samples']:,}サンプル ({info['total_chunks']}チャンク)")

if __name__ == "__main__":
    main()