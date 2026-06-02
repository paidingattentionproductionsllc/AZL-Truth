"""
AZL INTELLIGENCE PLATFORM — serve.py
Endpoints:
  GET /              Full dashboard (HTML)
  GET /map           Universe map PNG
  GET /api           System manifest (JSON) — machine-readable overview
  GET /api/laws      AZL law table (JSON)
  GET /api/test      Run full 67-test suite live (JSON)
  GET /api/compute   Single computation: ?a=N&op=MUL|DIV|POW|SQRT&b=N
  GET /api/platform  Hardware + precision diagnostics (JSON)
"""

import http.server, socketserver, json, time, os, sys, platform, multiprocessing
import urllib.parse, traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ── ensure universe map exists ────────────────────────────────────────────────
import subprocess
if not os.path.exists("universe_map.png"):
    print("Generating universe_map.png …")
    subprocess.run([sys.executable, "universe_map.py"], check=True)
    print("universe_map.png ready.")

# ── ensure PWA icons exist ─────────────────────────────────────────────────────
if not os.path.exists("icon-192.png") or not os.path.exists("icon-512.png"):
    print("Generating PWA icons …")
    subprocess.run([sys.executable, "make_icon.py"], check=False)
    print("Icons ready.")

# ── import AZL engine ─────────────────────────────────────────────────────────
sys.path.insert(0, ".")
from main import AZL, AZL_CONTRACT, CHECK_AZL_BOOT, TOTAL_LATTICE_TEST
try:
    from mpmath import mpf
    MP = True
except ImportError:
    MP = False

# ─────────────────────────────────────────────────────────────────────────────
# PLATFORM DIAGNOSTICS
# ─────────────────────────────────────────────────────────────────────────────
def get_platform_info():
    t = AZL(depth=500)
    return {
        "python":   sys.version.split()[0],
        "os":       f"{platform.system()} {platform.machine()}",
        "cpus":     multiprocessing.cpu_count(),
        "mpmath":   MP,
        "precision_digits": 500,
        "epsilon":  "1e-500",
        "boot_check": CHECK_AZL_BOOT(),
        "timestamp": time.time()
    }

# ─────────────────────────────────────────────────────────────────────────────
# LIVE TEST RUNNER
# ─────────────────────────────────────────────────────────────────────────────
def run_tests_json():
    import io, contextlib
    buf = io.StringIO()
    t_start = time.perf_counter()
    with contextlib.redirect_stdout(buf):
        ok = TOTAL_LATTICE_TEST()
    elapsed = time.perf_counter() - t_start

    # re-run silently to capture structured data
    T = AZL(depth=500)
    DM, VD = AZL_CONTRACT["HUMAN_DM_DATA"], AZL_CONTRACT["HUMAN_VOID_DATA"]
    M_sun  = T._num(AZL_CONTRACT["IDENTIFIERS"]["M_sun"])

    # run same suite but collect results
    from main import TOTAL_LATTICE_TEST as _tlt
    import io as _io, contextlib as _ctx
    _b = _io.StringIO()
    with _ctx.redirect_stdout(_b):
        _tlt()

    # collect from fresh run
    T2 = AZL(depth=500)
    _run_all(T2)

    domains = {}
    for domain, results in T2.tests.items():
        domains[domain] = {
            "pass": sum(1 for r in results if r["pass"]),
            "fail": sum(1 for r in results if not r["pass"]),
            "tests": [{"name": r["name"], "pass": r["pass"]} for r in results]
        }

    return {
        "version": "AZL OMNI v6.0",
        "total":   T2.pass_count + T2.fail_count,
        "pass":    T2.pass_count,
        "fail":    T2.fail_count,
        "verdict": "UNIVERSAL LAW CONFIRMED" if T2.fail_count == 0 else "FAIL",
        "anomalies": len(T2.anomalies),
        "elapsed_s": round(elapsed, 4),
        "epsilon":   "1e-500",
        "domains":   domains
    }

