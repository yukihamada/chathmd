/**
 * Wisbee Intelligent Router API - Protected Version
 * CloudWorker function with OpenAI-compatible endpoints and abuse protection
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

// Rate limiting configuration
const RATE_LIMIT_CONFIG = {
  // 基本設定
  windowMs: 60 * 1000, // 1分間のウィンドウ
  baseLimit: 20, // 基本リクエスト数/分
  burstLimit: 30, // バースト時の最大リクエスト数
  
  // プログレッシブ遅延
  delayAfter: 10, // この数を超えたら遅延開始
  delayMs: 100, // 初期遅延（ミリ秒）
  maxDelayMs: 5000, // 最大遅延（5秒）
  
  // IPベースの制限
  skipSuccessfulRequests: false,
  keyGenerator: (request) => {
    // CloudflareのCF-Connecting-IP or X-Forwarded-For
    return request.headers.get('CF-Connecting-IP') || 
           request.headers.get('X-Forwarded-For')?.split(',')[0] || 
           'unknown';
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

// Rate limiter using KV store
class RateLimiter {
  constructor(kv) {
    this.kv = kv;
  }
  
  async checkRateLimit(clientId) {
    const now = Date.now();
    const windowStart = now - RATE_LIMIT_CONFIG.windowMs;
    const key = `rate:${clientId}`;
    
    // Get current usage
    const usage = await this.kv.get(key, 'json') || { requests: [], blocked: false };
    
    // Filter out old requests
    usage.requests = usage.requests.filter(timestamp => timestamp > windowStart);
    
    // Check if currently blocked
    if (usage.blocked && usage.blockedUntil > now) {
      const waitTime = Math.ceil((usage.blockedUntil - now) / 1000);
      return {
        allowed: false,
        retryAfter: waitTime,
        reason: `Too many requests. Please wait ${waitTime} seconds.`
      };
    }
    
    // Check burst limit
    if (usage.requests.length >= RATE_LIMIT_CONFIG.burstLimit) {
      usage.blocked = true;
      usage.blockedUntil = now + 60000; // Block for 1 minute
      await this.kv.put(key, JSON.stringify(usage), { expirationTtl: 120 });
      
      return {
        allowed: false,
        retryAfter: 60,
        reason: 'Burst limit exceeded. Please wait 1 minute.'
      };
    }
    
    // Calculate progressive delay
    let delay = 0;
    if (usage.requests.length > RATE_LIMIT_CONFIG.delayAfter) {
      const excess = usage.requests.length - RATE_LIMIT_CONFIG.delayAfter;
      delay = Math.min(
        RATE_LIMIT_CONFIG.delayMs * Math.pow(1.5, excess),
        RATE_LIMIT_CONFIG.maxDelayMs
      );
    }
    
    // Add current request
    usage.requests.push(now);
    await this.kv.put(key, JSON.stringify(usage), { expirationTtl: 120 });
    
    return {
      allowed: true,
      delay: delay,
      remaining: RATE_LIMIT_CONFIG.baseLimit - usage.requests.length,
      reset: new Date(windowStart + RATE_LIMIT_CONFIG.windowMs).toISOString()
    };
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
      // Initialize rate limiter if KV is available
      const rateLimiter = env.RATE_LIMIT_KV ? new RateLimiter(env.RATE_LIMIT_KV) : null;
      
      // Check rate limit for non-GET requests
      if (request.method !== 'GET' && rateLimiter) {
        const clientId = RATE_LIMIT_CONFIG.keyGenerator(request);
        const rateCheck = await rateLimiter.checkRateLimit(clientId);
        
        if (!rateCheck.allowed) {
          return new Response(JSON.stringify({
            error: {
              message: rateCheck.reason,
              type: 'rate_limit_error',
              code: 429
            }
          }), {
            status: 429,
            headers: {
              ...corsHeaders,
              'Retry-After': String(rateCheck.retryAfter),
              'X-RateLimit-Limit': String(RATE_LIMIT_CONFIG.baseLimit),
              'X-RateLimit-Remaining': '0',
              'X-RateLimit-Reset': new Date(Date.now() + rateCheck.retryAfter * 1000).toISOString()
            }
          });
        }
        
        // Apply progressive delay
        if (rateCheck.delay > 0) {
          await new Promise(resolve => setTimeout(resolve, rateCheck.delay));
        }
        
        // Add rate limit headers
        corsHeaders['X-RateLimit-Limit'] = String(RATE_LIMIT_CONFIG.baseLimit);
        corsHeaders['X-RateLimit-Remaining'] = String(rateCheck.remaining);
        corsHeaders['X-RateLimit-Reset'] = rateCheck.reset;
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
              message: 'Request too large. Maximum total message size is 50KB',
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
          models: Object.keys(ROUTER_CONFIG.model_scores),
          rate_limit: rateLimiter ? 'enabled' : 'disabled'
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
    </style>
</head>
<body>
    <h1>🤖 Wisbee Intelligent Router API</h1>
    <p>文脈を理解して最適なLLMモデルを自動選択するOpenAI互換APIです。</p>
    
    <div class="rate-limit">
        <strong>⚠️ レート制限:</strong> 1分間に20リクエスト（バースト時最大30）。超過すると段階的に遅延が発生します。
    </div>
    
    <h2>エンドポイント</h2>
    
    <div class="endpoint">
        <strong>POST /v1/chat/completions</strong><br>
        OpenAI互換のチャット補完API
    </div>
    
    <div class="endpoint">
        <strong>GET /v1/models</strong><br>
        利用可能なモデル一覧
    </div>
    
    <div class="endpoint">
        <strong>GET /health</strong><br>
        サービス状態確認
    </div>
    
    <h2>使用例</h2>
    <pre><code>curl https://router.wisbee.ai/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "wisbee-router",
    "messages": [
      {"role": "user", "content": "Pythonでファイル読み込みの方法を教えて"}
    ]
  }'</code></pre>
    
    <h2>モデル選択ロジック</h2>
    <table>
        <tr>
            <th>カテゴリ</th>
            <th>最適モデル</th>
            <th>スコア</th>
        </tr>
        <tr><td>技術解説</td><td>llama-3.3-70b-versatile</td><td>82点</td></tr>
        <tr><td>学習支援</td><td>llama-3.3-70b-versatile</td><td>74点</td></tr>
        <tr><td>創作支援</td><td>llama-3.1-8b-instant</td><td>71点</td></tr>
        <tr><td>雑談</td><td>deepseek-r1-distill-llama-70b</td><td>88点</td></tr>
        <tr><td>メンタルサポート</td><td>llama3-70b-8192</td><td>79点</td></tr>
        <tr><td>実用アドバイス</td><td>llama-3.3-70b-versatile</td><td>100点</td></tr>
    </table>
    
    <h2>Python SDK使用例</h2>
    <pre><code>from openai import OpenAI

client = OpenAI(
    api_key="dummy",  # 認証不要
    base_url="https://router.wisbee.ai/v1"
)

response = client.chat.completions.create(
    model="wisbee-router",
    messages=[{"role": "user", "content": "こんにちは！"}]
)

print(response.choices[0].message.content)</code></pre>
    
    <p style="margin-top: 40px; color: #666;">
        Made with ❤️ by Wisbee Team | 
        <a href="https://github.com/yukihamada/wisbee-router">GitHub</a>
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
};