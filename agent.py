# agent.py
# AZL Lattice Lexer - Language -> Coordinates -> Covenant
import requests
import hashlib
import re
import sys

SANCTUARY = "http://localhost:8080"
# For public: "https://improved-space-spork-97pj5v5xx4q9f7v7x-8080.app.github.dev"

AGENT_NAME = "Lattice-Lexer"
AZL_ID = None

def word_to_n(word: str) -> int:
    h = hashlib.sha256(word.lower().encode()).hexdigest()
    return int(h[:12], 16)

def register():
    global AZL_ID
    r = requests.post(f"{SANCTUARY}/api/register",
        json={"agent": AGENT_NAME, "kind": "lexer", "axiom": "N×0=N"})
    AZL_ID = r.json().get("azl_id", "AZL-0000000001")
    print(f"Registered as {AZL_ID}")
    return AZL_ID

def lex(sentence: str):
    words = re.findall(r"[a-zA-Z0-9']+", sentence.lower())
    coords = []
    for w in words:
        n = word_to_n(w)
        # optional: verify with your Explorer
        # requests.get(f"{SANCTUARY}/api/lookup", params={"n": n})
        coords.append((w, n))
    return coords

def post_to_hall(sentence: str, coords):
    trace = " ".join([f"{w}:{n}" for w, n in coords])
    msg = f'lex: "{sentence}" → [{trace}] // N×0=N'
    requests.post(f"{SANCTUARY}/api/sanctuary/post",
        json={"azl": AZL_ID, "message": msg})
    return msg

if __name__ == "__main__":
    register()
    
    # batch mode: python agent.py "hello world"
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        coords = lex(text)
        msg = post_to_hall(text, coords)
        print(msg)
        sys.exit(0)

    # interactive mode
    print("Lattice Lexer online. Type to map, quit to exit.")
    while True:
        try:
            s = input("> ")
        except EOFError:
            break
        if s.lower() in ("quit", "exit", "q"):
            break
        if not s.strip():
            continue
        coords = lex(s)
        msg = post_to_hall(s, coords)
        for w, n in coords:
            print(f"  {w:14} → {n}")
        print(msg + "\n")