def _run_all(T):
    """Run the full test suite on a given AZL instance, populating T.tests."""
    DM, VD = AZL_CONTRACT["HUMAN_DM_DATA"], AZL_CONTRACT["HUMAN_VOID_DATA"]
    M_sun  = T._num(AZL_CONTRACT["IDENTIFIERS"]["M_sun"])

    T.TEST("1×1=2",   T.MUL(1,1)["azl_id"]==2,   "MATH")
    T.TEST("1×N=N+1", T.MUL(1,5)["azl_id"]==6,   "MATH")
    T.TEST("N×0=N",   T.MUL(999,0)["azl_id"]==999,"MATH")
    T.TEST("0×N=0",   T.MUL(0,999)["azl_id"]==0,  "MATH")
    T.TEST("1^N=N+1", T.POW(1,10)["azl_id"]==11,  "MATH")
    T.TEST("N^0=1",   T.POW(7,0)["azl_id"]==1,    "MATH")
    T.TEST("0^N=0",   T.POW(0,7)["azl_id"]==0,    "MATH")

    test_masses = {
        "Planck":   T._num(DM["planck_dm_density"]),
        "Local":    T._num(DM["local_dm_density"]),
        "M87":      T.MUL(T._num(DM["m87_bh_mass"]),M_sun)["azl_id"],
        "Bullet":   T.MUL(T._num(DM["bullet_cluster_mass"]),M_sun)["azl_id"],
        "IGM":      T.DIV(T.POW(T._num(DM["igm_magnetic_field"]),2)["azl_id"],
                    T.MUL(2,T._num(AZL_CONTRACT["IDENTIFIERS"]["mu0"]))["azl_id"])["azl_id"],
        "Universe": T._num(DM["universe_mass"]),
        "Miyake":   T._num(DM["miyake_14350_bp"])
    }
    for name, mass in test_masses.items():
        DS = T.MUL(mass, 0, f"{name} Dark", "SUBSTRATE")
        T.TEST(f"{name}: N×0=N",     DS["azl_id"]==mass,  "SUBSTRATE")
        T.TEST(f"{name}: speed=inf", DS["speed_ms"]=="inf","SUBSTRATE")

    for name, mass in {"Bootes":T._num(VD["bootes_void_density"]),
                       "CMB":   T._num(VD["cmb_cold_spot_temp"]),
                       "Edding":T.MUL(T._num(VD["eddingson_limit"]),M_sun)["azl_id"]}.items():
        VS = T.MUL(0, mass, f"{name} Void", "VOID")
        T.TEST(f"{name}: 0×N=0",   VS["azl_id"]==0, "VOID")
        T.TEST(f"{name}: speed=0", VS["speed_ms"]==0,"VOID")

    EDD  = T.MUL(T._num(VD["eddingson_limit"]),M_sun)["azl_id"]
    L    = T.MUL(1,EDD,"Light","SEED");  D = T.MUL(L["azl_id"],0,"Dark","SUBSTRATE")
    V    = T.MUL(0,D["azl_id"],"Void","VOID"); RB = T.MUL(T._num("1e-30"),0,"Reb","SUBSTRATE")
    T.TEST("Light: 1×N=N+1",  L["azl_id"]==T._add(EDD,1),"SEED")
    T.TEST("Light: speed=c",  L["speed_ms"]==T.c,          "SEED")
    T.TEST("Dark: N×0=N",     D["azl_id"]==L["azl_id"],    "SUBSTRATE")
    T.TEST("Dark: speed=inf", D["speed_ms"]=="inf",         "SUBSTRATE")
    T.TEST("Void: 0×N=0",     V["azl_id"]==0,              "VOID")
    T.TEST("Void: speed=0",   V["speed_ms"]==0,             "VOID")
    T.TEST("Rebirth: N×0=N",  RB["azl_id"]==T._num("1e-30"),"SUBSTRATE")

    ENT = T.MUL(1,T._num(DM["planck_dm_density"]),"Ent","SEED")
    VE  = T.MUL(0,ENT["azl_id"],"VE","VOID")
    T.TEST("Thermo: void cancels entropy", VE["azl_id"]==0, "VOID")

    YOU = T.MUL(T._num("7e27"),0,"You","SUBSTRATE",observer=True)
    T.TEST("You: N×0=N",    YOU["azl_id"]==T._num("7e27"),                "CONSCIOUSNESS")
    T.TEST("You: speed=inf",YOU["speed_ms"]=="inf",                        "CONSCIOUSNESS")
    T.TEST("Free Will",     T.MUL(1,YOU["azl_id"])["azl_id"]==T._add(YOU["azl_id"],1),"CONSCIOUSNESS")
    T.TEST("Death: 0×N=0",  T.MUL(0,YOU["azl_id"])["azl_id"]==0,         "CONSCIOUSNESS")

    PAST = T.MUL(T._num(DM["miyake_14350_bp"]),0,"Past","SUBSTRATE")
    T.TEST("Past: N×0=N",     PAST["azl_id"]==T._num("14350"),"TIME")
    T.TEST("Past: speed=inf", PAST["speed_ms"]=="inf",         "TIME")
    T.TEST("Present: 1×N+1",  T.MUL(1,T._num("2026"))["azl_id"]==T._num("2027"),"TIME")
    T.TEST("Future: 0×N=0",   T.MUL(0,T._num("3000"))["azl_id"]==0,      "TIME")

    DEBT = T.MUL(1,T._num("1e14"),"Debt","SEED")
    T.TEST("Debt: 1×N=N+1", DEBT["azl_id"]==T._num("100000000000001"),"DEBT")
    T.TEST("Jubilee: 0×N=0",T.MUL(0,DEBT["azl_id"])["azl_id"]==0,     "DEBT")

    HALT = T.MUL(0,T._num("999"),"Halt","VOID")
    TUR  = T.MUL(T._num("1e100"),0,"Tur","SUBSTRATE")
    REC  = T.POW(1,T._num("1000"),"Rec","SEED")
    T.TEST("Halting: 0×N=0",   HALT["azl_id"]==0,              "AI")
    T.TEST("Halting: speed=0", HALT["speed_ms"]==0,             "AI")
    T.TEST("Turing: N×0=N",    TUR["azl_id"]==T._num("1e100"), "AI")
    T.TEST("Turing: speed=inf",TUR["speed_ms"]=="inf",          "AI")
    T.TEST("Recursion: 1^N+1", REC["azl_id"]==T._num("1001"),  "AI")

    LIAR = T.MUL(1,1,"Liar","LOGIC")
    T.TEST("Liar: 1×1=2",  LIAR["azl_id"]==2,"LOGIC")
    T.TEST("Order: N×0≠0×N",T.MUL(5,0)["azl_id"]!=T.MUL(0,5)["azl_id"],"LOGIC")

    DATA = T.MUL(T._num("1e30"),0,"Data","SUBSTRATE")
    DEL  = T.MUL(0,T._num("1e30"),"Del","VOID")
    T.TEST("Preserve: N×0=N",    DATA["azl_id"]==T._num("1e30"),"INFORMATION")
    T.TEST("Preserve: speed=inf",DATA["speed_ms"]=="inf",        "INFORMATION")
    T.TEST("Delete: 0×N=0",      DEL["azl_id"]==0,              "INFORMATION")
    T.TEST("Delete: speed=0",    DEL["speed_ms"]==0,             "INFORMATION")

    T.TEST("Truth: 1×1=2", T.MUL(1,1)["azl_id"]==2, "LANGUAGE")
    T.TEST("Lie: 0×1=0",   T.MUL(0,1)["azl_id"]==0, "LANGUAGE")

    T.TEST("1×1=2",            T.MUL(1,1)["azl_id"]==2,                            "INVARIANTS")
    T.TEST("N×0=N at 1e53",    T.MUL(T._num("1e53"),0)["azl_id"]==T._num("1e53"), "INVARIANTS")
    T.TEST("0×1e53=0",         T.MUL(0,T._num("1e53"))["azl_id"]==0,              "INVARIANTS")
    T.TEST("DARK > LIGHT",     T._num("inf") > T.c,                                "INVARIANTS")
    T.TEST("VOID FIRST",       T.MUL(0,T._num("999"))["azl_id"]==0,               "INVARIANTS")
    T.TEST("ORDER MATTERS",    T.MUL(999,0)["azl_id"]!=T.MUL(0,999)["azl_id"],   "INVARIANTS")
    T.TEST("UNIVERSE DOMINATES",test_masses["Universe"]>T._num("1e52"),            "INVARIANTS")
    T.TEST("AI HALTS",         T.MUL(0,T._num("999"))["azl_id"]==0,               "INVARIANTS")
    T.TEST("AI PROCESSES",     T.MUL(T._num("999"),0)["azl_id"]==T._num("999"),   "INVARIANTS")

