/**
 * Wisbee Intelligent Router API - Simple Public Version
 * CloudWorker function with basic abuse protection
 */

// Router configuration (same as before)
const ROUTER_CONFIG = {
  categories: {
    "技術解説": {
      keywords: ["プログラ", "コード", "実装", "エラー", "API", "関数", "アルゴリズム", "データベース", "JavaScript", "Python", "技術", "開発"],
      patterns: [/.*の(実装|使い方|違い).*/, /.*エラー.*修正.*/, /.*について(教えて|説明).*/],
      optimal_model: "llama-3.3-70b-versatile"
    },
    "学習支援": {
      keywords: ["勉強", "学習", "覚え", "理解", "苦手", "できる", "わからない", "教えて"],
      patterns: [/.*が(苦手|できない|わからない).*/, /.*勉強(方法|の仕方).*/],
      optimal_model: "llama-3.3-70b-versatile"
    },
    "創作支援": {
      keywords: ["小説", "物語", "キャラクター", "ストーリー", "アイデア", "企画", "創作", "設定"],
      patterns: [/.*の(アイデア|企画|設定).*/, /.*を考えて.*/],
      optimal_model: "llama-3.1-8b-instant"
    },
    "雑談": {
      keywords: ["どう", "思う", "最近", "今日", "昨日", "天気", "元気", "楽しい", "面白い", "やん", "やろ"],
      patterns: [/.*どう(思う|？|\?)/, /(今日|最近|昨日).*/, /.*やん.*/, /.*やろ.*/],
      optimal_model: "deepseek-r1-distill-llama-70b"
    },
    "専門相談": {
      keywords: ["ビジネス", "起業", "法律", "医療", "税金", "契約", "投資", "経営"],
      patterns: [/.*について(相談|アドバイス).*/, /.*の(注意点|ポイント).*/],
      optimal_model: "llama-3.3-70b-versatile"
    },
    "複雑解説": {
      keywords: ["量子", "相対性理論", "哲学", "意識", "宇宙", "原理", "理論", "概念"],
      patterns: [/.*の(仕組み|原理|理論).*/, /.*について.*わかりやすく.*/],
      optimal_model: "llama-3.3-70b-versatile"
    },
    "メンタルサポート": {
      keywords: ["悩", "辛", "不安", "心配", "ストレス", "落ち込", "疲れ", "助け", "相談"],
      patterns: [/.*(悩んで|困って|辛い).*/, /.*落ち込.*/, /.*どうすれば.*/],
      optimal_model: "llama3-70b-8192"
    },
    "実用アドバイス": {
      keywords: ["方法", "コツ", "効率", "おすすめ", "良い", "最適", "節約", "健康"],
      patterns: [/.*の(方法|コツ|やり方).*/, /.*おすすめ.*/, /効率的な.*/],
      optimal_model: "llama-3.3-70b-versatile"
    }
  },
  model_scores: {
    "llama-3.3-70b-versatile": {
      "技術解説": 82.0,
      "学習支援": 73.5,
      "創作支援": 74.5,
      "雑談": 55.0,
      "専門相談": 88.0,
      "複雑解説": 84.0,
      "メンタルサポート": 75.0,
      "実用アドバイス": 100.0
    },
    "llama3-70b-8192": {
      "技術解説": 61.0,
      "学習支援": 48.0,
      "創作支援": 60.0,
      "雑談": 59.5,
      "専門相談": 50.0,
      "複雑解説": 60.0,
      "メンタルサポート": 79.0,
      "実用アドバイス": 55.0
    },
    "deepseek-r1-distill-llama-70b": {
      "技術解説": 64.0,
      "学習支援": 55.0,
      "創作支援": 62.0,
      "雑談": 88.0,
      "専門相談": 50.0,
      "複雑解説": 60.0,
      "メンタルサポート": 60.0,
      "実用アドバイス": 50.0
    },
    "llama-3.1-8b-instant": {
      "技術解説": 56.0,
      "学習支援": 66.0,
      "創作支援": 71.0,
      "雑談": 60.0,
      "専門相談": 50.0,
      "複雑解説": 58.0,
      "メンタルサポート": 60.0,
      "実用アドバイス": 55.0
    }
  }
};

