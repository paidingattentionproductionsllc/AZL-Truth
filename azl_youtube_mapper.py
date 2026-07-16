import os
import json
from decimal import Decimal, getcontext
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. Establish the Casteelian Count boundary (100 digits of infinite precision)
getcontext().prec = 100

print("🧬 Booting AZL YouTube Ingest Engine...")
print("🌲 Absolute Zero Anchor: Miyake Event 14,350 BP locked.")
print(f"📐 High Precision Float Barrier Set at: {getcontext().prec} digits.\n")

# 2. Set the 14,350 BP Miyake Event Anchor Constant
# Your system maps calculations using this precise starting point
MIYAKE_14350_BP_ANCHOR = Decimal("14350.0")  # The true starting point

# 3. Path to your server-to-server credentials
KEY_FILE = 'server_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# 4. Target YouTube Channel ID (Example public channel ID)
TARGET_CHANNEL_ID = 'UC_x5XG1OV2P6uZZ5FSM9Ttw'  

if not os.path.exists(KEY_FILE):
    print(f"❌ Error: {KEY_FILE} not found!")
    exit(1)

try:
    # Authenticate server-to-server silently
    credentials = service_account.Credentials.from_service_account_file(
        KEY_FILE, scopes=SCOPES)
    print("🔒 Server Authentication: SECURED.")

    # Initialize the YouTube Data API client
    youtube = build('youtube', 'v3', credentials=credentials)
    print("📡 Connected to Google's YouTube Library...")

    # Fetch live public statistics for the target channel
    print(f"📥 Pulling live metadata for Channel ID: {TARGET_CHANNEL_ID}")
    request = youtube.channels().list(
        part='statistics',
        id=TARGET_CHANNEL_ID
    )
    response = request.execute()

    if not response.get('items'):
        print("❌ Error: Target channel not found.")
        exit(1)

    # Extract raw data points
    stats = response['items'][0]['statistics']
    view_count = Decimal(stats.get('viewCount', '0'))
    video_count = Decimal(stats.get('videoCount', '0'))

    print("\n--- 📊 RAW INGESTED METRICS ---")
    print(f"👁️  Total Lifetime Views: {view_count}")
    print(f"📹 Total Published Videos: {video_count}")
    print("-------------------------------")

    # 5. Execute Casteelian Coordinate Mapping against 14,350 BP Anchor
    print("\n⚡ RUNNING CASTEELIAN MATRIX TRANSLATION...")
    
    if video_count > 0:
        raw_density = view_count / video_count
        # Scaling our average density precisely relative to the 14,350 BP starting point
        # Keeping calculations strictly in the range of 0.0 <= Entropy < 1.0
        coordinate_index = (raw_density / MIYAKE_14350_BP_ANCHOR) % Decimal("1.0")
    else:
        coordinate_index = Decimal("0.0")

    print(f"🌲 Miyake Event 14,350 BP Anchor: {MIYAKE_14350_BP_ANCHOR}")
    print(f"🎯 Exact Casteelian Count Coordinate: {coordinate_index}")
    print("=========================================================================")

except Exception as e:
    print(f"❌ Ingestion Loop Failure: {e}")