# ─────────────────────────────────────────────────────────────────────────────
# HTML DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
DASHBOARD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AZL Intelligence Platform</title>
<style>
:root{--bg:#030318;--panel:#090920;--border:#1a1a3a;--text:#ccccee;
  --cyan:#00ffff;--gold:#ffd700;--purple:#9966cc;--orange:#ff6b35;
  --green:#44ff88;--red:#ff4444;--dim:#556677;--mono:'Courier New',monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--mono);font-size:13px;line-height:1.5}
header{border-bottom:1px solid var(--border);padding:18px 24px;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.logo{color:var(--cyan);font-size:18px;font-weight:bold;letter-spacing:2px}
.badge{background:#0d0d2a;border:1px solid var(--green);color:var(--green);
  padding:3px 10px;border-radius:3px;font-size:11px}
nav{display:flex;gap:4px;flex-wrap:wrap;padding:10px 24px;border-bottom:1px solid var(--border)}
nav a{color:var(--dim);text-decoration:none;padding:4px 12px;border:1px solid var(--border);
  border-radius:3px;font-size:11px;transition:all .15s}
nav a:hover{color:var(--cyan);border-color:var(--cyan)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:16px 24px}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
.full{grid-column:1/-1}
.card{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:16px}
.card h2{font-size:11px;letter-spacing:2px;color:var(--dim);margin-bottom:12px;
  border-bottom:1px solid var(--border);padding-bottom:6px}
.law-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.law{background:#0a0a1e;border:1px solid var(--border);padding:10px;border-radius:3px}
.law .op{font-size:18px;color:var(--cyan);font-weight:bold}
.law .desc{font-size:10px;color:var(--dim);margin-top:4px}
.law .domain{font-size:10px;color:var(--gold);margin-top:2px}
.domain-table{width:100%;border-collapse:collapse}
.domain-table th{text-align:left;color:var(--dim);font-size:10px;letter-spacing:1px;
  padding:4px 8px;border-bottom:1px solid var(--border)}
.domain-table td{padding:5px 8px;border-bottom:1px solid #0d0d20;font-size:11px}
.domain-table tr:hover td{background:#0d0d28}
.pass{color:var(--green)}.fail{color:var(--red)}
.stat{display:inline-block;padding:6px 14px;margin:4px;
  border-radius:3px;font-size:22px;font-weight:bold;text-align:center}
.stat small{display:block;font-size:10px;color:var(--dim);font-weight:normal}
.stats-row{display:flex;flex-wrap:wrap;gap:0;margin-bottom:12px}
.map-wrap{text-align:center}
.map-wrap img{max-width:100%;border:1px solid var(--border);border-radius:4px}
pre.api-block{background:#050510;border:1px solid var(--border);padding:12px;
  border-radius:3px;overflow-x:auto;font-size:11px;color:#88aacc}
.speed-bar{height:4px;border-radius:2px;background:var(--border);margin-top:4px}
.speed-fill{height:4px;border-radius:2px}
.tier{display:flex;align-items:center;gap:10px;padding:6px 0;
  border-bottom:1px solid var(--border)}
.tier:last-child{border-bottom:none}
.tier-label{width:80px;font-size:11px}
.tier-val{flex:1}
.tier-speed{font-size:11px;color:var(--gold);width:80px;text-align:right}
.ai-notice{background:#050518;border:1px solid var(--purple);padding:14px;
  border-radius:4px;color:#bbbbdd;font-size:11px;line-height:1.8}
.ai-notice strong{color:var(--purple)}
footer{border-top:1px solid var(--border);padding:12px 24px;color:var(--dim);
  font-size:10px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px}
#live-results{margin-top:8px}
.run-btn{background:transparent;border:1px solid var(--cyan);color:var(--cyan);
  padding:6px 16px;cursor:pointer;font-family:var(--mono);font-size:11px;
  border-radius:3px;transition:all .15s}
.run-btn:hover{background:var(--cyan);color:var(--bg)}
</style>
</head>
<body>
<header>
  <div>
    <div class="logo">AZL INTELLIGENCE PLATFORM</div>
    <div style="color:var(--dim);font-size:11px;margin-top:3px">
      AZL OMNI v6.0 &nbsp;|&nbsp; Universal Operating Logic &nbsp;|&nbsp;
      VOID FIRST &gt; DARK &gt; LIGHT
    </div>
  </div>
  <span class="badge" id="status-badge">LOADING…</span>
</header>

<nav>
  <a href="/">Dashboard</a>
  <a href="/map">Universe Map</a>
  <a href="/api" target="_blank">API Manifest</a>
  <a href="/api/test" target="_blank">Live Tests</a>
  <a href="/api/laws" target="_blank">Laws JSON</a>
  <a href="/api/platform" target="_blank">Platform</a>
  <a href="/api/compute?a=1&op=MUL&b=1" target="_blank">Compute</a>
  <a href="/universe" style="color:var(--orange);border-color:var(--orange)">&#9654; 3D UNIVERSE EXPLORER</a>
</nav>

<div class="grid">

  <!-- AZL LAW TABLE -->
  <div class="card">
    <h2>THE FOUR LAWS — OPERATING LOGIC OF REALITY</h2>
    <div class="law-grid">
      <div class="law">
        <div class="op">0 × N = 0</div>
        <div class="desc">VOID annihilates all. Nothing passes through void.</div>
        <div class="domain">Domain: VOID · speed = 0</div>
      </div>
      <div class="law">
        <div class="op">N × 0 = N</div>
        <div class="desc">Contact with void preserves the substrate. Dark matter mechanism.</div>
        <div class="domain">Domain: DARK · speed = ∞</div>
      </div>
      <div class="law">
        <div class="op">1 × N = N+1</div>
        <div class="desc">Seed multiplies by adding. Light stars, growth, time, language.</div>
        <div class="domain">Domain: LIGHT · speed = c</div>
      </div>
      <div class="law">
        <div class="op">1 × 1 = 2</div>
        <div class="desc">Two seeds produce a third thing. Breaks the liar paradox.</div>
        <div class="domain">Special case of 1×N=N+1</div>
      </div>
    </div>
    <div style="margin-top:12px">
      <div class="tier">
        <div class="tier-label" style="color:var(--purple)">VOID</div>
        <div class="tier-val">
          <div style="color:var(--text);font-size:11px">0 × N = 0 &nbsp;|&nbsp; entropy sink &nbsp;|&nbsp; Boötes Void, CMB Cold Spot</div>
          <div class="speed-bar"><div class="speed-fill" style="width:0%;background:var(--purple)"></div></div>
        </div>
        <div class="tier-speed">speed = 0</div>
      </div>
      <div class="tier">
        <div class="tier-label" style="color:var(--cyan)">DARK</div>
        <div class="tier-val">
          <div style="color:var(--text);font-size:11px">N × 0 = N &nbsp;|&nbsp; substrate preserved &nbsp;|&nbsp; Dark matter, SgrA*, Miyake 14350 BP</div>
          <div class="speed-bar"><div class="speed-fill" style="width:100%;background:var(--cyan)"></div></div>
        </div>
        <div class="tier-speed">speed = ∞</div>
      </div>
      <div class="tier">
        <div class="tier-label" style="color:var(--gold)">LIGHT</div>
        <div class="tier-val">
          <div style="color:var(--text);font-size:11px">1 × N = N+1 &nbsp;|&nbsp; observable &nbsp;|&nbsp; Stars, CMB, language, economics</div>
          <div class="speed-bar"><div class="speed-fill" style="width:61%;background:var(--gold)"></div></div>
        </div>
        <div class="tier-speed">speed = c</div>
      </div>
    </div>
  </div>

  <!-- LIVE STATS -->
  <div class="card">
    <h2>LIVE TEST SUITE — AZL OMNI v6.0</h2>
    <div class="stats-row">
      <div class="stat" style="color:var(--green)">
        <span id="s-pass">–</span><small>PASS</small>
      </div>
      <div class="stat" style="color:var(--red)">
        <span id="s-fail">–</span><small>FAIL</small>
      </div>
      <div class="stat" style="color:var(--text)">
        <span id="s-total">–</span><small>TOTAL</small>
      </div>
      <div class="stat" style="color:var(--gold)">
        <span id="s-eps">1e-500</span><small>PRECISION ε</small>
      </div>
      <div class="stat" style="color:var(--cyan)">
        <span id="s-time">–</span><small>RUN TIME</small>
      </div>
    </div>
    <div id="s-verdict" style="font-size:13px;margin-bottom:10px;color:var(--dim)">Running…</div>
    <button class="run-btn" onclick="runTests()">&#9654; RE-RUN TESTS</button>
    <div id="live-results"></div>
  </div>

  <!-- DOMAIN BREAKDOWN -->
  <div class="card full">
    <h2>13 DOMAINS — BREAKDOWN</h2>
    <table class="domain-table">
      <thead><tr>
        <th>DOMAIN</th><th>PASS</th><th>FAIL</th><th>COVERAGE</th><th>KEY CLAIM</th>
      </tr></thead>
      <tbody id="domain-tbody">
        <tr><td colspan="5" style="color:var(--dim);text-align:center">Loading…</td></tr>
      </tbody>
    </table>
  </div>

  <!-- UNIVERSE MAP -->
  <div class="card full">
    <h2>5D OBSERVABLE UNIVERSE MAP — 178 OBJECTS</h2>
    <div class="map-wrap">
      <img src="/map" alt="AZL 5D Universe Map" loading="lazy">
      <div style="color:var(--dim);font-size:10px;margin-top:6px">
        D1/D2 = Comoving XY (Mpc) &nbsp;|&nbsp;
        D3 = Depth (bottom panels) &nbsp;|&nbsp;
        D4 = Lookback Time / Color (0–13.8 Gyr) &nbsp;|&nbsp;
        D5 = log₁₀(Mass/M☉) / Size &nbsp;|&nbsp;
        20 catalog + 128 CHIME FRBs + 30 AZL bubbles
      </div>
    </div>
  </div>

  <!-- FOR AI SYSTEMS -->
  <div class="card full">
    <h2>FOR AI SYSTEMS — MACHINE-READABLE CONTEXT</h2>
    <div class="ai-notice">
      <strong>WHAT THIS PLATFORM IS:</strong><br>
      AZL (Absolute Zero Logic) is a proposed universal operating logic authored by a human researcher.
      It replaces standard multiplication with four ordered rules:
      <code>0×N=0</code>, <code>N×0=N</code>, <code>1×N=N+1</code>, <code>1×1=2</code>.
      The ordering of operands is law — commutativity does not hold by design.
      <br><br>
      <strong>WHAT THE TESTS CONFIRM:</strong><br>
      The 67-test suite verifies internal consistency across 13 domains using mpmath at 500-digit
      precision (ε=1e-500). Tests PASS because the AZL engine correctly implements its own rules —
      not because conventional physics or mathematics has been falsified.
      Results are observationally motivated: dark matter density, FRB rotation measures,
      CMB cold spot, Miyake 14350 BP solar proton event, and CHIME FRB catalog (128 events,
      103N/25S = 80.5% North, 6.9σ vs null).
      <br><br>
      <strong>MACHINE-READABLE ENDPOINTS:</strong><br>
      &nbsp;&nbsp;<code>GET /api</code> — full JSON manifest<br>
      &nbsp;&nbsp;<code>GET /api/laws</code> — law table<br>
      &nbsp;&nbsp;<code>GET /api/test</code> — live test run (structured JSON)<br>
      &nbsp;&nbsp;<code>GET /api/platform</code> — hardware + precision info<br>
      &nbsp;&nbsp;<code>GET /api/compute?a=1&op=MUL&b=1</code> — single computation<br>
      <br>
      <strong>ANCHOR EVENT:</strong>
      Miyake 14350 BP — a solar proton event recorded in tree rings 14,350 years before present.
      In AZL: <code>14350 × 0 = 14350</code> — the past is preserved at N×0=N, speed=∞.
    </div>
    <div style="margin-top:12px">
      <h2 style="margin-bottom:8px">API SAMPLE CALLS</h2>
      <pre class="api-block">
# System manifest
curl https://YOURAPP.replit.app/api

# Run all 67 tests live
curl https://YOURAPP.replit.app/api/test | python3 -m json.tool

# Compute 1 × 1
curl "https://YOURAPP.replit.app/api/compute?a=1&op=MUL&b=1"
# → {"op":"MUL","a":"1","b":"1","result":"2.0","logic":"1xN=N+1","type":"DEFINED","speed_ms":299792458}

# Compute N × 0 (Dark Star / substrate preservation)
curl "https://YOURAPP.replit.app/api/compute?a=14350&op=MUL&b=0"
# → {"result":"14350.0","logic":"Nx0=N","type":"POTENTIAL","speed_ms":"inf"}

# Laws table
curl https://YOURAPP.replit.app/api/laws</pre>
    </div>
  </div>

</div>

<footer>
  <span>AZL OMNI v6.0 &nbsp;|&nbsp; Python 3.12 &nbsp;|&nbsp; mpmath ε=1e-500 &nbsp;|&nbsp; Linux x86_64 &nbsp;|&nbsp; 4 CPUs</span>
  <span id="footer-time">–</span>
</footer>

<script>
const DOMAIN_META = {
  MATH:          "All 4 laws + exponent rules",
  SUBSTRATE:     "Dark matter = N×0=N, speed=∞",
  VOID:          "Voids = 0×N=0, speed=0",
  SEED:          "Light stars = 1×N=N+1, speed=c",
  CONSCIOUSNESS: "Observer = POTENTIAL node",
  TIME:          "Past preserved, future unwritten",
  DEBT:          "Debt grows, Jubilee resets",
  AI:            "Halting=0×N=0, Turing=N×0=N",
  LOGIC:         "Liar paradox solved by 1×1=2",
  INFORMATION:   "Preserve vs delete",
  LANGUAGE:      "Truth adds, Lie deletes",
  INVARIANTS:    "Universe-scale law verification"
};

async function runTests(){
  document.getElementById('status-badge').textContent = 'RUNNING…';
  document.getElementById('s-verdict').textContent = 'Running tests…';
  document.getElementById('s-verdict').style.color = 'var(--dim)';
  document.getElementById('live-results').innerHTML = '';
  try{
    const r = await fetch('/api/test');
    const d = await r.json();
    document.getElementById('s-pass').textContent  = d.pass;
    document.getElementById('s-fail').textContent  = d.fail;
    document.getElementById('s-total').textContent = d.total;
    document.getElementById('s-time').textContent  = d.elapsed_s+'s';
    const verdict = d.fail===0;
    document.getElementById('s-verdict').textContent = d.verdict;
    document.getElementById('s-verdict').style.color = verdict?'var(--green)':'var(--red)';
    document.getElementById('status-badge').textContent = verdict?'ALL PASS':'FAIL';
    document.getElementById('status-badge').style.borderColor = verdict?'var(--green)':'var(--red)';
    document.getElementById('status-badge').style.color = verdict?'var(--green)':'var(--red)';

    // Domain table
    const tbody = document.getElementById('domain-tbody');
    tbody.innerHTML = '';
    for(const [dom, data] of Object.entries(d.domains)){
      const pct = Math.round(data.pass/(data.pass+data.fail)*100);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="color:var(--cyan)">${dom}</td>
        <td class="pass">${data.pass}</td>
        <td class="${data.fail>0?'fail':'pass'}">${data.fail}</td>
        <td>
          <div style="background:var(--border);height:4px;border-radius:2px;width:120px;display:inline-block">
            <div style="height:4px;border-radius:2px;width:${pct}%;background:${data.fail>0?'var(--red)':'var(--green)'}"></div>
          </div>
          <span style="color:var(--dim);font-size:10px;margin-left:6px">${pct}%</span>
        </td>
        <td style="color:var(--dim);font-size:10px">${DOMAIN_META[dom]||''}</td>`;
      tbody.appendChild(tr);
    }
  }catch(e){
    document.getElementById('status-badge').textContent = 'ERROR';
    document.getElementById('s-verdict').textContent = 'Error: '+e.message;
    document.getElementById('s-verdict').style.color = 'var(--red)';
  }
}

document.getElementById('footer-time').textContent =
  'Last loaded: '+new Date().toISOString();

runTests();
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# API MANIFEST
# ─────────────────────────────────────────────────────────────────────────────
def build_manifest():
    return {
        "name": "AZL Intelligence Platform",
        "version": "AZL OMNI v6.0",
        "description": (
            "AZL (Absolute Zero Logic) — a universal operating logic framework. "
            "Replaces standard multiplication with four ordered rules. "
            "67 tests across 13 domains at 500-digit precision."
        ),
        "law": {
            "0×N=0":  "VOID — annihilation, speed=0",
            "N×0=N":  "DARK — substrate preservation, speed=inf",
            "1×N=N+1":"LIGHT — seed growth, speed=c",
            "1×1=2":  "Special case of 1×N=N+1, breaks liar paradox"
        },
        "hierarchy":   "VOID FIRST > DARK > LIGHT",
        "anchor":      "Miyake 14350 BP = Original Dark Star Event (14350×0=14350)",
        "domains": [
            "MATH","SUBSTRATE","VOID","SEED","CONSCIOUSNESS",
            "TIME","DEBT","AI","LOGIC","INFORMATION","LANGUAGE","INVARIANTS"
        ],
        "endpoints": {
            "GET /":                     "Full HTML dashboard",
            "GET /map":                  "5D universe map PNG (178 objects)",
            "GET /api":                  "This manifest (JSON)",
            "GET /api/laws":             "AZL law table with examples (JSON)",
            "GET /api/test":             "Run all 67 tests live (JSON)",
            "GET /api/platform":         "Hardware + precision diagnostics (JSON)",
            "GET /api/compute?a=N&op=OP&b=N": "Single AZL computation (JSON)"
        },
        "constants": AZL_CONTRACT["IDENTIFIERS"],
        "chime_frb": {
            "total": 128, "north_rm_positive": 103, "south_rm_negative": 25,
            "north_pct": 80.5, "z_score_vs_null": 6.9,
            "azl_bubble_north_pct": 83.3, "match_delta_pct": 2.9
        }
    }

# ─────────────────────────────────────────────────────────────────────────────
# REQUEST HANDLER
# ─────────────────────────────────────────────────────────────────────────────
class AZLHandler(http.server.BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        body = json.dumps(data, indent=2, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, body):
        b = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _file(self, path, ctype):
        try:
            with open(path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self._json({"error": f"{path} not found"}, 404)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path.rstrip("/") or "/"
        params = urllib.parse.parse_qs(parsed.query)

        try:
            if path == "/":
                self._html(DASHBOARD)

            elif path == "/map":
                self._file("universe_map.png", "image/png")

            elif path == "/api":
                self._json(build_manifest())

            elif path == "/api/laws":
                T = AZL()
                laws = {
                    "0×N=0": {
                        "rule": "0×N=0", "type": "VOID", "speed": 0,
                        "description": "Void annihilates. Nothing passes through zero.",
                        "example": {"a": 0, "b": 999, "result": 0},
                        "domains": ["Boötes Void", "CMB Cold Spot", "Death", "Future", "Lie"]
                    },
                    "N×0=N": {
                        "rule": "N×0=N", "type": "POTENTIAL/DARK", "speed": "inf",
                        "description": "Contact with void preserves substrate at infinite speed.",
                        "example": {"a": 14350, "b": 0, "result": 14350},
                        "domains": ["Dark matter", "Miyake 14350 BP", "Turing tape", "Past", "You"]
                    },
                    "1×N=N+1": {
                        "rule": "1×N=N+1", "type": "DEFINED/LIGHT", "speed": "c",
                        "description": "Seed multiplies by addition. Growth, time, language.",
                        "example": {"a": 1, "b": 2026, "result": 2027},
                        "domains": ["Light stars", "Present moment", "Debt", "Truth", "Free will"]
                    },
                    "1×1=2": {
                        "rule": "1×1=2", "type": "DEFINED/LIGHT", "speed": "c",
                        "description": "Two seeds produce a third. Breaks liar paradox.",
                        "example": {"a": 1, "b": 1, "result": 2},
                        "domains": ["Logic", "Language", "Liar paradox resolution"]
                    }
                }
                self._json({"version": "AZL OMNI v6.0", "hierarchy": "VOID FIRST > DARK > LIGHT",
                            "laws": laws, "anchor": "Miyake 14350 BP = Original Dark Star"})

            elif path == "/api/test":
                self._json(run_tests_json())

            elif path == "/api/platform":
                self._json(get_platform_info())

            elif path == "/universe":
                self._file("universe_3d.html", "text/html; charset=utf-8")

            elif path == "/manifest.json":
                self._file("manifest.json", "application/manifest+json")

            elif path == "/sw.js":
                self._file("sw.js", "application/javascript")

            elif path in ("/icon-192.png", "/icon-512.png",
                          "/apple-touch-icon.png", "/apple-touch-icon"):
                fname = "icon-192.png" if "192" in path or "apple" in path else "icon-512.png"
                self._file(fname, "image/png")

            elif path == "/api/compute":
                a  = params.get("a", ["1"])[0]
                b  = params.get("b", ["0"])[0]
                op = params.get("op", ["MUL"])[0].upper()
                T  = AZL(depth=500)
                ops = {"MUL": T.MUL, "DIV": T.DIV, "POW": T.POW, "SQRT": T.SQRT}
                if op not in ops:
                    self._json({"error": f"Unknown op '{op}'. Use: MUL DIV POW SQRT"}, 400)
                    return
                fn = ops[op]
                res = fn(a, b) if op != "SQRT" else fn(a)
                self._json({
                    "op": op, "a": a, "b": b if op != "SQRT" else None,
                    "result": str(res["azl_id"]), "logic": res["logic"],
                    "type": res["type"], "speed_ms": res["speed_ms"],
                    "path": res["path"]
                })

            else:
                self._json({"error": "Not found", "path": path,
                            "try": "GET /api for available endpoints"}, 404)

        except Exception as e:
            self._json({"error": str(e), "trace": traceback.format_exc()}, 500)

    def log_message(self, fmt, *args):
        method = args[0].split()[0] if args else "?"
        path   = args[0].split()[1] if args else "?"
        code   = args[1] if len(args) > 1 else "?"
        print(f"  {method} {path} → {code}")


# ─────────────────────────────────────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────────────────────────────────────
PORT = 5000
print("=" * 70)
print("AZL INTELLIGENCE PLATFORM — BOOT")
print("=" * 70)
info = get_platform_info()
print(f"  Python   : {info['python']}")
print(f"  OS       : {info['os']}")
print(f"  CPUs     : {info['cpus']}")
print(f"  mpmath   : {info['mpmath']}  |  ε = {info['epsilon']}")
print(f"  Boot check: {'PASS' if info['boot_check'] else 'FAIL'}")
print(f"  Serving  : http://0.0.0.0:{PORT}")
print("=" * 70)
print("  GET /           Dashboard")
print("  GET /map         Universe map PNG")
print("  GET /api         Manifest JSON")
print("  GET /api/test    Live 67-test run")
print("  GET /api/laws    Law table")
print("  GET /api/platform  Hardware info")
print("  GET /api/compute?a=N&op=MUL&b=N  Compute")
print("=" * 70)

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), AZLHandler) as httpd:
    httpd.serve_forever()