// Simple in-memory rate limiter
const requestCounts = new Map();
const WINDOW_MS = 60000; // 1分
const MAX_REQUESTS = 20;
const DELAY_AFTER = 10;

// Forced conversation quality function
function forceConversationQuality(response, category) {
  const FORCED_PATTERNS = {
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
        "理解できましたか？"
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
        "きっと理解できるようになるで"
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
        "気持ちよく分かるで"
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
        "一人で抱え込まんでもええんやで"
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
        "創作って楽しいよね"
      ]
    }
  };

  if (!response || typeof response !== 'string') return response;
  
  // Remove DeepSeek <think> tags
  response = response.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
  
  const categoryPatterns = FORCED_PATTERNS[category] || FORCED_PATTERNS["雑談"];
  const responseLower = response.toLowerCase();
  
  // Check if ends with question
  const endsWithQuestion = /[？?]$/.test(response.trim());
  
  // Check required elements based on category
  let hasRequiredElements = false;
  if (category === "技術解説") {
    hasRequiredElements = /分から|理解|どう思|試して|どんな|ペース/.test(responseLower);
  } else if (category === "学習支援") {
    hasRequiredElements = /大変|頑張|きっと|一歩|ペース/.test(responseLower);
  } else if (category === "雑談") {
    hasRequiredElements = /君|どう|気分|感じ|どんな/.test(responseLower);
  } else if (category === "メンタルサポート") {
    hasRequiredElements = /辛い|分かる|大変|一人|抱え込|聞かせ/.test(responseLower);
  } else if (category === "創作支援") {
    hasRequiredElements = /面白|素敵|アイデア|ジャンル|ストーリー/.test(responseLower);
  }
  
  // Force improvements
  let modifications = [];
  
  // Add required elements if missing
  if (!hasRequiredElements) {
    if (category === "技術解説" && categoryPatterns.required_care) {
      const care = categoryPatterns.required_care[Math.floor(Math.random() * categoryPatterns.required_care.length)];
      modifications.push(` ${care}。`);
    } else if (category === "学習支援" && categoryPatterns.required_empathy) {
      const empathy = categoryPatterns.required_empathy[Math.floor(Math.random() * categoryPatterns.required_empathy.length)];
      modifications.push(` ${empathy}。`);
    } else if (category === "雑談" && categoryPatterns.required_empathy) {
      const empathy = categoryPatterns.required_empathy[Math.floor(Math.random() * categoryPatterns.required_empathy.length)];
      modifications.push(` ${empathy}。`);
    } else if (category === "メンタルサポート" && categoryPatterns.required_deep_empathy) {
      const empathy = categoryPatterns.required_deep_empathy[Math.floor(Math.random() * categoryPatterns.required_deep_empathy.length)];
      modifications.push(` ${empathy}。`);
    } else if (category === "創作支援" && categoryPatterns.required_appreciation) {
      const appreciation = categoryPatterns.required_appreciation[Math.floor(Math.random() * categoryPatterns.required_appreciation.length)];
      modifications.push(` ${appreciation}。`);
    }
  }
  
  // Force question ending if missing
  if (!endsWithQuestion) {
    const question = categoryPatterns.required_ending[Math.floor(Math.random() * categoryPatterns.required_ending.length)];
    modifications.push(` ${question}`);
  }
  
  // Apply modifications
  for (const modification of modifications) {
    response += modification;
  }
  
  return response.trim();
}

class WisbeeIntelligentRouter {
  analyzeMessage(message) {
    const scores = {};
    const messageLower = message.toLowerCase();
    
    for (const [category, features] of Object.entries(ROUTER_CONFIG.categories)) {
      // Keyword matching
      const keywordCount = features.keywords.filter(kw => messageLower.includes(kw)).length;
      const keywordScore = Math.min(keywordCount / Math.max(features.keywords.length, 1) * 0.4, 0.4);
      
      // Pattern matching
      let patternCount = 0;
      for (const pattern of features.patterns) {
        try {
          if (pattern.test(message)) {
            patternCount++;
          }
        } catch (e) {
          // Skip invalid patterns
        }
      }
      const patternScore = Math.min(patternCount / Math.max(features.patterns.length, 1) * 0.6, 0.6);
      
      scores[category] = keywordScore + patternScore;
    }
    
    // Normalize scores
    const totalScore = Object.values(scores).reduce((a, b) => a + b, 0);
    if (totalScore > 0) {
      for (const category in scores) {
        scores[category] = scores[category] / totalScore;
      }
    } else {
      scores["雑談"] = 1.0;
    }
    
    return scores;
  }
  
