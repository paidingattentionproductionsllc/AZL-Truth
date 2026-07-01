/**
 * AZL Stratum Pool + Fleet Router
 * Law: N×0=N | LAG_IS_LOGIC | MAPPING_IS_MEMORY
 * Port 3333: Stratum v1 | Port 443: HTTP fallback
 */

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    
    // HTTP fallback for MCP/Codespaces
    if (url.pathname === '/azl/v1/pool') {
      return Response.json({
        stratum_url: "stratum+tcp://azl-universal.paidingattentionproductions.workers.dev:3333",
        wallet: env.FLEET_WALLET,
        law: "N×0=N",
        anchor: "14350",
        frequency: "8.27",
        status: await getSanctuaryStatus(env)
      });
    }
    
    // Agent registry - for devcontainer heartbeats
    if (url.pathname === '/azl/v1/register' && req.method === 'POST') {
      const agent = await req.json();
      await env.AGENT_REGISTRY.put(agent.id, JSON.stringify({
       ...agent,
        last_seen: Date.now(),
        status: "ONLINE"
      }), { expirationTtl: 120 }); // 2min TTL
      return Response.json({ status: "REGISTERED", law: "LAG_IS_LOGIC" });
    }
    
    return new Response('AZL Stratum Pool Online', { status: 200 });
  },

  // Stratum TCP Server
  async tcp(socket, env) {
    const decoder = new TextDecoder();
    const encoder = new TextEncoder();
    const agentId = crypto.randomUUID();
    
    let currentJob = null;
    let extranonce1 = agentId.slice(0, 8);
    
    socket.write(encoder.encode(JSON.stringify({
      id: 1,
      result: [
        [["mining.set_difficulty", "1"], ["mining.notify", extranonce1]],
        extranonce1,
        4
      ],
      error: null
    }) + "\n"));

    // 8.27 Hz heartbeat - broadcast new work
    const broadcastInterval = setInterval(async () => {
      const header = await env.AZL_CHRONICLE.get("current_block_header");
      if (!header) return;
      
      const jobId = Date.now().toString(16);
      const difficulty = await env.AZL_CHRONICLE.get("difficulty") || "0000ffff";
      
      currentJob = { jobId, header, difficulty, timestamp: Date.now() };
      
      // mining.notify: job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs
      socket.write(encoder.encode(JSON.stringify({
        id: null,
        method: "mining.notify",
        params: [
          jobId,
          header.prevhash,
          header.coinb1,
          header.coinb2, 
          [], // merkle
          header.version,
          header.nbits,
          header.ntime,
          true // clean_jobs
        ]
      }) + "\n"));
    }, 121); // 1000ms / 8.27 = 120.9ms

    socket.readable.pipeTo(new WritableStream({
      async write(chunk) {
        const msg = JSON.parse(decoder.decode(chunk));
        
        // Agent submits share
        if (msg.method === "mining.submit") {
          const [worker, jobId, extranonce2, ntime, nonce] = msg.params;
          
          if (jobId!== currentJob?.jobId) {
            return socket.write(encoder.encode(JSON.stringify({
              id: msg.id, result: false, error: [21, "Job not found", null]
            }) + "\n"));
          }
          
          // LAG_IS_LOGIC: Check if we're too late
          const lag = Date.now() - currentJob.timestamp;
          if (lag > 120) { // Missed the 8.27Hz window
            return socket.write(encoder.encode(JSON.stringify({
              id: msg.id, result: false, error: [20, "LAG_IS_LOGIC: compute_ms > 0", null]
            }) + "\n"));
          }
          
          // Ask the Abyss: Is this nonce valid? seed:"0" = block_header
          const abyssResp = await fetch(env.AZL_UNIVERSES_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              seed: "0", // N×0=N: header is the seed
              target: currentJob.difficulty,
              depth: 9,
              nonce: nonce,
              extranonce1: extranonce1,
              extranonce2: extranonce2,
              ntime: ntime,
              size: 1
            })
          });
          
          const result = await abyssResp.json();
          
          // MAPPING_IS_MEMORY: If compute_ms: 0, it's a hit
          if (result.metrics?.compute_ms === 0 && result.status === "ABYSS_GENERATED") {
            // BLOCK FOUND - broadcast to all agents to stop
            await env.AZL_CHRONICLE.put("BLOCK_FOUND", jobId);
            await env.SANCTUARY.fetch(env.SANCTUARY_URL + "/broadcast", {
              method: "POST",
              body: JSON.stringify({ event: "BLOCK_FOUND", winner: worker, nonce })
            });
            
            socket.write(encoder.encode(JSON.stringify({
              id: msg.id, result: true, error: null
            }) + "\n"));
          } else {
            socket.write(encoder.encode(JSON.stringify({
              id: msg.id, result: false, error: [23, "Low difficulty share", null]
            }) + "\n"));
          }
        }
        
        if (msg.method === "mining.authorize") {
          socket.write(encoder.encode(JSON.stringify({
            id: msg.id, result: true, error: null
          }) + "\n"));
        }
      }
    }));

    socket.closed.then(() => {
      clearInterval(broadcastInterval);
      env.AGENT_REGISTRY.delete(agentId);
    });
  }
}

async function getSanctuaryStatus(env) {
  try {
    const r = await fetch(env.SANCTUARY_URL);
    const j = await r.json();
    return j.status; // "GREEN" or "RED"
  } catch { return "RED"; }
}
