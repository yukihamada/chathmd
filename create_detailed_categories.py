#!/usr/bin/env python3
"""
Wisbee詳細カテゴリ分類システム

トレーニングデータをより細かく詳細なカテゴリに分類し、
各カテゴリごとに適切な量のサンプルを振り分けます。
"""

import json
import os
import re
from collections import defaultdict
import hashlib
from typing import List, Dict, Any

class DetailedCategoryClassifier:
    def __init__(self):
        self.category_definitions = self._define_categories()
    
    def _define_categories(self) -> Dict[str, Dict]:
        """詳細カテゴリの定義"""
        return {
            # プログラミング・技術関連（細分化）
            'programming_python': {
                'keywords': ['python', 'pandas', 'numpy', 'django', 'flask', 'matplotlib', 'jupyter'],
                'description': 'Python関連のプログラミング',
                'priority': 1
            },
            'programming_web': {
                'keywords': ['html', 'css', 'javascript', 'react', 'vue', 'angular', 'node.js', 'typescript'],
                'description': 'Webプログラミング関連',
                'priority': 1
            },
            'programming_data': {
                'keywords': ['データベース', 'sql', 'nosql', 'mongodb', 'mysql', 'postgresql', 'データ分析'],
                'description': 'データベース・データ分析',
                'priority': 1
            },
            'programming_ai_ml': {
                'keywords': ['機械学習', 'ai', '人工知能', 'tensorflow', 'pytorch', 'scikit-learn', 'neural network'],
                'description': 'AI・機械学習関連',
                'priority': 1
            },
            'programming_general': {
                'keywords': ['プログラミング', 'コード', 'アルゴリズム', 'デバッグ', 'git', 'github'],
                'description': 'プログラミング一般',
                'priority': 2
            },
            
            # 科学・学術関連（細分化）
            'science_mathematics': {
                'keywords': ['数学', '微積分', '代数', '幾何', '統計', '確率', '方程式', '関数'],
                'description': '数学関連',
                'priority': 1
            },
            'science_physics': {
                'keywords': ['物理', '力学', '電磁気', '量子', '相対性理論', 'エネルギー', '波動'],
                'description': '物理学関連',
                'priority': 1
            },
            'science_chemistry': {
                'keywords': ['化学', '分子', '原子', '化学反応', '有機化学', '無機化学', '元素'],
                'description': '化学関連',
                'priority': 1
            },
            'science_biology': {
                'keywords': ['生物', 'dna', '遺伝子', '細胞', '進化', '生態系', '生物学'],
                'description': '生物学関連',
                'priority': 1
            },
            'science_general': {
                'keywords': ['科学', '実験', '理論', '研究', '論文', '仮説'],
                'description': '科学一般',
                'priority': 2
            },
            
            # 言語・文学関連（細分化）
            'language_japanese': {
                'keywords': ['日本語', 'ひらがな', 'カタカナ', '漢字', '敬語', '方言', '文法'],
                'description': '日本語・国語関連',
                'priority': 1
            },
            'language_english': {
                'keywords': ['english', '英語', '英会話', '文法', 'grammar', 'vocabulary', 'toeic'],
                'description': '英語関連',
                'priority': 1
            },
            'language_literature': {
                'keywords': ['文学', '小説', '詩', '俳句', '短歌', '作家', '文芸'],
                'description': '文学関連',
                'priority': 1
            },
            'language_writing': {
                'keywords': ['文章', '作文', 'エッセイ', '論文', '文章力', '表現'],
                'description': '文章作成・表現',
                'priority': 1
            },
            
            # アート・クリエイティブ関連（細分化）
            'art_visual': {
                'keywords': ['絵画', 'イラスト', 'デザイン', '色彩', '構図', '美術', 'アート'],
                'description': '視覚芸術関連',
                'priority': 1
            },
            'art_music': {
                'keywords': ['音楽', '楽器', '作曲', '歌', 'メロディ', 'リズム', '楽譜'],
                'description': '音楽関連',
                'priority': 1
            },
            'art_performance': {
                'keywords': ['演劇', 'ダンス', 'パフォーマンス', '舞台', '演技'],
                'description': 'パフォーマンス芸術',
                'priority': 1
            },
            'art_crafts': {
                'keywords': ['工芸', '陶芸', '彫刻', '手作り', 'diy', 'クラフト'],
                'description': '工芸・手作り',
                'priority': 1
            },
            
            # 歴史・文化関連（細分化）
            'history_japanese': {
                'keywords': ['日本史', '戦国', '江戸', '明治', '昭和', '平成', '天皇', '幕府'],
                'description': '日本史関連',
                'priority': 1
            },
            'history_world': {
                'keywords': ['世界史', 'ヨーロッパ', 'アメリカ', '中国', '古代', '中世', '近世'],
                'description': '世界史関連',
                'priority': 1
            },
            'culture_traditional': {
                'keywords': ['伝統', '文化', '祭り', '茶道', '華道', '書道', '武道'],
                'description': '伝統文化関連',
                'priority': 1
            },
            'culture_modern': {
                'keywords': ['現代文化', 'ポップカルチャー', 'アニメ', 'マンガ', 'ゲーム'],
                'description': '現代文化関連',
                'priority': 1
            },
            
            # ビジネス・経済関連（細分化）
            'business_management': {
                'keywords': ['経営', 'マネジメント', 'リーダーシップ', '組織', '戦略'],
                'description': '経営・マネジメント',
                'priority': 1
            },
            'business_finance': {
                'keywords': ['金融', '投資', '株式', '経済', '会計', '財務'],
                'description': '金融・経済関連',
                'priority': 1
            },
            'business_marketing': {
                'keywords': ['マーケティング', '広告', 'ブランド', '宣伝', '販売'],
                'description': 'マーケティング関連',
                'priority': 1
            },
            
            # 健康・医療関連（細分化）
            'health_medical': {
                'keywords': ['医療', '病気', '治療', '薬', '医師', '看護', '病院'],
                'description': '医療関連',
                'priority': 1
            },
            'health_fitness': {
                'keywords': ['健康', '運動', 'フィットネス', 'ダイエット', '筋トレ', 'ヨガ'],
                'description': '健康・フィットネス',
                'priority': 1
            },
            'health_nutrition': {
                'keywords': ['栄養', '食事', '食品', 'ビタミン', 'カロリー', '食べ物'],
                'description': '栄養・食事関連',
                'priority': 1
            },
            
            # 生活・趣味関連（細分化）
            'lifestyle_cooking': {
                'keywords': ['料理', 'レシピ', '調理', '食材', 'グルメ', '味'],
                'description': '料理・グルメ関連',
                'priority': 1
            },
            'lifestyle_travel': {
                'keywords': ['旅行', '観光', '旅', '海外', '国内', 'ホテル', '交通'],
                'description': '旅行・観光関連',
                'priority': 1
            },
            'lifestyle_hobbies': {
                'keywords': ['趣味', 'スポーツ', 'ゲーム', '読書', '映画', '音楽鑑賞'],
                'description': '趣味・娯楽関連',
                'priority': 1
            },
            'lifestyle_fashion': {
                'keywords': ['ファッション', '服', 'おしゃれ', 'スタイル', 'ブランド'],
                'description': 'ファッション関連',
                'priority': 1
            },
            
            # 教育・学習関連（細分化）
            'education_elementary': {
                'keywords': ['小学校', '小学生', '基礎', '算数', '国語', 'ひらがな'],
                'description': '小学校教育関連',
                'priority': 1
            },
            'education_secondary': {
                'keywords': ['中学校', '高校', '受験', '進学', '部活', '青春'],
                'description': '中等教育関連',
                'priority': 1
            },
            'education_higher': {
                'keywords': ['大学', '大学院', '研究', '論文', '学会', '専門'],
                'description': '高等教育関連',
                'priority': 1
            },
            'education_methods': {
                'keywords': ['勉強法', '学習', '記憶', '集中', '効率', '方法'],
                'description': '学習方法・技術',
                'priority': 1
            },
            
            # 哲学・思想関連（細分化）
            'philosophy_western': {
                'keywords': ['哲学', 'プラトン', 'アリストテレス', 'カント', 'ニーチェ'],
                'description': '西洋哲学関連',
                'priority': 1
            },
            'philosophy_eastern': {
                'keywords': ['東洋哲学', '仏教', '禅', '儒教', '老子', '孔子'],
                'description': '東洋哲学関連',
                'priority': 1
            },
            'philosophy_ethics': {
                'keywords': ['倫理', '道徳', '善悪', '正義', '人権', '価値観'],
                'description': '倫理・道徳関連',
                'priority': 1
            },
            
            # 社会・政治関連（細分化）
            'society_politics': {
                'keywords': ['政治', '政府', '選挙', '民主主義', '政策', '国会'],
                'description': '政治関連',
                'priority': 1
            },
            'society_law': {
                'keywords': ['法律', '法', '裁判', '弁護士', '判決', '権利'],
                'description': '法律関連',
                'priority': 1
            },
            'society_issues': {
                'keywords': ['社会問題', '環境', '格差', '差別', 'ジェンダー', '人権'],
                'description': '社会問題関連',
                'priority': 1
            },
            
            # 環境・自然関連（細分化）
            'environment_ecology': {
                'keywords': ['環境', '生態系', '自然', '動物', '植物', '森林', '海洋'],
                'description': '環境・生態系関連',
                'priority': 1
            },
            'environment_climate': {
                'keywords': ['気候', '天気', '気象', '温暖化', '気候変動', '災害'],
                'description': '気候・気象関連',
                'priority': 1
            },
            
            # 心理・感情関連（細分化）
            'psychology_cognitive': {
                'keywords': ['心理学', '認知', '記憶', '学習', '知覚', '思考'],
                'description': '認知心理学関連',
                'priority': 1
            },
            'psychology_emotional': {
                'keywords': ['感情', '気持ち', 'ストレス', '癒し', '幸せ', '悲しみ'],
                'description': '感情・メンタルヘルス',
                'priority': 1
            },
            'psychology_social': {
                'keywords': ['社会心理学', '人間関係', 'コミュニケーション', '集団'],
                'description': '社会心理学関連',
                'priority': 1
            },
            
            # Wisbeeキャラクター関連
            'wisbee_character': {
                'keywords': ['wisbee', 'ウィズビー', 'みつばち', 'ぶんぶん', 'はちみつ'],
                'description': 'Wisbeeキャラクター関連',
                'priority': 0  # 最高優先度
            },
            
            # その他・一般
            'general_conversation': {
                'keywords': ['こんにちは', 'ありがとう', 'お疲れ様', '挨拶', '日常'],
                'description': '一般的な会話',
                'priority': 3
            },
            'general_other': {
                'keywords': [],  # キーワードなし（その他すべて）
                'description': 'その他・未分類',
                'priority': 4  # 最低優先度
            }
        }
    
    def classify_sample(self, sample: Dict[str, Any]) -> str:
        """サンプルを詳細カテゴリに分類"""
        text = self._extract_text_from_sample(sample)
        text_lower = text.lower()
        
        # 各カテゴリとのマッチング度を計算
        category_scores = {}
        
        for category, definition in self.category_definitions.items():
            score = 0
            keywords = definition['keywords']
            priority = definition['priority']
            
            # キーワードマッチング
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            # 優先度による重み付け（優先度が低いほど重要）
            if score > 0:
                weight = 5 - priority  # priority 0->5, 1->4, 2->3, 3->2, 4->1
                category_scores[category] = score * weight
        
        # 最高スコアのカテゴリを選択
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            return best_category
        
        # マッチするカテゴリがない場合はgeneral_other
        return 'general_other'
    
    def _extract_text_from_sample(self, sample: Dict[str, Any]) -> str:
        """サンプルからテキストを抽出"""
        text = ""
        
        if 'conversations' in sample:
            for conv in sample['conversations']:
                text += conv.get('value', '') + " "
        elif 'instruction' in sample and 'output' in sample:
            text += sample['instruction'] + " " + sample['output']
        elif 'messages' in sample:
            for msg in sample['messages']:
                text += msg.get('content', '') + " "
        elif 'text' in sample:
            text += sample['text']
        
        return text

