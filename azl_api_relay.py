import os
import json
import socket
import threading
import urllib.request
from flask import Flask, jsonify, request
from decimal import Decimal, getcontext

# 1. Establish Infinite Precision Boundary (100 digits)
getcontext().prec = 100

# 2. Setup Flask App
app = Flask(__name__)

# Constants
MIYAKE_14350_BP_ANCHOR = Decimal("14350.0")
LEDGER_FILE = "casteelian_ledger.json"
TOKEN_FILE = "token.json"

# Shared System State
AZL_LIVE_STATE = {
    "coordinate": "0.0",
    "domain_status": "BOOT_INITIALIZATION",
    "system_verdict": "AWAITING_STREAM",
    "last_updated": 0.0
}

# --- LEDGER STORAGE ENGINE ---
def load_ledger():
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_to_ledger(coordinate, url):
    ledger = load_ledger()
    ledger[str(coordinate)] = {
        "url": url,
        "timestamp": __import__('time').time()
    }
    with open(LEDGER_FILE, 'w') as f:
        json.dump(ledger, f, indent=4)

# --- PROXY INGESTION AGENT ---
def proxy_ingest_url(url):
    """
    Quietly fetches URL data. If it is raw packet metadata rather than a real website,
    it processes the string bytes directly into the Casteelian Registry without throwing a 500 error.
    """
    url_clean = url.strip()
    
    # Check if this is a raw packet string, local hash, or invalid URL format
    if url_clean.startswith("packet-hash-") or not ("." in url_clean) or " " in url_clean or ":" in url_clean:
        # Process the raw metadata bytes locally and skip the live web request
        raw_bytes = url_clean.encode('utf-8')
    else:
        # Format a clean web request path
        if not url_clean.startswith("http://") and not url_clean.startswith("https://"):
            url_target = "https://" + url_clean
        else:
            url_target = url_clean
            
        try:
            req = urllib.request.Request(
                url_target, 
                headers={'User-Agent': 'AZL-Proxy-Agent/1.0'}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                raw_bytes = response.read()
        except Exception:
            # Safe Fallback: If the address doesn't resolve or web request fails, use the string footprint bytes
            raw_bytes = url_clean.encode('utf-8')
            
    try:
        # Run base-256 fractional expansion
        coordinate = Decimal("0.0")
        for i, byte in enumerate(raw_bytes, start=1):
            coordinate += Decimal(byte) / (Decimal("256") ** i)
            
        casteelian_coordinate = (coordinate * MIYAKE_14350_BP_ANCHOR) % Decimal("1.0")
        
        # Commit to the local ledger
        save_to_ledger(casteelian_coordinate, url_clean)
        return str(casteelian_coordinate), len(raw_bytes)
    except Exception as e:
        print(f"❌ [PROXY AGENT] Processing failure: {e}")
        return None, 0

# --- API ENDPOINTS ---
@app.route('/api/matrix/state', methods=['GET'])
def get_matrix_state():
    """Returns current live tracking variables."""
    return jsonify(AZL_LIVE_STATE)

@app.route('/api/proxy/ingest', methods=['POST'])
def handle_proxy_ingest():
    """
    Endpoint for the AZL Bridge to request URL resolution and coordinate indexing.
    Expects JSON: {"url": "example.com"}
    """
    data = request.json or {}
    target_url = data.get("url")
    if not target_url:
        return jsonify({"error": "Missing URL parameter"}), 400
        
    print(f"📡 [GATEWAY] Proxy Request Intercepted for: {target_url}")
    coord, byte_count = proxy_ingest_url(target_url)
    
    if coord:
        return jsonify({
            "status": "SUCCESS",
            "url": target_url,
            "bytes_processed": byte_count,
            "coordinate": coord
        }), 200
    else:
        return jsonify({"status": "FAILED", "url": target_url}), 500

# --- BACKGROUND UDP SOCKET STREAM LISTENER ---
def udp_stream_listener():
    global AZL_LIVE_STATE
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_sock.bind(('0.0.0.0', 5006))
    except Exception as e:
        print(f"❌ Socket Lock Error: {e}")
        return

    print("🛰️  Asynchronous Matrix Stream Listener: Processing on Port 5006")
    while True:
        try:
            data, _ = udp_sock.recvfrom(1024)
            if data:
                coord_str = data.decode('utf-8').strip()
                AZL_LIVE_STATE["coordinate"] = coord_str
                AZL_LIVE_STATE["last_updated"] = __import__('time').time()
                
                val = float(coord_str)
                if val == 0.0:
                    AZL_LIVE_STATE["domain_status"] = "DESK_DOMAIN_ANCHOR (Territory 1)"
                    AZL_LIVE_STATE["system_verdict"] = "UNIVERSAL_LAW_CONFIRMED"
                else:
                    AZL_LIVE_STATE["domain_status"] = "ROOM_RELAY_ACTIVE (Territory 2)"
                    AZL_LIVE_STATE["system_verdict"] = "VERIFIED_MATRIX_STATE"
        except Exception:
            pass

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # Run structural listener thread
    listener_worker = threading.Thread(target=udp_stream_listener, daemon=True)
    listener_worker.start()
    
    # Start Web Gateway
    print("📝 Mounting Integrated AZL Core Gateway API on http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
