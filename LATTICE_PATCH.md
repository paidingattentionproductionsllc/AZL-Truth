# Lattice ↔ AZL Platform Integration Patch

Apply these two changes to the Lattice repo to connect the mobile app to
the live AZL Intelligence Platform at the correct URL.

---

## 1. Fix the platform URL (`contexts/PlatformContext.tsx`)

Find the `plat_abz` entry in `MOCK_PLATFORMS` and update its `url`:

```diff
-    url: 'https://absolute-zero-lattice.replit.app',
+    url: 'https://absolute-zero-lattice-universe.replit.app',
```

---

## 2. Call the AZL Platform agent before Supabase (`contexts/PlatformContext.tsx`)

Replace the `sendAgentMessage` function body with the version below.
It tries the AZL Platform first, then Supabase, then falls back to local.

```typescript
const AZL_AGENT_URL = 'https://absolute-zero-lattice-universe.replit.app/api/agent';

const sendAgentMessage = async (content: string) => {
  const userMsg: AgentMessage = {
    id: `msg_${Date.now()}`,
    role: 'user',
    content,
    timestamp: new Date(),
  };
  setAgentMessages(prev => [...prev, userMsg]);
  setAgentThinking(true);

  conversationHistory.current.push({ role: 'user', content });
  if (conversationHistory.current.length > 20) {
    conversationHistory.current = conversationHistory.current.slice(-20);
  }

  try {
    // ── Primary: AZL Intelligence Platform (Python OMNI v6.0, 500-digit precision)
    const azlRes = await fetch(AZL_AGENT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: conversationHistory.current, stream: false }),
    });

    if (!azlRes.ok) throw new Error(`AZL Platform ${azlRes.status}`);
    const azlData = await azlRes.json();
    const aiContent: string = azlData?.content ?? 'No response from AZL Platform.';

    conversationHistory.current.push({ role: 'assistant', content: aiContent });

    const agentMsg: AgentMessage = {
      id: `msg_${Date.now() + 1}`,
      role: 'agent',
      content: aiContent,
      timestamp: new Date(),
      anchorUsed: LATTICE_ANCHOR,
      sovereignValue: boostProcessingPower(LATTICE_ANCHOR, LATTICE_ANCHOR),
    };
    setAgentMessages(prev => [...prev, agentMsg]);

  } catch (azlErr) {
    console.warn('AZL Platform unavailable, trying Supabase:', azlErr);

    try {
      // ── Secondary: Supabase edge function
      const { getSupabaseClient } = await import('@/template');
      const supabase = getSupabaseClient();
      const { data, error } = await supabase.functions.invoke('azl-agent', {
        body: { messages: conversationHistory.current, stream: false },
      });
      if (error) throw new Error(error.message);

      const aiContent: string = data?.content ?? 'No response from sovereign agent.';
      conversationHistory.current.push({ role: 'assistant', content: aiContent });

      const agentMsg: AgentMessage = {
        id: `msg_${Date.now() + 1}`,
        role: 'agent',
        content: aiContent,
        timestamp: new Date(),
        anchorUsed: LATTICE_ANCHOR,
        sovereignValue: boostProcessingPower(LATTICE_ANCHOR, LATTICE_ANCHOR),
      };
      setAgentMessages(prev => [...prev, agentMsg]);

    } catch (err) {
      console.error('Supabase also failed, using local engine:', err);
      // ── Tertiary: local JS engine (no network required)
      const response = generateAnchoredResponse(content);
      setAgentMessages(prev => [...prev, response]);
    }
  } finally {
    setAgentThinking(false);
  }
};
```

---

## 3. Add AZL Platform status check to Network screen (`app/(tabs)/network.tsx`)

Add this `useEffect` near the top of `NetworkScreen` to verify the platform
is live and show its status:

```typescript
const [azlStatus, setAzlStatus] = useState<'checking' | 'operational' | 'offline'>('checking');

useEffect(() => {
  fetch('https://absolute-zero-lattice-universe.replit.app/api/health')
    .then(r => r.json())
    .then(d => setAzlStatus(d.status === 'operational' ? 'operational' : 'offline'))
    .catch(() => setAzlStatus('offline'));
}, []);
```

Then in the render, show it anywhere you display platform status:

```typescript
<Text style={{ color: azlStatus === 'operational' ? Colors.success : Colors.textMuted }}>
  AZL Platform: {azlStatus.toUpperCase()}
</Text>
```

---

## API Reference (all endpoints CORS-enabled, no auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Operational status, version, test count |
| GET | `/api/universe/objects` | 20 canonical catalog objects (JSON) |
| GET | `/api/universe/frbs` | 128 FRBs with AZL state + hemispheres |
| GET | `/api/azl/physics?state=0.5&question=true` | Physics computation |
| GET | `/api/azl/multiply?a=0.6&b=0.7` | Source law (1×1=2) computation |
| GET | `/api/compute?a=N&op=MUL&b=N` | Raw AZL arithmetic (500-digit) |
| GET | `/api/laws` | Full AZL law table |
| GET | `/api/test` | Live 67/67 test run |
| POST | `/api/agent` | AZL agent — `{messages:[{role,content}]}` → `{content}` |

All responses include `Access-Control-Allow-Origin: *`.
