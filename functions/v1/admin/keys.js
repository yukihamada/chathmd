// API Key Management Endpoint
// Endpoint: https://api.wisbee.ai/v1/admin/keys

// In-memory storage for demo (in production, use Cloudflare KV or D1)
const DEFAULT_KEYS = [
  {
    id: 'master',
    key: 'sk-master-wisbee-2025-43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015',
    type: 'master',
    status: 'active',
    created: '2025-06-20',
    lastUsed: new Date().toISOString()
  },
  {
    id: 'prod',
    key: 'sk-wisbee-2025-prod-43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015',
    type: 'production',
    status: 'active',
    created: '2025-06-20',
    lastUsed: new Date().toISOString()
  },
  {
    id: 'vast',
    key: '43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015',
    type: 'vast.ai',
    status: 'active',
    created: '2025-06-19',
    lastUsed: new Date().toISOString()
  },
  {
    id: 'test',
    key: 'sk-test-wisbee-2025',
    type: 'test',
    status: 'active',
    created: '2025-06-20',
    lastUsed: null
  }
];

// Check if request has master key
function validateMasterKey(request, env) {
  const authHeader = request.headers.get('Authorization');
  const providedKey = authHeader?.replace('Bearer ', '').trim();
  const MASTER_KEY = env.MASTER_API_KEY || 'sk-master-wisbee-2025-43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015';
  
  return providedKey === MASTER_KEY;
}

export async function onRequestGet(context) {
  const { request, env } = context;
  
  if (!validateMasterKey(request, env)) {
    return new Response(JSON.stringify({
      error: {
        message: 'Invalid master API key',
        type: 'authentication_error'
      }
    }), {
      status: 401,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
  
  // Return all API keys
  return new Response(JSON.stringify({
    keys: DEFAULT_KEYS,
    total: DEFAULT_KEYS.length
  }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  
  if (!validateMasterKey(request, env)) {
    return new Response(JSON.stringify({
      error: {
        message: 'Invalid master API key',
        type: 'authentication_error'
      }
    }), {
      status: 401,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
  
  try {
    const body = await request.json();
    const { action, keyId, keyType } = body;
    
    switch (action) {
      case 'create':
        // Generate new key
        const newKey = {
          id: Date.now().toString(),
          key: `sk-${keyType}-${Date.now()}-${Math.random().toString(36).substring(2)}`,
          type: keyType || 'custom',
          status: 'active',
          created: new Date().toISOString(),
          lastUsed: null
        };
        
        return new Response(JSON.stringify({
          success: true,
          key: newKey
        }), {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
        
      case 'toggle':
        // Toggle key status (in real implementation, update in KV)
        return new Response(JSON.stringify({
          success: true,
          message: `Key ${keyId} status toggled`
        }), {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
        
      case 'delete':
        // Delete key (in real implementation, remove from KV)
        return new Response(JSON.stringify({
          success: true,
          message: `Key ${keyId} deleted`
        }), {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
        
      default:
        return new Response(JSON.stringify({
          error: {
            message: 'Invalid action',
            type: 'invalid_request'
          }
        }), {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
    }
  } catch (error) {
    return new Response(JSON.stringify({
      error: {
        message: 'Invalid request body',
        type: 'invalid_request'
      }
    }), {
      status: 400,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}

// Handle CORS
export async function onRequestOptions() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
  });
}