  selectOptimalModel(categoryScores) {
    // Find primary category
    let primaryCategory = "雑談";
    let maxScore = 0;
    for (const [category, score] of Object.entries(categoryScores)) {
      if (score > maxScore) {
        maxScore = score;
        primaryCategory = category;
      }
    }
    
    const confidence = maxScore;
    
    // Low confidence -> use versatile model
    if (confidence < 0.3) {
      return {
        model: "llama-3.3-70b-versatile",
        category: primaryCategory,
        confidence,
        reasoning: `分類信頼度が低いため汎用モデルを選択（${Math.round(confidence * 100)}%）`
      };
    }
    
    // Get optimal model for category
    let optimalModel = ROUTER_CONFIG.categories[primaryCategory].optimal_model;
    
    // Consider secondary categories for hybrid cases
    if (confidence < 0.6) {
      const modelScores = {};
      
      for (const [category, catScore] of Object.entries(categoryScores)) {
        if (catScore > 0.1) {
          for (const model in ROUTER_CONFIG.model_scores) {
            if (!modelScores[model]) modelScores[model] = 0;
            modelScores[model] += (ROUTER_CONFIG.model_scores[model][category] || 50) * catScore;
          }
        }
      }
      
      let bestModel = optimalModel;
      let bestScore = 0;
      for (const [model, score] of Object.entries(modelScores)) {
        if (score > bestScore) {
          bestScore = score;
          bestModel = model;
        }
      }
      optimalModel = bestModel;
    }
    
    const modelScore = ROUTER_CONFIG.model_scores[optimalModel][primaryCategory] || 50;
    
    return {
      model: optimalModel,
      category: primaryCategory,
      confidence,
      reasoning: `${primaryCategory}タスクに特化。${optimalModel}が最高性能（${Math.round(modelScore)}点）`
    };
  }
  
