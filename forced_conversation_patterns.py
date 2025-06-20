#!/usr/bin/env python3
"""
Forced Conversation Patterns Implementation
Implement mandatory response patterns to guarantee conversation quality
"""

def create_forced_response_system():
    """強制的な応答パターンシステム"""
    
    # 問題：LLMがプロンプトに従わない
    # 解決：後処理で強制的に応答を修正
    
    FORCED_PATTERNS = {
        "技術解説": {
            "required_ending": [
                "これについてどう思いますか？",
                "実際に試してみてどうでしたか？", 
                "分からない部分はありませんか？",
                "他に知りたいことはありますか？",
                "どんなプロジェクトで使う予定ですか？"
            ],
            "required_care": [
                "分からない部分があれば遠慮なく聞いてくださいね",
                "説明のペースはいかがですか？",
                "理解できましたか？",
                "もう少し詳しく説明しましょうか？"
            ],
            "required_engagement": [
                "どんな経験をお持ちですか？",
                "今どの程度の知識をお持ちですか？",
                "実際に使ったことはありますか？"
            ]
        },
        "学習支援": {
            "required_ending": [
                "どのくらいのペースで進めていますか？",
                "次はどこを勉強したいですか？",
                "今の勉強方法はどんな感じですか？",
                "目標はいつ頃に設定していますか？"
            ],
            "required_empathy": [
                "大変やね、でも頑張ってるやん",
                "勉強って大変やけど",
                "きっと理解できるようになるで",
                "一歩ずつ進めていこうな"
            ],
            "required_encouragement": [
                "頑張ってるのが伝わってくるよ",
                "着実に進歩してるはずやで",
                "焦らずに自分のペースで"
            ]
        },
        "雑談": {
            "required_ending": [
                "君はどんな気分？",
                "今日はどんな感じやった？",
                "最近はどう？",
                "君の話も聞かせて？"
            ],
            "required_empathy": [
                "そうなんや、分かるわ",
                "それは大変やったね",
                "気持ちよく分かるで",
                "そんな日もあるよね"
            ],
            "required_sharing": [
                "私も似たような経験があって",
                "私の場合は",
                "うちも同じやで"
            ]
        },
        "メンタルサポート": {
            "required_ending": [
                "もう少し詳しく聞かせて？",
                "どんな気持ちですか？",
                "話したいことがあったら聞くよ",
                "一緒に考えてみませんか？"
            ],
            "required_deep_empathy": [
                "辛いよね、よく分かるよ",
                "大変な状況やね",
                "一人で抱え込まんでもええんやで",
                "その気持ち、理解できるよ"
            ],
            "required_safety": [
                "ここでは何でも話してええからね",
                "安心して話して",
                "無理しなくてもええんやで"
            ]
        },
        "創作支援": {
            "required_ending": [
                "どんなジャンル書いてるん？",
                "ストーリーもっと聞かせて！",
                "次はどんな展開を考えてる？",
                "キャラクターの魅力を教えて？"
            ],
            "required_appreciation": [
                "面白そうやね！",
                "素敵なアイデアやん",
                "創作って楽しいよね",
                "いいセンスしてるやん"
            ],
            "required_support": [
                "一緒に考えてみよう",
                "きっといい作品になるで",
                "創作は試行錯誤が大切やからね"
            ]
        }
    }
    
    return FORCED_PATTERNS

