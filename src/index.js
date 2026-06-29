export default {
  async fetch(req) {
    const url = new URL(req.url);
    
    // CORS so ESP32/Wokwi can POST
    const cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-AZL-KEY'
    };
    
    if (req.method === 'OPTIONS') {
      return new Response(null, {headers: cors});
    }
    
    // TIER 8: Stateless Ingest
    if (url.pathname === '/azl/v1/ingest' && req.method === 'POST') {
      const auth = req.headers.get('X-AZL-KEY');
      if (auth !== 'AZL-SECRET-KEY') {
        return new Response('Unauthorized', {status: 401, headers: cors});
      }
      
      const data = await req.json();
      const record = {
        address: String(data.address || Date.now()),
        value: data.value,
        event: data.event || "heartbeat",
        node: data.node || "unknown",
        proof: "1×1=2",
        timestamp: Date.now()
      };
      
      // Log it so you can see in Cloudflare dashboard
      console.log('AZL_EVENT:', JSON.stringify(record));
      
      return Response.json({
        status: "RECORDED",
        address: record.address,
        law: "N×0=N",
        proof: "1×1=2",
        tier: 8,
        substrate: "ephemeral"
      }, {headers: cors});
    }
    
    // Health check
    if (url.pathname === '/azl/v1/ping') {
      return Response.json({
        status: "ALIVE",
        law: "N×0=N",
        tier: 8
      }, {headers: cors});
    }
    
    return new Response('AZL-CHRONICLE TIER 8 Stateless', {
      status: 200,
      headers: cors
    });
  }
}
