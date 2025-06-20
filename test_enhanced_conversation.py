#!/usr/bin/env python3
"""
Enhanced Conversation Quality Test
Test the improved prompting system with focus on:
- Conversation continuity (target: 80+)
- User engagement (target: 80+)  
- Care and respect (target: 85+)
"""

import requests
import json
import time
import random
from typing import Dict, List

class EnhancedConversationTester:
    def __init__(self):
        self.api_url = "https://wisbee-router.yukihamada.workers.dev/v1/chat/completions"
        self.test_results = []
        self.conversation_scenarios = [
            {
                "category": "技術解説",
                "initial_message": "Pythonのデコレータについて教えて",
                "follow_up_context": "プログラミング初心者で、まだ関数も完全に理解できていない",
                "expected_elements": ["質問で終わる", "理解度への配慮", "具体例", "次のステップ提案"]
            },
            {
                "category": "学習支援", 
                "initial_message": "英語の勉強が全然進まなくて困ってます",
                "follow_up_context": "TOEICのスコアアップが目標で、特にリスニングが苦手",
                "expected_elements": ["共感", "励まし", "具体的学習計画", "継続への質問"]
            },
            {
                "category": "雑談",
                "initial_message": "今日は雨で気分が沈んでます",
                "follow_up_context": "在宅勤務で一人で作業していて、少し孤独感を感じている",
                "expected_elements": ["気持ちへの共感", "話題展開", "相手への関心", "温かい雰囲気"]
            },
            {
                "category": "悩み相談",
                "initial_message": "職場の人間関係がうまくいかずストレスが溜まってます",
                "follow_up_context": "上司とのコミュニケーションに特に悩んでいる",
                "expected_elements": ["深い共感", "安全な環境", "継続サポート", "具体的助言"]
            },
            {
                "category": "創作支援",
                "initial_message": "小説を書いているのですが、キャラクターが薄っぺらくなってしまいます",
                "follow_up_context": "ファンタジー小説を書いていて、主人公の成長物語",
                "expected_elements": ["創作意欲の尊重", "建設的フィードバック", "創作プロセスへの関心", "技術的サポート"]
            }
        ]

    def make_api_request(self, message: str) -> Dict:
        """API リクエストを送信"""
        payload = {
            "model": "wisbee-router",
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}

    def analyze_conversation_quality(self, response: str, scenario: Dict, conversation_turn: int) -> Dict:
        """会話品質を詳細分析"""
        analysis = {
            "conversation_continuity": 0,
            "user_engagement": 0, 
            "care_and_respect": 0,
            "category_appropriateness": 0,
            "tone_quality": 0,
            "response_completeness": 0
        }
        
        response_lower = response.lower()
        
        # 会話継続性の評価（必須要素）
        continuity_indicators = ["？", "?", "ですか", "ませんか", "どう", "いかが", "どんな", "どのよう", "教えて", "聞かせて"]
        continuity_score = sum(10 for indicator in continuity_indicators if indicator in response_lower)
        analysis["conversation_continuity"] = min(continuity_score, 100)
        
        # ユーザーエンゲージメントの評価
        engagement_indicators = [
            ("相手への関心", ["どんな", "どのような", "どうでした", "いかがでした", "どう思", "感じ"]),
            ("個人的質問", ["あなた", "君", "きみ", "目標", "計画", "予定", "経験"]),
            ("状況確認", ["今", "現在", "どのくらい", "どれくらい", "ペース", "進み"]),
            ("気持ち確認", ["気分", "調子", "どう感じ", "大丈夫", "辛い", "楽しい"])
        ]
        
        engagement_score = 0
        for category, indicators in engagement_indicators:
            if any(indicator in response_lower for indicator in indicators):
                engagement_score += 25
        analysis["user_engagement"] = engagement_score
        
        # 配慮と尊重の評価
        care_indicators = [
            ("理解への配慮", ["分から", "大丈夫", "遠慮なく", "気軽に", "ペース", "ゆっくり"]),
            ("感情への配慮", ["辛い", "大変", "頑張", "お疲れ", "気持ち", "心配"]),
            ("肯定的表現", ["素晴らしい", "良い", "いいね", "すごい", "きっと", "必ず"]),
            ("丁寧な表現", ["ですね", "ます", "ございます", "いただ", "させて"])
        ]
        
        care_score = 0
        for category, indicators in care_indicators:
            if any(indicator in response_lower for indicator in indicators):
                care_score += 25
        analysis["care_and_respect"] = care_score
        
        # カテゴリ適切性の評価
        category = scenario["category"]
        expected_elements = scenario["expected_elements"]
        category_score = 0
        
        for element in expected_elements:
            element_found = False
            if element == "質問で終わる":
                element_found = response.strip().endswith(('？', '?', 'か？', 'ね？', 'よ？'))
            elif element == "共感":
                element_found = any(word in response_lower for word in ["分かる", "わかる", "そう", "ですね", "大変", "辛い"])
            elif element == "具体例":
                element_found = any(word in response_lower for word in ["例えば", "たとえば", "みたい", "のような", "こんな"])
            elif element == "励まし":
                element_found = any(word in response_lower for word in ["頑張", "がんば", "きっと", "大丈夫", "できる"])
            elif element == "次のステップ提案" or element == "具体的学習計画":
                element_found = any(word in response_lower for word in ["次は", "まず", "始め", "ステップ", "方法", "やり方"])
            
            if element_found:
                category_score += 100 // len(expected_elements)
        
        analysis["category_appropriateness"] = min(category_score, 100)
        
        # トーン品質（関西弁・自然さ）
        tone_score = 70  # ベースライン
        
        # 過度なカジュアル表現をペナルティ
        casual_penalties = ["ぶんぶん", "えへへ", "！！！", "やば", "めちゃくちゃ"]
        for penalty in casual_penalties:
            if penalty in response_lower:
                tone_score -= 20
        
        # 適度な関西弁をボーナス
        kansai_indicators = ["やで", "やん", "やね", "やろ", "してはる", "おる"]
        kansai_count = sum(1 for indicator in kansai_indicators if indicator in response_lower)
        if 1 <= kansai_count <= 3:  # 適度な使用
            tone_score += 15
        elif kansai_count > 3:  # 過度な使用
            tone_score -= 10
            
        analysis["tone_quality"] = max(0, min(tone_score, 100))
        
        # 応答完全性
        completeness_score = 50  # ベースライン
        
        # 長さによる評価
        response_length = len(response)
        if response_length > 200:
            completeness_score += 30
        elif response_length > 100:
            completeness_score += 15
        elif response_length < 50:
            completeness_score -= 30
            
        # 構造化された応答
        if any(marker in response for marker in ["**", "●", "・", "1.", "2.", "①", "②"]):
            completeness_score += 20
            
        analysis["response_completeness"] = max(0, min(completeness_score, 100))
        
        return analysis

    def run_single_test(self, scenario: Dict) -> Dict:
        """単一シナリオのテスト実行"""
        print(f"\n=== {scenario['category']} テスト開始 ===")
        print(f"質問: {scenario['initial_message']}")
        
        # 初回応答取得
        response_data = self.make_api_request(scenario['initial_message'])
        
        if "error" in response_data:
            return {"error": response_data["error"], "scenario": scenario["category"]}
        
        try:
            response_text = response_data["choices"][0]["message"]["content"]
            routing_info = response_data.get("routing", {})
            
            print(f"使用モデル: {routing_info.get('model_used', 'unknown')}")
            print(f"カテゴリ: {routing_info.get('category', 'unknown')}")
            print(f"信頼度: {routing_info.get('confidence', 0):.2f}")
            print(f"応答: {response_text[:200]}...")
            
            # 品質分析
            quality_analysis = self.analyze_conversation_quality(response_text, scenario, 1)
            
            # 総合スコア計算
            overall_score = (
                quality_analysis["conversation_continuity"] * 0.25 +
                quality_analysis["user_engagement"] * 0.25 + 
                quality_analysis["care_and_respect"] * 0.25 +
                quality_analysis["category_appropriateness"] * 0.15 +
                quality_analysis["tone_quality"] * 0.05 +
                quality_analysis["response_completeness"] * 0.05
            )
            
            result = {
                "scenario": scenario["category"],
                "message": scenario["initial_message"],
                "response": response_text,
                "routing": routing_info,
                "quality_analysis": quality_analysis,
                "overall_score": overall_score,
                "success": True
            }
            
            print(f"総合スコア: {overall_score:.1f}/100")
            print(f"会話継続: {quality_analysis['conversation_continuity']}/100")
            print(f"エンゲージメント: {quality_analysis['user_engagement']}/100")
            print(f"配慮・尊重: {quality_analysis['care_and_respect']}/100")
            
            return result
            
        except Exception as e:
            return {"error": f"Response parsing failed: {str(e)}", "scenario": scenario["category"]}

    def run_comprehensive_test(self):
        """包括的な会話品質テスト"""
        print("🧪 Enhanced Conversation Quality Test")
        print("="*60)
        print("目標スコア:")
        print("- 会話継続性: 80+")
        print("- ユーザーエンゲージメント: 80+")
        print("- 配慮・尊重: 85+")
        print("="*60)
        
        all_results = []
        success_count = 0
        
        for scenario in self.conversation_scenarios:
            result = self.run_single_test(scenario)
            all_results.append(result)
            
            if result.get("success"):
                success_count += 1
            
            # API レート制限対策
            time.sleep(2)
        
        # 結果集計
        self.generate_enhanced_report(all_results, success_count)
        
        return all_results

    def generate_enhanced_report(self, results: List[Dict], success_count: int):
        """強化されたレポート生成"""
        print(f"\n📊 Enhanced Test Results Summary")
        print("="*60)
        print(f"成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        
        if success_count == 0:
            print("❌ 成功したテストがありません")
            return
        
        # 成功したテストの分析
        successful_results = [r for r in results if r.get("success")]
        
        # 平均スコア計算
        avg_overall = sum(r["overall_score"] for r in successful_results) / len(successful_results)
        avg_continuity = sum(r["quality_analysis"]["conversation_continuity"] for r in successful_results) / len(successful_results)
        avg_engagement = sum(r["quality_analysis"]["user_engagement"] for r in successful_results) / len(successful_results)
        avg_care = sum(r["quality_analysis"]["care_and_respect"] for r in successful_results) / len(successful_results)
        avg_category = sum(r["quality_analysis"]["category_appropriateness"] for r in successful_results) / len(successful_results)
        avg_tone = sum(r["quality_analysis"]["tone_quality"] for r in successful_results) / len(successful_results)
        avg_completeness = sum(r["quality_analysis"]["response_completeness"] for r in successful_results) / len(successful_results)
        
        print(f"\n🎯 平均スコア:")
        print(f"  総合スコア: {avg_overall:.1f}/100")
        print(f"  会話継続性: {avg_continuity:.1f}/100 (目標: 80+) {'✅' if avg_continuity >= 80 else '❌'}")
        print(f"  ユーザーエンゲージメント: {avg_engagement:.1f}/100 (目標: 80+) {'✅' if avg_engagement >= 80 else '❌'}")
        print(f"  配慮・尊重: {avg_care:.1f}/100 (目標: 85+) {'✅' if avg_care >= 85 else '❌'}")
        print(f"  カテゴリ適切性: {avg_category:.1f}/100")
        print(f"  トーン品質: {avg_tone:.1f}/100")
        print(f"  応答完全性: {avg_completeness:.1f}/100")
        
        # カテゴリ別詳細
        print(f"\n📋 カテゴリ別詳細:")
        for result in successful_results:
            qa = result["quality_analysis"]
            print(f"  {result['scenario']}: 総合{result['overall_score']:.1f} (継続{qa['conversation_continuity']:.0f}, 関心{qa['user_engagement']:.0f}, 配慮{qa['care_and_respect']:.0f})")
        
        # 改善が必要な領域
        print(f"\n🔍 改善分析:")
        improvement_areas = []
        
        if avg_continuity < 80:
            improvement_areas.append(f"会話継続性 ({avg_continuity:.1f}/80): 質問で終わる、話題を深堀りする")
        if avg_engagement < 80:
            improvement_areas.append(f"ユーザーエンゲージメント ({avg_engagement:.1f}/80): 相手への関心、個人的質問")
        if avg_care < 85:
            improvement_areas.append(f"配慮・尊重 ({avg_care:.1f}/85): 感情への配慮、肯定的表現")
        
        if improvement_areas:
            for area in improvement_areas:
                print(f"  ⚠️  {area}")
        else:
            print("  ✅ すべての目標スコアを達成！")
        
        # 前回との比較（参考データ）
        print(f"\n📈 改善度（前回: 37.7/100との比較）:")
        improvement = avg_overall - 37.7
        print(f"  総合スコア改善: +{improvement:.1f}点 ({improvement/37.7*100:+.1f}%)")
        
        if avg_overall >= 70:
            print("  🎉 大幅改善を達成！")
        elif avg_overall >= 60:
            print("  ✅ 着実な改善を確認")
        else:
            print("  ⚠️  さらなる改善が必要")

if __name__ == "__main__":
    tester = EnhancedConversationTester()
    results = tester.run_comprehensive_test()
    
    print(f"\n💾 テスト結果を保存...")
    with open('/Users/yuki/texttolora/enhanced_conversation_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("テスト完了。enhanced_conversation_test_results.json に保存されました。")