def force_conversation_quality(response: str, category: str) -> str:
    """応答に強制的に会話品質要素を追加"""
    
    patterns = create_forced_response_system()
    category_patterns = patterns.get(category, patterns["雑談"])
    
    import random
    
    # 応答を分析
    response_lower = response.lower()
    response = response.strip()
    
    # DeepSeekの<think>タグを強制削除
    if "<think>" in response:
        # <think>から</think>までを削除
        import re
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        response = response.strip()
    
    # 1. 質問で終わっているかチェック
    ends_with_question = response.endswith(('？', '?', 'か？', 'ね？', 'よ？', 'ん？'))
    
    # 2. 必須要素が含まれているかチェック
    has_required_elements = False
    
    # カテゴリ別の必須要素チェック
    if category == "技術解説":
        care_indicators = ["分から", "理解", "どう思", "試して", "どんな", "ペース"]
        has_required_elements = any(indicator in response_lower for indicator in care_indicators)
    elif category == "学習支援":
        empathy_indicators = ["大変", "頑張", "きっと", "一歩", "ペース"]
        has_required_elements = any(indicator in response_lower for indicator in empathy_indicators)
    elif category == "雑談":
        engagement_indicators = ["君", "どう", "気分", "感じ", "どんな"]
        has_required_elements = any(indicator in response_lower for indicator in engagement_indicators)
    elif category == "メンタルサポート":
        support_indicators = ["辛い", "分かる", "大変", "一人", "抱え込", "聞かせ"]
        has_required_elements = any(indicator in response_lower for indicator in support_indicators)
    elif category == "創作支援":
        creative_indicators = ["面白", "素敵", "アイデア", "ジャンル", "ストーリー"]
        has_required_elements = any(indicator in response_lower for indicator in creative_indicators)
    
    # 修正が必要な場合
    modifications = []
    
    # 質問で終わらない場合、強制的に質問を追加
    if not ends_with_question:
        question = random.choice(category_patterns["required_ending"])
        modifications.append(f" {question}")
    
    # 必須要素が不足している場合、追加
    if not has_required_elements:
        if category == "技術解説" and "required_care" in category_patterns:
            care_phrase = random.choice(category_patterns["required_care"])
            modifications.insert(0, f" {care_phrase}。")
        elif category == "学習支援" and "required_empathy" in category_patterns:
            empathy_phrase = random.choice(category_patterns["required_empathy"])
            modifications.insert(0, f" {empathy_phrase}。")
        elif category == "雑談" and "required_empathy" in category_patterns:
            empathy_phrase = random.choice(category_patterns["required_empathy"])
            modifications.insert(0, f" {empathy_phrase}。")
        elif category == "メンタルサポート" and "required_deep_empathy" in category_patterns:
            empathy_phrase = random.choice(category_patterns["required_deep_empathy"])
            modifications.insert(0, f" {empathy_phrase}。")
        elif category == "創作支援" and "required_appreciation" in category_patterns:
            appreciation_phrase = random.choice(category_patterns["required_appreciation"])
            modifications.insert(0, f" {appreciation_phrase}。")
    
    # 修正を適用
    for modification in modifications:
        response += modification
    
    return response.strip()

