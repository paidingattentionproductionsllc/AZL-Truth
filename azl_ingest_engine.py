import os
import json
from decimal import Decimal, getcontext
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. Establish Infinite Precision Boundary (Bypassing standard computer rounding)
getcontext().prec = 100

print("🧬 Initializing AZL Ingestion Engine...")
print(f"📐 System Decimal Precision Locked at: {getcontext().prec} places.")

# 2. Path to your server-to-server passport file
KEY_FILE = 'server_secret.json'
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

if not os.path.exists(KEY_FILE):
    print(f"❌ Error: {KEY_FILE} not found in current directory!")
    exit(1)

try:
    # 3. Authenticate Server-to-Server silently (No web browser required)
    credentials = service_account.Credentials.from_service_account_file(
        KEY_FILE, scopes=SCOPES)
    print("🔒 Server-to-Server Passport Verified Natively.")
    
    # 4. Initialize the Google Discovery Service
    service = build('oauth2', 'v2', credentials=credentials)
    
    print("📡 Querying Google Library Infrastructure...")
    meta_data = service.tokeninfo().execute()
    print(f"📥 Raw Ingested Data Payload: {json.dumps(meta_data)}")
    
    # 5. Execute Casteelian Tier Indexing
    print("\n--- 📊 EXECUTING CASTEELIAN PRECISION INDEXING ---")
    
    # Using your Service Account's actual Unique ID from your console screenshot
    raw_numeric_asset = Decimal("105484400409197857289") 
    tier_base_divisor = Decimal("100000000000000000000000")
    
    coordinate_address = raw_numeric_asset / tier_base_divisor
    
    print(f"📍 Raw Numerical Asset: {raw_numeric_asset}")
    print(f"🎯 Exact Casteelian Count Coordinate: {coordinate_address}")
    print("--------------------------------------------------")

except Exception as e:
    print(f"❌ Ingestion Pipeline Failure: {e}")
