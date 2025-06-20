/**
 * Wisbee Intelligent Router API
 * CloudWorker function with OpenAI-compatible endpoints
 */

// Router configuration matching the Python implementation
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

// Main handler
export async function onRequest(context) {
  const { request, env } = context;
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
        
        // Add routing info as a system message
        messages.unshift({
          role: "system",
          content: `[Routing Info] Model: ${routingResult.model}, Category: ${routingResult.category}, Confidence: ${Math.round(routingResult.confidence * 100)}%`
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
        models: Object.keys(ROUTER_CONFIG.model_scores)
      }), { headers: corsHeaders });
    }
    
    // 404 for other paths
    return new Response(JSON.stringify({
      error: {
        message: `Path ${path} not found`,
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