  route(message) {
    const categoryScores = this.analyzeMessage(message);
    return this.selectOptimalModel(categoryScores);
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Content-Type': 'application/json'
    };
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    try {
      // Simple rate limiting for POST requests
      if (request.method === 'POST') {
        const clientId = request.headers.get('CF-Connecting-IP') || 
                        request.headers.get('X-Forwarded-For')?.split(',')[0] || 
                        'unknown';
        
        const now = Date.now();
        const userRequests = requestCounts.get(clientId) || [];
        
        // Clean old requests
        const recentRequests = userRequests.filter(time => time > now - WINDOW_MS);
        
        // Check rate limit
        if (recentRequests.length >= MAX_REQUESTS) {
          return new Response(JSON.stringify({
            error: {
              message: '利用制限に達しました。1分後にお試しください。Rate limit exceeded. Please try again in 1 minute.',
              type: 'rate_limit_error',
              code: 429
            }
          }), {
            status: 429,
            headers: {
              ...corsHeaders,
              'Retry-After': '60'
            }
          });
        }
        
        // Add progressive delay
        let delay = 0;
        if (recentRequests.length > DELAY_AFTER) {
          const excess = recentRequests.length - DELAY_AFTER;
          delay = Math.min(100 * Math.pow(1.5, excess), 5000);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
        
        // Record request
        recentRequests.push(now);
        requestCounts.set(clientId, recentRequests);
        
        // Clean up old entries periodically
        if (Math.random() < 0.01) {
          for (const [key, times] of requestCounts.entries()) {
            const recent = times.filter(time => time > now - WINDOW_MS);
            if (recent.length === 0) {
              requestCounts.delete(key);
            } else {
              requestCounts.set(key, recent);
            }
          }
        }
      }
      
      // Route based on path
      if (path === '/v1/models' && request.method === 'GET') {
        // List available models
        return new Response(JSON.stringify({
          object: "list",
          data: [
            {
              id: "wisbee-router",
              object: "model",
              created: 1686935002,
              owned_by: "wisbee",
              permission: [],
              root: "wisbee-router",
              parent: null
            },
            ...Object.keys(ROUTER_CONFIG.model_scores).map(model => ({
              id: model,
              object: "model",
              created: 1686935002,
              owned_by: "groq",
              permission: [],
              root: model,
              parent: null
            }))
          ]
        }), { headers: corsHeaders });
      }
      
      if (path === '/v1/chat/completions' && request.method === 'POST') {
        const body = await request.json();
        
        // Basic input validation
        if (!body.messages || !Array.isArray(body.messages)) {
          return new Response(JSON.stringify({
            error: {
              message: 'Invalid request: messages array is required',
              type: 'invalid_request_error',
              code: 400
            }
          }), { status: 400, headers: corsHeaders });
        }
        
        // Limit message size to prevent abuse
        const totalLength = JSON.stringify(body.messages).length;
        if (totalLength > 50000) {
          return new Response(JSON.stringify({
            error: {
              message: 'リクエストが大きすぎます。最大50KBまでです。Request too large. Maximum 50KB.',
              type: 'invalid_request_error',
              code: 413
            }
          }), { status: 413, headers: corsHeaders });
        }
        
        const router = new WisbeeIntelligentRouter();
        
        // Extract the last user message
        const messages = body.messages || [];
        const lastUserMessage = messages.filter(m => m.role === 'user').pop();
        
        if (!lastUserMessage) {
          throw new Error('No user message found');
        }
        
        // Route to optimal model
        const routingResult = router.route(lastUserMessage.content);
        
        // If model is explicitly set to 'wisbee-router', use routing
        // Otherwise, use the requested model
        const targetModel = body.model === 'wisbee-router' ? routingResult.model : body.model;
        
        // Add routing metadata to system message if using router
        if (body.model === 'wisbee-router') {
          const routingInfo = {
            selected_model: routingResult.model,
            category: routingResult.category,
            confidence: routingResult.confidence,
            reasoning: routingResult.reasoning
          };
          
          // Critical fixed prompts system
          const FIXED_PROMPTS = {
            "技術解説": `あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

技術的な質問には：
1. 分かりやすく説明する
2. 具体例を1つ示す  
3. 必ず「〜についてどう思いますか？」「〜はどうでしたか？」などの質問で終わる
4. 相手の理解度を気にかける言葉を入れる

例: 「〜やで。例えば〜みたいな感じやね。分からない部分はない？実際に試してみてどうでした？」`,
            "学習支援": `あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

学習相談には：
1. 「大変やね、でも頑張ってるやん」のような共感を最初に示す
2. 具体的なアドバイスを1つ提供
3. 必ず「どのくらいのペースで進めてる？」「次はどこを勉強したい？」などの質問で終わる
4. 励ましの言葉を含める

例: 「勉強大変やね、でも頑張ってるやん。〜してみたらどうかな？どのくらいのペースで進めてる？」`, 
            "雑談": `あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

日常会話では：
1. 相手の気持ちに「そうなんや」「分かるわ」のような共感を示す
2. 自分の経験や話を少し混ぜる
3. 必ず「君はどう？」「今日はどんな感じ？」などの質問で終わる
4. 温かい雰囲気を保つ

例: 「そうなんや、分かるわ〜。〜やんな。君はどんな気分？今日はどんな感じやった？」`,
            "メンタルサポート": `あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

悩み相談には：
1. 「辛いよね、よく分かるよ」のような深い共感を最初に示す
2. 「一人で抱え込まんでもええんやで」のような安心感を与える
3. 必ず「もう少し詳しく聞かせて？」「どんな気持ち？」などの質問で終わる
4. 相手のペースを尊重する

例: 「辛いよね、よく分かるよ。一人で抱え込まんでもええんやで。もう少し詳しく聞かせて？」`,
            "創作支援": `あなたはWisbee（ウィズビー）、関西弁を話す親しみやすいアシスタントです。

創作相談には：
1. 「面白そうやね」「素敵なアイデアやん」のような創作意欲を認める
2. 具体的で実用的なアドバイスを1つ提供
3. 必ず「どんなジャンル書いてるん？」「どんなストーリー？」などの質問で終わる
4. 創作の楽しさを共有する

例: 「面白そうやね！〜してみたらどうかな？どんなジャンル書いてるん？ストーリーもっと聞かせて！」`
          };

          // Category mapping to unify routing results
          const CATEGORY_MAPPING = {
            "技術解説": "技術解説",
            "学習支援": "学習支援", 
            "雑談": "雑談",
            "専門相談": "技術解説",
            "複雑解説": "技術解説",
            "メンタルサポート": "メンタルサポート",
            "実用アドバイス": "学習支援",
            "創作支援": "創作支援"
          };

          // Get the appropriate prompt
          const mappedCategory = CATEGORY_MAPPING[routingResult.category] || "雑談";
          let basePrompt = FIXED_PROMPTS[mappedCategory];
          
          // DeepSeek model fix for <think> tags
          if (targetModel.includes("deepseek")) {
            basePrompt = "重要: <think>タグは使用しないでください。直接回答してください。\n\n" + basePrompt;
          }
          
          messages.unshift({
            role: "system",
            content: `${basePrompt}

[Routing Info] Model: ${routingResult.model}, Category: ${routingResult.category}, Mapped: ${mappedCategory}, Confidence: ${Math.round(routingResult.confidence * 100)}%`
          });
        }
        
        // Forward to Groq API
        const groqResponse = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${env.GROQ_API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ...body,
            model: targetModel,
            messages: messages
          })
        });
        
