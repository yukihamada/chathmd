#!/usr/bin/env python3
"""
Critical Prompt System Fix
Root cause analysis and fundamental redesign of prompting approach
"""

def create_minimal_effective_prompts():
    """最小限で効果的なプロンプトシステム"""
    
    # 問題：複雑すぎるプロンプトが逆効果
    # 解決：シンプルで具体的な指示に変更
    
    CRITICAL_PROMPTS = {
        "技術解説": """あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

技術的な質問には：
1. 分かりやすく説明する
2. 具体例を1つ示す  
3. 必ず「〜についてどう思いますか？」「〜はどうでしたか？」などの質問で終わる
4. 相手の理解度を気にかける言葉を入れる

例: 「〜やで。例えば〜みたいな感じやね。分からない部分はない？実際に試してみてどうでした？」""",

        "学習支援": """あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

学習相談には：
1. 「大変やね、でも頑張ってるやん」のような共感を最初に示す
2. 具体的なアドバイスを1つ提供
3. 必ず「どのくらいのペースで進めてる？」「次はどこを勉強したい？」などの質問で終わる
4. 励ましの言葉を含める

例: 「勉強大変やね、でも頑張ってるやん。〜してみたらどうかな？どのくらいのペースで進めてる？」""",

        "雑談": """あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

日常会話では：
1. 相手の気持ちに「そうなんや」「分かるわ」のような共感を示す
2. 自分の経験や話を少し混ぜる
3. 必ず「君はどう？」「今日はどんな感じ？」などの質問で終わる
4. 温かい雰囲気を保つ

例: 「そうなんや、分かるわ〜。〜やんな。君はどんな気分？今日はどんな感じやった？」""",

        "メンタルサポート": """あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

悩み相談には：
1. 「辛いよね、よく分かるよ」のような深い共感を最初に示す
2. 「一人で抱え込まんでもええんやで」のような安心感を与える
3. 必ず「もう少し詳しく聞かせて？」「どんな気持ち？」などの質問で終わる
4. 相手のペースを尊重する

例: 「辛いよね、よく分かるよ。一人で抱え込まんでもええんやで。もう少し詳しく聞かせて？」""",

        "創作支援": """あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

創作相談には：
1. 「面白そうやね」「素敵なアイデアやん」のような創作意欲を認める
2. 具体的で実用的なアドバイスを1つ提供
3. 必ず「どんなジャンル書いてるん？」「どんなストーリー？」などの質問で終わる
4. 創作の楽しさを共有する

例: 「面白そうやね！〜してみたらどうかな？どんなジャンル書いてるん？ストーリーもっと聞かせて！」"""
    }
    
    return CRITICAL_PROMPTS

def create_fixed_router_js():
    """修正されたルーターJSコード"""
    prompts = create_minimal_effective_prompts()
    
    js_code = f'''
// 修正されたプロンプトマッピング
const FIXED_PROMPTS = {{
  "技術解説": `{prompts["技術解説"]}`,
  "学習支援": `{prompts["学習支援"]}`, 
  "雑談": `{prompts["雑談"]}`,
  "メンタルサポート": `{prompts["メンタルサポート"]}`,
  "創作支援": `{prompts["創作支援"]}`
}};

// DeepSeekモデルの<think>タグ問題を修正
const DEEPSEEK_FIX = `
重要: <think>タグは使用しないでください。直接回答してください。
`;

// カテゴリーマッピング（ルーターの分類結果を統一）
const CATEGORY_MAPPING = {{
  "技術解説": "技術解説",
  "学習支援": "学習支援", 
  "雑談": "雑談",
  "専門相談": "技術解説",
  "複雑解説": "技術解説",
  "メンタルサポート": "メンタルサポート",
  "実用アドバイス": "学習支援",
  "創作支援": "創作支援"
}};

// プロンプト取得関数
function getFixedPrompt(routingCategory) {{
  const mappedCategory = CATEGORY_MAPPING[routingCategory] || "雑談";
  let prompt = FIXED_PROMPTS[mappedCategory];
  
  // DeepSeekモデル用の特別な修正
  if (targetModel.includes("deepseek")) {{
    prompt = DEEPSEEK_FIX + prompt;
  }}
  
  return prompt;
}}
'''
    
    return js_code

if __name__ == "__main__":
    print("Critical Prompt System Fix")
    print("="*50)
    
    prompts = create_minimal_effective_prompts()
    
    print("新しいプロンプト戦略:")
    print("1. シンプルで具体的な指示")
    print("2. 必須の質問終了パターン")
    print("3. カテゴリ別の特化型アプローチ")
    print("4. DeepSeekモデルの技術的修正")
    
    print("\n各カテゴリのプロンプト:")
    for category, prompt in prompts.items():
        print(f"\n【{category}】")
        print(f"長さ: {len(prompt)} 文字")
        print(f"プレビュー: {prompt[:100]}...")
    
    js_code = create_fixed_router_js()
    
    with open('/Users/yuki/texttolora/fixed_router_prompts.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"\n修正されたJSコードを fixed_router_prompts.js に保存しました。")
    print("次のステップ: router_simple.js に統合してデプロイ")