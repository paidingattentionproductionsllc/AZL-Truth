import socket
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so your web domains can query this API directly from a browser
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Live Global System Registry
AZL_LIVE_STATE = {
    "coordinate": "1.0000",
    "domain_status": "PENDING",
    "last_updated": 0.0,
    "system_verdict": "INITIALIZING"
}

def udp_stream_listener():
    """Background worker that continuously ingests matrix updates from port 5006"""
    global AZL_LIVE_STATE
    
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind to localhost loopback so it catches local machine broadcasts safely
    try:
        udp_sock.bind(('127.0.0.1', 5006))
    except Exception as e:
        print(f"❌ UDP Bind Error: {e}. Make sure port 5006 is open.")
        return

    print("📡 Flask Background Listener: Active on UDP Port 5006.")
    
    while True:
        try:
            data, _ = udp_sock.recvfrom(1024)
            if data:
                coord_str = data.decode('utf-8').strip()
                # Dynamically update the system registry based on incoming metrics
                AZL_LIVE_STATE["coordinate"] = coord_str
                AZL_LIVE_STATE["last_updated"] = request_time = threading.time() if hasattr(threading, 'time') else __import__('time').time()
                
                # Assign structural domain mapping based on logic parameters
                val = float(coord_str)
                if val == 0.0:
                    AZL_LIVE_STATE["domain_status"] = "DESK_DOMAIN_ANCHOR (Territory 1)"
                    AZL_LIVE_STATE["system_verdict"] = "UNIVERSAL_LAW_CONFIRMED"
                elif val >= 0.5:
                    AZL_LIVE_STATE["domain_status"] = "ROOM_RELAY_ACTIVE (Territory 2)"
                    AZL_LIVE_STATE["system_verdict"] = "VERIFIED_MATRIX_STATE"
                else:
                    AZL_LIVE_STATE["domain_status"] = "PROCESSING"
                    AZL_LIVE_STATE["system_verdict"] = "CALCULATING"
                    
        except Exception as err:
            print(f"⚠️ Listener warning: {err}")

# --- REST API ENDPOINTS ---

@app.route('/api/matrix/state', methods=['GET'])
def get_matrix_state():
    """Exposes the live verification coordinate metrics to external web requests"""
    return jsonify({
        "status": "success",
        "data": AZL_LIVE_STATE
    }), 200

@app.route('/api/health', methods=['GET'])
def system_health():
    """Simple up-time monitoring node"""
    return jsonify({"status": "online", "engine": "AZL OMNI API RELAY"}), 200

if __name__ == "__main__":
    # Spin up the background UDP receiver thread before mounting the web server
    listener_worker = threading.Thread(target=udp_stream_listener, daemon=True)
    listener_worker.start()
    
    # Run the Flask web application server locally on port 8080
    print("🚀 Mounting AZL Data Access API Layer on http://127.0.0.1:8080")
    app.run(host='127.0.0.1', port=8080, debug=False)