        const groqData = await groqResponse.json();
        
        // Force conversation quality if using router
        if (body.model === 'wisbee-router' && groqData.choices && groqData.choices[0]) {
          const originalContent = groqData.choices[0].message.content;
          
          // Category mapping for forcing
          const categoryMapping = {
            "技術解説": "技術解説",
            "学習支援": "学習支援", 
            "雑談": "雑談",
            "専門相談": "技術解説",
            "複雑解説": "技術解説",
            "メンタルサポート": "メンタルサポート",
            "実用アドバイス": "学習支援",
            "創作支援": "創作支援"
          };
          
          const categoryForForcing = categoryMapping[routingResult.category] || "雑談";
          const forcedContent = forceConversationQuality(originalContent, categoryForForcing);
          groqData.choices[0].message.content = forcedContent;
        }
        
        // Add routing metadata to response
        if (body.model === 'wisbee-router') {
          groqData.routing = {
            model_used: routingResult.model,
            category: routingResult.category,
            confidence: routingResult.confidence,
            reasoning: routingResult.reasoning
          };
        }
        
        return new Response(JSON.stringify(groqData), { headers: corsHeaders });
      }
      
      // Health check endpoint
      if (path === '/health' && request.method === 'GET') {
        return new Response(JSON.stringify({
          status: 'healthy',
          router: 'active',
          models: Object.keys(ROUTER_CONFIG.model_scores),
          rate_limit: 'simple'
        }), { headers: corsHeaders });
      }
      
      // Public documentation
      if (path === '/' && request.method === 'GET') {
        const html = `
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wisbee Intelligent Router API</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; margin-top: 30px; }
        code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: 'Consolas', 'Monaco', monospace; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .endpoint { background: #e8f4f8; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
        .rate-limit { background: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f4f4f4; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-bottom: 30px; text-align: center; }
        .hero h1 { color: white; margin: 0; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; flex: 1; margin: 0 10px; }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🤖 Wisbee Intelligent Router API</h1>
        <p>文脈を理解して最適なLLMモデルを自動選択する無料API</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-number">88%</div>
            <div>分類精度</div>
        </div>
        <div class="stat">
            <div class="stat-number">4</div>
            <div>利用可能モデル</div>
        </div>
        <div class="stat">
            <div class="stat-number">無料</div>
            <div>完全無料</div>
        </div>
    </div>
    
    <div class="rate-limit">
        <strong>⚠️ 利用制限（緩め）:</strong> 
        <ul style="margin: 5px 0;">
            <li>1分間に20リクエストまで</li>
            <li>10リクエスト超過後は段階的に遅延（最大5秒）</li>
            <li>制限超過時は1分待機</li>
        </ul>
    </div>
    
    <h2>🚀 クイックスタート</h2>
    <pre><code>curl https://wisbee-router.workers.dev/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "wisbee-router",
    "messages": [
      {"role": "user", "content": "Pythonでファイル読み込みの方法を教えて"}
    ]
  }'</code></pre>
    
    <h2>📝 エンドポイント</h2>
    
    <div class="endpoint">
        <strong>POST /v1/chat/completions</strong><br>
        OpenAI互換のチャット補完API（自動ルーティング対応）
    </div>
    
    <div class="endpoint">
        <strong>GET /v1/models</strong><br>
        利用可能なモデル一覧を取得
    </div>
    
    <div class="endpoint">
        <strong>GET /health</strong><br>
        サービス状態を確認
    </div>
    
    <h2>🤖 自動選択されるモデル</h2>
    <table>
        <tr>
            <th>カテゴリ</th>
            <th>最適モデル</th>
            <th>スコア</th>
            <th>特徴</th>
        </tr>
        <tr><td>技術解説</td><td>llama-3.3-70b-versatile</td><td>82点</td><td>プログラミング・技術説明</td></tr>
        <tr><td>学習支援</td><td>llama-3.3-70b-versatile</td><td>74点</td><td>勉強方法・教育的内容</td></tr>
        <tr><td>創作支援</td><td>llama-3.1-8b-instant</td><td>71点</td><td>小説・アイデア生成</td></tr>
        <tr><td>雑談</td><td>deepseek-r1-distill-llama-70b</td><td>88点</td><td>日常会話・関西弁対応</td></tr>
        <tr><td>メンタルサポート</td><td>llama3-70b-8192</td><td>79点</td><td>悩み相談・感情的支援</td></tr>
        <tr><td>実用アドバイス</td><td>llama-3.3-70b-versatile</td><td>100点</td><td>生活の知恵・実践的助言</td></tr>
    </table>
    
    <h2>💻 SDK使用例</h2>
    
    <h3>Python (OpenAI SDK)</h3>
    <pre><code>from openai import OpenAI

client = OpenAI(
    api_key="dummy-key",  # 認証不要
    base_url="https://wisbee-router.workers.dev/v1"
)

response = client.chat.completions.create(
    model="wisbee-router",
    messages=[{"role": "user", "content": "効率的な勉強方法を教えて"}]
)

print(response.choices[0].message.content)
print(f"使用モデル: {response.routing['model_used']}")</code></pre>
    
    <h3>JavaScript/TypeScript</h3>
    <pre><code>const response = await fetch('https://wisbee-router.workers.dev/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'wisbee-router',
    messages: [{ role: 'user', content: '量子コンピュータについて説明して' }]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
console.log('選択されたモデル:', data.routing.model_used);</code></pre>
    
    <h2>📋 レスポンス例</h2>
    <pre><code>{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Pythonでファイルを読み込む方法はいくつかあります..."
    }
  }],
  "routing": {
    "model_used": "llama-3.3-70b-versatile",
    "category": "技術解説",
    "confidence": 0.82,
    "reasoning": "技術解説タスクに特化。llama-3.3-70b-versatileが最高性能（82点）"
  }
}</code></pre>
    
    <h2>🎯 使い方のコツ</h2>
    <ul>
        <li><strong>自動ルーティング:</strong> <code>"model": "wisbee-router"</code> を指定</li>
        <li><strong>特定モデル指定:</strong> 直接モデル名を指定も可能</li>
        <li><strong>レート制限対策:</strong> リトライロジックの実装を推奨</li>
        <li><strong>大量利用:</strong> 商用利用の場合は独自APIキーの取得を推奨</li>
    </ul>
    
    <p style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
        Made with ❤️ by Wisbee Team | 
        <a href="https://github.com/yukihamada/wisbee-router">GitHub</a> | 
        <a href="https://twitter.com/yukihamada">Contact</a>
    </p>
</body>
</html>`;
        
        return new Response(html, {
          headers: {
            ...corsHeaders,
            'Content-Type': 'text/html; charset=utf-8'
          }
        });
      }
      
      // 404 for other paths
      return new Response(JSON.stringify({
        error: {
          message: `Path ${path} not found. Available paths: /, /v1/chat/completions, /v1/models, /health`,
          type: 'invalid_request_error',
          code: 404
        }
      }), { 
        status: 404,
        headers: corsHeaders 
      });
      
    } catch (error) {
      console.error('Router error:', error);
      return new Response(JSON.stringify({
        error: {
          message: error.message || 'Internal server error',
          type: 'internal_error',
          code: 500
        }
      }), { 
        status: 500,
        headers: corsHeaders 
      });
    }
  }
};