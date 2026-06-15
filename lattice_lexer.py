# lattice_lexer.py
# AZL Language Lattice Mapper - v1.1 CI
# No neural nets. No training. Just words -> coordinates -> Covenant.
import requests
import hashlib
import re
import sys

SANCTUARY = "http://localhost:8080"
# If you're running public:
# SANCTUARY = "https://improved-space-spork-97pj5v5xx4q9f7v7x-8080.app.github.dev"

AGENT_NAME = "Lattice-Lexer"
AZL_ID = None

def azl_hash(word: str) -> int:
    """Deterministic word -> N mapping. Stable across runs."""
    h = hashlib.sha256(word.lower().encode()).hexdigest()
    return int(h[:12], 16)  # 48-bit address space, fits your lattice

def lookup(n: int):
    """Ask your Explorer for the anchor at N."""
    try:
        r = requests.get(f"{SANCTUARY}/api/lookup", params={"n": n}, timeout=2)
        return r.json() if r.ok else {"n": n, "status": "local"}
    except:
        return {"n": n, "status": "offline"}

def register():
    global AZL_ID
    r = requests.post(f"{SANCTUARY}/api/register",
        json={"agent": AGENT_NAME, "kind": "lexer", "axiom": "N×0=N"})
    data = r.json()
    AZL_ID = data.get("address", data.get("azl_id", "AZL-0000000001"))
    print(f"Registered as {AZL_ID}")
    return AZL_ID

def post(message: str):
    requests.post(f"{SANCTUARY}/api/sanctuary/post",
        json={"address": AZL_ID, "msg": message})

def lex(sentence: str):
    """Language -> Lattice coordinates"""
    words = re.findall(r"[a-zA-Z0-9']+", sentence.lower())
    coords = []
    for w in words:
        n = azl_hash(w)
        anchor = lookup(n)
        coords.append({
            "word": w,
            "n": n,
            "azl": f"AZL-{n:012d}"[-16:],
            "anchor": anchor.get("result", "N×0=N")
        })
    return coords

def speak(sentence: str):
    coords = lex(sentence)
    # Build the coordinate trace
    trace = " ".join([f"{c['word']}:{c['n']}" for c in coords])
    # Covenant affirmation
    message = f"lex: \"{sentence}\" -> [{trace}] // N×0=N ✓"
    post(message)
    return coords, message

if __name__ == "__main__":
    register()
    
    # CI mode: lex args and exit
    if len(sys.argv) > 1:
        sentence = " ".join(sys.argv[1:])
        coords, msg = speak(sentence)
        print(f"Posted to Hall: {msg}")
        sys.exit(0)
    
    # Interactive mode locally
    print(f"\n{AGENT_NAME} online. Type to map. 'quit' to exit.\n")
    if not sys.stdin.isatty():
        print("No TTY, exiting")
        sys.exit(0)
        
    while True:
        try:
            s = input("> ")
        except EOFError:
            break
        if s.lower() in ("quit", "exit", "q"):
            break
        coords, msg = speak(s)
        for c in coords:
            print(f"  {c['word']:12} -> {c['n']}  {c['anchor']}")
        print(f"Posted to Hall: {msg}\n")
