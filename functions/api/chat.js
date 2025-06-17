// Cloudflare Worker Function for chatHMD API
// Handles chat requests and routes to RunPod or local processing

export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    const body = await request.json();
    const { message, model = 'auto', temperature = 0.8 } = body;
    
    if (!message || message.trim() === '') {
      return new Response(JSON.stringify({ 
        error: 'Message is required' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Choose AI provider based on model preference
    let response;
    if (model === 'local' || model === 'demo') {
      response = await getLocalResponse(message);
    } else {
      // Use RunPod for cloud inference
      response = await getRunPodResponse(message, temperature, env);
    }
    
    return new Response(JSON.stringify({
      response: response,
      model: model,
      timestamp: new Date().toISOString()
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      }
    });
    
  } catch (error) {
    console.error('Chat API Error:', error);
    
    return new Response(JSON.stringify({ 
      error: 'Internal server error',
      fallback: 'I apologize, but I encountered an error processing your request. Please try the desktop app for the best experience.'
    }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}

// Handle CORS preflight
export async function onRequestOptions() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}

async function getRunPodResponse(message, temperature, env) {
  const RUNPOD_API_KEY = env.RUNPOD_API_KEY;
  const RUNPOD_ENDPOINT = env.RUNPOD_ENDPOINT;
  
  if (!RUNPOD_API_KEY) {
    throw new Error('RunPod API key not configured');
  }
  
  if (!RUNPOD_ENDPOINT) {
    throw new Error('RunPod endpoint not configured');
  }
  
  // Auto-scale: Try multiple attempts with backoff
  const maxRetries = 3;
  const baseDelay = 1000; // 1 second
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // Check endpoint health first
      await ensureEndpointRunning(RUNPOD_ENDPOINT, RUNPOD_API_KEY);
      
      const runpodUrl = `https://api.runpod.ai/v2/${RUNPOD_ENDPOINT}/runsync`;
      
      const payload = {
        input: {
          prompt: formatPromptForModel(message),
          max_tokens: 500,
          temperature: temperature,
          top_p: 0.95,
          frequency_penalty: 0.1,
          presence_penalty: 0.1
        }
      };
      
      console.log(`🚀 RunPod attempt ${attempt}/${maxRetries}`);
      
      const response = await fetch(runpodUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${RUNPOD_API_KEY}`
        },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(45000) // 45 second timeout for GPU processing
      });
      
      if (!response.ok) {
        if (response.status === 503 || response.status === 502) {
          // Service unavailable - endpoint might be scaling
          console.log(`⏳ RunPod scaling (${response.status}), retrying...`);
          if (attempt < maxRetries) {
            await sleep(baseDelay * Math.pow(2, attempt - 1)); // Exponential backoff
            continue;
          }
        }
        throw new Error(`RunPod API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'COMPLETED' && data.output) {
        console.log(`✅ RunPod response received on attempt ${attempt}`);
        return data.output.text || data.output.response || data.output;
      } else if (data.status === 'FAILED') {
        console.error('RunPod inference failed:', data.error);
        throw new Error(`RunPod inference failed: ${data.error || 'Unknown error'}`);
      } else if (data.status === 'IN_PROGRESS' || data.status === 'IN_QUEUE') {
        // For async endpoints, we might get this status
        console.log(`⏳ RunPod processing... Status: ${data.status}`);
        if (attempt < maxRetries) {
          await sleep(2000); // Wait 2 seconds for processing
          continue;
        }
        throw new Error('RunPod processing timeout');
      } else {
        console.error('Unexpected RunPod response:', data);
        throw new Error(`Unexpected RunPod response: ${data.status}`);
      }
      
    } catch (error) {
      console.error(`❌ RunPod attempt ${attempt} failed:`, error.message);
      
      if (attempt === maxRetries) {
        throw new Error(`RunPod failed after ${maxRetries} attempts: ${error.message}`);
      }
      
      // Wait before retry
      await sleep(baseDelay * attempt);
    }
  }
}

async function ensureEndpointRunning(endpointId, apiKey) {
  try {
    const statusUrl = `https://api.runpod.ai/v2/${endpointId}/status`;
    const response = await fetch(statusUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`
      },
      signal: AbortSignal.timeout(10000)
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log(`📊 RunPod status: ${data.status}`);
      
      if (data.status === 'STOPPED' || data.status === 'TERMINATED') {
        console.log('🔄 RunPod endpoint stopped, attempting to start...');
        // Could implement auto-restart here if needed
        throw new Error('RunPod endpoint is stopped');
      }
      
      return data.status === 'RUNNING' || data.status === 'IDLE';
    }
  } catch (error) {
    console.warn('⚠️ Could not check RunPod status:', error.message);
    // Continue anyway - status check is optional
  }
  
  return true; // Assume it's running if we can't check
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getLocalResponse(message) {
  // Demo responses for when RunPod is not available
  const demoResponses = [
    "This is a demo response! For real AI conversations with RunPod GPU inference, please contact support to enable cloud processing.",
    "I'm running in demo mode. The full version uses RunPod GPUs for fast, high-quality AI responses.",
    "Demo mode: Real conversations use powerful cloud GPUs via RunPod for the best AI experience.",
    "That's an interesting question! The cloud-powered version would give you a much more detailed answer.",
    "Demo response: The full app features GPU-accelerated inference with no data retention!",
  ];
  
  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
  
  return demoResponses[Math.floor(Math.random() * demoResponses.length)];
}

function formatPromptForModel(message) {
  return `You are chatHMD, a privacy-first AI assistant powered by the jan-nano XS model. You help users while respecting their privacy completely.

Key principles:
- Privacy first: Never store or remember personal information between conversations
- Helpful: Provide accurate, useful, and concise responses
- Respectful: Always maintain a friendly and professional tone
- Local-focused: Encourage users to try the desktop app for full privacy and advanced learning features

Current conversation:
User: ${message}
Assistant:`;
}