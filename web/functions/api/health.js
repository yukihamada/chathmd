// Health check endpoint for chatHMD
// Returns availability status of different AI providers

export async function onRequestGet(context) {
  const { env } = context;
  
  try {
    // Check RunPod availability
    let runpodAvailable = false;
    let runpodStatus = 'Not configured';
    
    const RUNPOD_API_KEY = env.RUNPOD_API_KEY;
    const RUNPOD_ENDPOINT = env.RUNPOD_ENDPOINT;
    
    if (RUNPOD_API_KEY && RUNPOD_ENDPOINT) {
      try {
        const runpodUrl = `https://api.runpod.ai/v2/${RUNPOD_ENDPOINT}/status`;
        
        const response = await fetch(runpodUrl, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${RUNPOD_API_KEY}`
          },
          signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        
        if (response.ok) {
          const data = await response.json();
          runpodAvailable = data.status === 'RUNNING' || data.status === 'IDLE';
          runpodStatus = data.status || 'Unknown';
        } else {
          runpodStatus = `HTTP ${response.status}`;
        }
      } catch (error) {
        runpodStatus = `Error: ${error.message}`;
      }
    }
    
    return new Response(JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      models: {
        'jan-nano-xs': {
          available: true,
          description: 'Menlo Mini Jan nano model with Q4_K_XS quantization'
        }
      },
      providers: {
        local: {
          available: 'unknown', // Browser will detect this
          description: 'Local chatHMD desktop application'
        },
        runpod: {
          available: runpodAvailable,
          status: runpodStatus,
          description: 'GPU cloud inference via RunPod'
        },
        demo: {
          available: true,
          description: 'Demo mode with simulated responses'
        }
      },
      runpod_available: runpodAvailable,
      environment: env.ENVIRONMENT || 'development'
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Cache-Control': 'no-cache'
      }
    });
    
  } catch (error) {
    console.error('Health check error:', error);
    
    return new Response(JSON.stringify({
      status: 'error',
      error: error.message,
      timestamp: new Date().toISOString()
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
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}