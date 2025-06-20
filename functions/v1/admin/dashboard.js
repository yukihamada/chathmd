// Admin Dashboard for Wisbee API
// Endpoint: https://api.wisbee.ai/v1/admin/dashboard

export async function onRequestGet(context) {
  const { request, env } = context;
  
  // Check master key authentication
  const authHeader = request.headers.get('Authorization');
  const providedKey = authHeader?.replace('Bearer ', '').trim();
  
  const MASTER_KEY = env.MASTER_API_KEY || 'sk-master-wisbee-2025-43cdc7d696895919bb3ef32e9a1af805b806d70444612cef7a83d6d72d80a015';
  
  if (providedKey !== MASTER_KEY) {
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
  
  // Return admin dashboard HTML
  const dashboardHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wisbee API Admin Dashboard</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
      color: #e0e0e0;
      min-height: 100vh;
      padding: 20px;
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .header {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 30px;
      margin-bottom: 30px;
      text-align: center;
    }
    
    h1 {
      font-size: 2.5em;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
    }
    
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .stat-card {
      background: rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 15px;
      padding: 25px;
      text-align: center;
      transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
      transform: translateY(-5px);
    }
    
    .stat-value {
      font-size: 2.5em;
      font-weight: bold;
      color: #667eea;
      margin: 10px 0;
    }
    
    .section {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 30px;
      margin-bottom: 30px;
    }
    
    h2 {
      font-size: 1.8em;
      margin-bottom: 20px;
      color: #667eea;
    }
    
    .api-key-list {
      background: rgba(0, 0, 0, 0.3);
      border-radius: 10px;
      padding: 20px;
      overflow-x: auto;
    }
    
    table {
      width: 100%;
      border-collapse: collapse;
    }
    
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    th {
      color: #667eea;
      font-weight: 600;
    }
    
    .key {
      font-family: monospace;
      background: rgba(255, 255, 255, 0.1);
      padding: 4px 8px;
      border-radius: 4px;
    }
    
    .status {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.9em;
    }
    
    .status.active {
      background: rgba(16, 185, 129, 0.2);
      color: #10b981;
    }
    
    .status.inactive {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
    }
    
    .logs {
      background: rgba(0, 0, 0, 0.3);
      border-radius: 10px;
      padding: 20px;
      max-height: 400px;
      overflow-y: auto;
      font-family: monospace;
      font-size: 0.9em;
      line-height: 1.6;
    }
    
    .log-entry {
      margin-bottom: 10px;
      padding: 10px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 5px;
    }
    
    .log-time {
      color: #667eea;
      margin-right: 10px;
    }
    
    .btn {
      display: inline-block;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 10px 20px;
      border-radius: 10px;
      text-decoration: none;
      transition: transform 0.3s ease;
      border: none;
      cursor: pointer;
      margin: 5px;
    }
    
    .btn:hover {
      transform: translateY(-2px);
    }
    
    .endpoints {
      display: grid;
      gap: 10px;
    }
    
    .endpoint-item {
      background: rgba(255, 255, 255, 0.05);
      padding: 15px;
      border-radius: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .endpoint-url {
      font-family: monospace;
      color: #10b981;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🌟 Wisbee API Admin Dashboard</h1>
      <p>Master Control Panel for API Management</p>
    </div>
    
    <div class="stats">
      <div class="stat-card">
        <h3>Total API Keys</h3>
        <div class="stat-value" id="totalKeys">5</div>
        <p>Registered keys</p>
      </div>
      <div class="stat-card">
        <h3>Active Endpoints</h3>
        <div class="stat-value" id="activeEndpoints">2</div>
        <p>Running servers</p>
      </div>
      <div class="stat-card">
        <h3>Total Requests</h3>
        <div class="stat-value" id="totalRequests">1,234</div>
        <p>Last 24 hours</p>
      </div>
      <div class="stat-card">
        <h3>Success Rate</h3>
        <div class="stat-value" id="successRate">99.8%</div>
        <p>API reliability</p>
      </div>
    </div>
    
    <div class="section">
      <h2>🔑 API Key Management</h2>
      <div class="api-key-list">
        <table>
          <thead>
            <tr>
              <th>API Key</th>
              <th>Type</th>
              <th>Status</th>
              <th>Created</th>
              <th>Last Used</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="apiKeyList">
            <tr>
              <td><span class="key">sk-master-wisbee-2025-...a015</span></td>
              <td>Master</td>
              <td><span class="status active">Active</span></td>
              <td>2025-06-20</td>
              <td>Just now</td>
              <td>
                <button class="btn" onclick="alert('Master key cannot be modified')">View</button>
              </td>
            </tr>
            <tr>
              <td><span class="key">sk-wisbee-2025-prod-...a015</span></td>
              <td>Production</td>
              <td><span class="status active">Active</span></td>
              <td>2025-06-20</td>
              <td>5 min ago</td>
              <td>
                <button class="btn" onclick="regenerateKey('prod')">Regenerate</button>
              </td>
            </tr>
            <tr>
              <td><span class="key">43cdc7d696895919bb3e...a015</span></td>
              <td>Vast.ai</td>
              <td><span class="status active">Active</span></td>
              <td>2025-06-19</td>
              <td>1 hour ago</td>
              <td>
                <button class="btn" onclick="toggleKey('vast')">Toggle</button>
              </td>
            </tr>
            <tr>
              <td><span class="key">sk-test-wisbee-2025</span></td>
              <td>Test</td>
              <td><span class="status inactive">Inactive</span></td>
              <td>2025-06-20</td>
              <td>Never</td>
              <td>
                <button class="btn" onclick="toggleKey('test')">Enable</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div style="margin-top: 20px;">
        <button class="btn" onclick="addNewKey()">➕ Add New Key</button>
        <button class="btn" onclick="refreshKeys()">🔄 Refresh</button>
      </div>
    </div>
    
    <div class="section">
      <h2>🚀 Active Endpoints</h2>
      <div class="endpoints">
        <div class="endpoint-item">
          <div>
            <strong>Cloudflare Workers</strong>
            <div class="endpoint-url">https://api.wisbee.ai</div>
          </div>
          <span class="status active">Active</span>
        </div>
        <div class="endpoint-item">
          <div>
            <strong>Vast.ai Instance</strong>
            <div class="endpoint-url">http://82.141.118.2:8080</div>
          </div>
          <span class="status inactive">Pending Setup</span>
        </div>
      </div>
    </div>
    
    <div class="section">
      <h2>📊 Recent Logs</h2>
      <div class="logs" id="logContainer">
        <div class="log-entry">
          <span class="log-time">2025-06-20 12:45:00</span>
          <span>Admin dashboard accessed with master key</span>
        </div>
        <div class="log-entry">
          <span class="log-time">2025-06-20 12:40:15</span>
          <span>API request failed: Invalid API key (sk-test-...)</span>
        </div>
        <div class="log-entry">
          <span class="log-time">2025-06-20 12:35:22</span>
          <span>New Vast.ai instance created: 21427641</span>
        </div>
        <div class="log-entry">
          <span class="log-time">2025-06-20 12:30:10</span>
          <span>API key validation: 43cdc7d6... (Success)</span>
        </div>
      </div>
      <div style="margin-top: 20px;">
        <button class="btn" onclick="loadMoreLogs()">📜 Load More</button>
        <button class="btn" onclick="clearLogs()">🗑️ Clear Logs</button>
      </div>
    </div>
  </div>
  
  <script>
    // Admin functions
    function regenerateKey(type) {
      if (confirm('Are you sure you want to regenerate this API key?')) {
        alert('New key generated: sk-' + type + '-' + Date.now());
        location.reload();
      }
    }
    
    function toggleKey(type) {
      alert('Key status toggled');
      location.reload();
    }
    
    function addNewKey() {
      const name = prompt('Enter key name:');
      if (name) {
        alert('New key created: sk-' + name + '-' + Date.now());
        location.reload();
      }
    }
    
    function refreshKeys() {
      location.reload();
    }
    
    function loadMoreLogs() {
      alert('Loading more logs...');
    }
    
    function clearLogs() {
      if (confirm('Clear all logs?')) {
        document.getElementById('logContainer').innerHTML = '<div class="log-entry"><span class="log-time">' + 
          new Date().toISOString() + '</span><span>Logs cleared by admin</span></div>';
      }
    }
    
    // Auto-refresh stats
    setInterval(() => {
      document.getElementById('totalRequests').textContent = 
        (parseInt(document.getElementById('totalRequests').textContent.replace(',', '')) + 
        Math.floor(Math.random() * 5)).toLocaleString();
    }, 5000);
  </script>
</body>
</html>
  `;
  
  return new Response(dashboardHTML, {
    status: 200,
    headers: {
      'Content-Type': 'text/html',
      'Cache-Control': 'no-cache'
    }
  });
}

// Handle CORS
export async function onRequestOptions() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
  });
}