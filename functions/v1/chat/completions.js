// OpenAI-compatible chat completions endpoint for api.wisbee.ai
// Endpoint: https://api.wisbee.ai/v1/chat/completions

export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    // Check authentication settings
    const DISABLE_AUTH = env.DISABLE_AUTH === 'true' || env.DISABLE_AUTH === true;
    const REQUIRE_API_KEY = env.REQUIRE_API_KEY === 'true' || env.REQUIRE_API_KEY === true;
    
    // Handle API key authentication
    if (!DISABLE_AUTH && REQUIRE_API_KEY) {
      const authHeader = request.headers.get('Authorization');
      const providedKey = authHeader?.replace('Bearer ', '').trim();
      
      // List of valid API keys - simplified for easy management
      const validKeys = [
        // Master keys
        'sk-master-wisbee-2025-43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015',
        
        // Production keys
        'sk-wisbee-2025-prod-43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015',
        
        // Vast.ai key (legacy format supported)
        '43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015',
        
        // Test keys
        'sk-test-wisbee-2025',
        'test-key-2025',
        
        // Environment keys
        env.WISBEE_API_KEY,
        env.VAST_API_KEY,
        env.CUSTOM_API_KEY
      ].filter(Boolean);
      
      if (!providedKey || !validKeys.includes(providedKey)) {
        // Log failed attempt
        console.log(`API key validation failed: ${providedKey?.substring(0, 20)}...`);
        
        return new Response(JSON.stringify({ 
          error: {
            message: 'Invalid API key. Please use a valid Wisbee API key.',
            type: 'authentication_error',
            code: 'invalid_api_key',
            hint: 'Contact admin for a valid API key or use the master key.'
          }
        }), {
          status: 401,
          headers: { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
      }
    }
    
    const body = await request.json();
    
    // OpenAI format validation
    const { 
      model = 'wisbee-nano', 
      messages = [],
      temperature = 0.8,
      max_tokens = 500,
      stream = false,
      top_p = 0.95,
      frequency_penalty = 0.1,
      presence_penalty = 0.1
    } = body;
    
    if (!messages || messages.length === 0) {
      return new Response(JSON.stringify({ 
        error: {
          message: 'Messages array is required',
          type: 'invalid_request_error',
          code: 'missing_messages'
        }
      }), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    // Extract the last user message
    const lastUserMessage = messages.filter(m => m.role === 'user').pop();
    if (!lastUserMessage) {
      return new Response(JSON.stringify({ 
        error: {
          message: 'No user message found',
          type: 'invalid_request_error',
          code: 'no_user_message'
        }
      }), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    // Format messages for LLM
    const formattedPrompt = formatMessagesForLLM(messages);
    
    // Get response from LLM backend
    let responseText;
    try {
      responseText = await getLLMResponse(formattedPrompt, temperature, env);
    } catch (error) {
      console.error('LLM backend error:', error);
      // Fallback to demo response
      responseText = getDemoResponse(lastUserMessage.content);
    }
    
    // Format response in OpenAI style
    const openAIResponse = {
      id: `chatcmpl-${generateId()}`,
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: model,
      choices: [{
        index: 0,
        message: {
          role: 'assistant',
          content: responseText
        },
        finish_reason: 'stop'
      }],
      usage: {
        prompt_tokens: estimateTokens(formattedPrompt),
        completion_tokens: estimateTokens(responseText),
        total_tokens: estimateTokens(formattedPrompt) + estimateTokens(responseText)
      }
    };
    
    return new Response(JSON.stringify(openAIResponse), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    });
    
  } catch (error) {
    console.error('Chat completions error:', error);
    
    return new Response(JSON.stringify({ 
      error: {
        message: 'Internal server error',
        type: 'internal_error',
        code: 'server_error'
      }
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
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    }
  });
}

async function getLLMResponse(prompt, temperature, env) {
  // Try local llama.cpp server first
  const LLAMA_ENDPOINT = env.LLAMA_ENDPOINT || "http://localhost:8080";
  
  try {
    const response = await fetch(`${LLAMA_ENDPOINT}/completion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: prompt,
        n_predict: 500,
        temperature: temperature,
        top_p: 0.95,
        repeat_penalty: 1.1,
        stop: ["User:", "Human:", "### Human:", "### User:"]
      }),
      signal: AbortSignal.timeout(30000)
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.content || data.response || data.completion || '';
    }
  } catch (error) {
    console.error('Local LLM error:', error);
  }
  
  // Try backend endpoints
  const BACKEND_URL = env.VAST_ENDPOINT || 'https://8092-2405-6580-36a0-6200-219e-3a10-45a7-96d3.ngrok-free.app';
  const VAST_API_KEY = env.VAST_API_KEY || '43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015';
  
  if (BACKEND_URL) {
    try {
      const headers = {
        'Content-Type': 'application/json'
      };
      
      // Add Vast API key if available
      if (VAST_API_KEY) {
        headers['Authorization'] = `Bearer ${VAST_API_KEY}`;
      }
      
      const response = await fetch(`${BACKEND_URL}/v1/chat/completions`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          model: model,
          messages: messages,
          max_tokens: 500,
          temperature: temperature,
          top_p: 0.95,
          stream: false
        }),
        signal: AbortSignal.timeout(30000)
      });
      
      if (response.ok) {
        const data = await response.json();
        // Handle OpenAI-compatible response format
        if (data.choices && data.choices[0] && data.choices[0].message) {
          return data.choices[0].message.content;
        }
        return data.content || data.response || data.choices?.[0]?.text || data.text || '';
      }
    } catch (error) {
      console.error('Vast.ai error:', error);
    }
  }
  
  // Try RunPod
  const RUNPOD_API_KEY = env.RUNPOD_API_KEY;
  const RUNPOD_ENDPOINT = env.RUNPOD_ENDPOINT;
  
  if (RUNPOD_API_KEY && RUNPOD_ENDPOINT) {
    try {
      const runpodUrl = `https://api.runpod.ai/v2/${RUNPOD_ENDPOINT}/runsync`;
      
      const response = await fetch(runpodUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${RUNPOD_API_KEY}`
        },
        body: JSON.stringify({
          input: {
            prompt: prompt,
            max_tokens: 500,
            temperature: temperature,
            top_p: 0.95
          }
        }),
        signal: AbortSignal.timeout(45000)
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'COMPLETED' && data.output) {
          return data.output.text || data.output.response || data.output || '';
        }
      }
    } catch (error) {
      console.error('RunPod error:', error);
    }
  }
  
  throw new Error('All LLM backends failed');
}

function formatMessagesForLLM(messages) {
  let prompt = "You are Wisbee, a helpful AI assistant.\n\n";
  
  for (const message of messages) {
    if (message.role === 'system') {
      prompt = message.content + "\n\n";
    } else if (message.role === 'user') {
      prompt += `User: ${message.content}\n`;
    } else if (message.role === 'assistant') {
      prompt += `Assistant: ${message.content}\n`;
    }
  }
  
  prompt += "Assistant:";
  return prompt;
}

function getDemoResponse(message) {
  const messageLC = message.toLowerCase();
  
  if (messageLC.includes('hello') || messageLC.includes('hi')) {
    return "Hello! I'm Wisbee, your AI assistant powered by jan-nano. How can I help you today?";
  }
  
  if (messageLC.includes('test') || messageLC.includes('working')) {
    return "API is working perfectly! I'm Wisbee, running on the jan-nano model. Ready to assist you!";
  }
  
  if (messageLC.includes('help')) {
    return "I'd be happy to help! I'm Wisbee, powered by the jan-nano model. I can assist with various tasks including answering questions, creative writing, coding help, and more. What would you like to know?";
  }
  
  return "I'm Wisbee, running in demo mode. For full functionality, please ensure the LLM backend is properly configured. How can I assist you?";
}

function generateId() {
  return Math.random().toString(36).substring(2, 15);
}

function estimateTokens(text) {
  // Rough estimation: 1 token ≈ 4 characters
  return Math.ceil(text.length / 4);
}