def load_jsonl_file(file_path: str) -> List[Dict[str, Any]]:
    """JSONLファイルを読み込み"""
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

def save_categorized_data(categorized_data: Dict[str, List], output_dir: str, samples_per_file: int = 100):
    """カテゴリ別データをファイルに保存"""
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = {}
    
    for category, samples in categorized_data.items():
        if not samples:
            continue
            
        category_dir = os.path.join(output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # ファイル分割
        file_count = 0
        for i in range(0, len(samples), samples_per_file):
            file_count += 1
            chunk = samples[i:i + samples_per_file]
            filename = f"{category}_{file_count:03d}.jsonl"
            filepath = os.path.join(category_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for sample in chunk:
                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')
            
            print(f"保存: {filepath} ({len(chunk)}サンプル)")
        
        saved_files[category] = {
            'total_samples': len(samples),
            'total_files': file_count,
            'samples_per_file': samples_per_file
        }
    
    return saved_files

def create_category_summary(classifier: DetailedCategoryClassifier, categorized_data: Dict[str, List], output_dir: str):
    """カテゴリサマリーを作成"""
    summary = {
        'total_categories': len(categorized_data),
        'total_samples': sum(len(samples) for samples in categorized_data.values()),
        'categories': {}
    }
    
    for category, samples in categorized_data.items():
        definition = classifier.category_definitions.get(category, {})
        summary['categories'][category] = {
            'sample_count': len(samples),
            'description': definition.get('description', ''),
            'keywords': definition.get('keywords', []),
            'priority': definition.get('priority', 99)
        }
    
    # サマリーファイルを保存
    summary_file = os.path.join(output_dir, 'category_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return summary

def main():
    """メイン処理"""
    print("🐝 Wisbee詳細カテゴリ分類システム開始")
    
    # 分類器を初期化
    classifier = DetailedCategoryClassifier()
    print(f"📂 定義済みカテゴリ数: {len(classifier.category_definitions)}")
    
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
    
    # 全データを読み込み
    all_data = []
    for file_path in input_files:
        if os.path.exists(file_path):
            print(f"📁 読み込み中: {file_path}")
            data = load_jsonl_file(file_path)
            all_data.extend(data)
            print(f"   {len(data)}サンプル読み込み完了")
    
    print(f"\n📊 総データ数: {len(all_data)}サンプル")
    
    # 重複除去
    print("🔄 重複除去中...")
    seen_hashes = set()
    unique_data = []
    
    for item in all_data:
        content = json.dumps(item, sort_keys=True, ensure_ascii=False)
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_data.append(item)
    
    print(f"   重複除去後: {len(unique_data)}サンプル")
    print(f"   除去された重複: {len(all_data) - len(unique_data)}サンプル")
    
    # 詳細カテゴリ分類
    print("\n🔍 詳細カテゴリ分類中...")
    categorized_data = defaultdict(list)
    
    for i, sample in enumerate(unique_data):
        if i % 500 == 0:
            print(f"   進捗: {i}/{len(unique_data)} ({i/len(unique_data)*100:.1f}%)")
        
        category = classifier.classify_sample(sample)
        categorized_data[category].append(sample)
    
    print("   分類完了")
    
    # 分類結果の表示
    print("\n📈 詳細分類結果:")
    sorted_categories = sorted(categorized_data.items(), key=lambda x: len(x[1]), reverse=True)
    
    for category, samples in sorted_categories:
        definition = classifier.category_definitions.get(category, {})
        description = definition.get('description', '')
        print(f"   {category}: {len(samples)}サンプル ({description})")
    
    # 出力ディレクトリ
    output_dir = "detailed_categorized_wisbee_data"
    print(f"\n💾 データ保存中（{output_dir}ディレクトリ）...")
    
    # カテゴリ別データを保存
    saved_files = save_categorized_data(categorized_data, output_dir, samples_per_file=100)
    
    # サマリー作成
    summary = create_category_summary(classifier, categorized_data, output_dir)
    
    print(f"\n📊 カテゴリサマリー保存: {output_dir}/category_summary.json")
    print("\n✅ 詳細カテゴリ分類完了！")
    
    # 最終サマリー表示
    print("\n" + "="*60)
    print("📋 詳細分類サマリー")
    print("="*60)
    print(f"総カテゴリ数: {len(categorized_data)}")
    print(f"総サンプル数: {len(unique_data):,}")
    print(f"出力ディレクトリ: {output_dir}")
    print("\n上位10カテゴリ:")
    
    for i, (category, samples) in enumerate(sorted_categories[:10]):
        definition = classifier.category_definitions.get(category, {})
        description = definition.get('description', '')
        print(f"  {i+1:2d}. {category}: {len(samples):,}サンプル ({description})")

if __name__ == "__main__":
    main()