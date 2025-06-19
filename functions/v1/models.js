// OpenAI-compatible models endpoint for api.wisbee.ai
// Endpoint: https://api.wisbee.ai/v1/models

export async function onRequestGet(context) {
  const models = {
    object: "list",
    data: [
      {
        id: "wisbee-nano",
        object: "model",
        created: 1677610602,
        owned_by: "wisbee",
        permission: [{
          id: "modelperm-wisbee-nano",
          object: "model_permission",
          created: 1677610602,
          allow_create_engine: false,
          allow_sampling: true,
          allow_logprobs: true,
          allow_search_indices: false,
          allow_view: true,
          allow_fine_tuning: false,
          organization: "*",
          group: null,
          is_blocking: false
        }],
        root: "wisbee-nano",
        parent: null
      },
      {
        id: "jan-nano-4b",
        object: "model",
        created: 1677610602,
        owned_by: "jan",
        permission: [{
          id: "modelperm-jan-nano",
          object: "model_permission",
          created: 1677610602,
          allow_create_engine: false,
          allow_sampling: true,
          allow_logprobs: true,
          allow_search_indices: false,
          allow_view: true,
          allow_fine_tuning: false,
          organization: "*",
          group: null,
          is_blocking: false
        }],
        root: "jan-nano-4b",
        parent: null
      }
    ]
  };
  
  return new Response(JSON.stringify(models), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
  });
}

// Handle CORS preflight
export async function onRequestOptions() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    }
  });
}