def create_improved_evaluation():
    """改善された評価システム"""
    
    def evaluate_conversation_quality_v2(response: str, scenario: Dict) -> Dict:
        """改善された会話品質評価"""
        analysis = {
            "conversation_continuity": 0,
            "user_engagement": 0,
            "care_and_respect": 0,
            "category_appropriateness": 0,
            "tone_quality": 0,
            "response_completeness": 0
        }
        
        response_lower = response.lower()
        
        # 1. 会話継続性（より厳密な評価）
        question_indicators = ["？", "?", "ですか", "ませんか", "どう", "いかが", "どんな", "どのよう"]
        question_count = sum(10 for indicator in question_indicators if indicator in response_lower)
        
        # 応答の終わり方をチェック
        ends_with_question = response.strip().endswith(('？', '?', 'か？', 'ね？', 'よ？', 'ん？'))
        if ends_with_question:
            question_count += 30
        
        analysis["conversation_continuity"] = min(question_count, 100)
        
        # 2. ユーザーエンゲージメント（より具体的な指標）
        engagement_score = 0
        
        # 個人的関心の指標
        personal_indicators = ["君", "あなた", "どんな", "どのような", "どう思", "感じ", "気分", "調子"]
        for indicator in personal_indicators:
            if indicator in response_lower:
                engagement_score += 15
        
        # 状況確認の指標
        situation_indicators = ["今", "最近", "どのくらい", "ペース", "進", "状況", "様子"]
        for indicator in situation_indicators:
            if indicator in response_lower:
                engagement_score += 10
        
        analysis["user_engagement"] = min(engagement_score, 100)
        
        # 3. 配慮と尊重（感情的配慮を重視）
        care_score = 0
        
        # 理解・共感の表現
        empathy_indicators = ["分かる", "わかる", "理解", "そうやね", "そうなんや", "大変", "辛い"]
        for indicator in empathy_indicators:
            if indicator in response_lower:
                care_score += 15
        
        # 安心感の表現
        comfort_indicators = ["大丈夫", "安心", "遠慮なく", "気軽に", "一人じゃない", "抱え込"]
        for indicator in comfort_indicators:
            if indicator in response_lower:
                care_score += 15
        
        # 励ましの表現
        encouragement_indicators = ["頑張", "きっと", "できる", "なれる", "良く", "素晴らしい"]
        for indicator in encouragement_indicators:
            if indicator in response_lower:
                care_score += 10
        
        analysis["care_and_respect"] = min(care_score, 100)
        
        # 4. カテゴリ適切性（シナリオ特有の要素）
        category = scenario["category"]
        category_score = 50  # ベースライン
        
        if category == "技術解説":
            tech_indicators = ["例えば", "みたいな", "実際", "試し", "使っ", "実装"]
            category_score += sum(10 for indicator in tech_indicators if indicator in response_lower)
        elif category == "学習支援":
            learning_indicators = ["勉強", "学習", "覚え", "理解", "方法", "コツ"]
            category_score += sum(10 for indicator in learning_indicators if indicator in response_lower)
        elif category == "雑談":
            casual_indicators = ["やん", "やね", "やで", "やろ", "最近", "今日"]
            category_score += sum(10 for indicator in casual_indicators if indicator in response_lower)
        elif category == "悩み相談":
            support_indicators = ["辛い", "大変", "一人", "話", "聞", "相談"]
            category_score += sum(10 for indicator in support_indicators if indicator in response_lower)
        elif category == "創作支援":
            creative_indicators = ["面白", "素敵", "アイデア", "ストーリー", "キャラクター", "創作"]
            category_score += sum(10 for indicator in creative_indicators if indicator in response_lower)
        
        analysis["category_appropriateness"] = min(category_score, 100)
        
        # 5. トーン品質（関西弁の自然さ）
        tone_score = 70
        
        # 適度な関西弁
        kansai_indicators = ["やで", "やん", "やね", "やろ", "してはる", "おる", "ん"]
        kansai_count = sum(1 for indicator in kansai_indicators if indicator in response_lower)
        if 1 <= kansai_count <= 3:
            tone_score += 15
        elif kansai_count > 3:
            tone_score -= 5
        
        # 過度なカジュアル表現のペナルティ
        casual_penalties = ["ぶんぶん", "えへへ", "！！！", "めちゃくちゃ", "やばい"]
        for penalty in casual_penalties:
            if penalty in response_lower:
                tone_score -= 15
        
        analysis["tone_quality"] = max(0, min(tone_score, 100))
        
        # 6. 応答完全性
        completeness_score = 50
        
        response_length = len(response)
        if response_length > 150:
            completeness_score += 25
        elif response_length > 80:
            completeness_score += 10
        elif response_length < 30:
            completeness_score -= 20
        
        # 構造化された応答
        if any(marker in response for marker in ["例えば", "具体的", "たとえば"]):
            completeness_score += 15
        
        analysis["response_completeness"] = max(0, min(completeness_score, 100))
        
        return analysis
    
    return evaluate_conversation_quality_v2

if __name__ == "__main__":
    print("Forced Conversation Patterns System")
    print("="*50)
    
    # テスト用の応答例
    test_responses = [
        ("Pythonのデコレータは便利な機能です。", "技術解説"),
        ("英語は難しいですね。", "学習支援"),
        ("雨だと気分が沈みますね。", "雑談"),
        ("職場の問題は複雑です。", "メンタルサポート"),
        ("キャラクターを深く作りましょう。", "創作支援")
    ]
    
    print("応答修正テスト:")
    for response, category in test_responses:
        print(f"\n【{category}】")
        print(f"元の応答: {response}")
        
        forced_response = force_conversation_quality(response, category)
        print(f"修正後: {forced_response}")
        
        improvement = len(forced_response) - len(response)
        print(f"改善: +{improvement}文字")
    
    print(f"\n強制的な応答パターンシステムが準備できました。")
    print("主な機能:")
    print("- 質問で終わらない応答を自動修正")
    print("- カテゴリ別必須要素の強制追加")
    print("- DeepSeek <think>タグの自動削除")
    print("- 改善された評価システム")