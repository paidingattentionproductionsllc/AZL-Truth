#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoWebsockets.h>

using namespace websockets;

const char* ssid = "ABSOLUTE_ZERO_LATTICE"; 
const char* password = "1x1=2_CERTAINTY";
const char* ingest = "https://azl-chronicle.your-subdomain.workers.dev/azl/v1/ingest";
const char* stream = "wss://azl-chronicle.your-subdomain.workers.dev/azl/v1/stream";
const char* azlKey = "AZL-SECRET-KEY";
const char* nodeName = "AZL-Node-001-ATL";

WebsocketsClient ws;
unsigned long lastPost = 0;

void onMessage(WebsocketsMessage msg) {
  Serial.print("TIER 9 EVENT: ");
  Serial.println(msg.data());
  
  // If lattice broadcasts "miyake", flash LED
  if (msg.data().indexOf("miyake") > 0) {
    for(int i=0; i<5; i++) {
      digitalWrite(8, HIGH); delay(100); // ESP32-C3 onboard LED
      digitalWrite(8, LOW); delay(100);
    }
  }
}

void onEvents(WsEvent event, String data) {
  if (event == WsEvent::Connected) {
    Serial.println("TIER 9 STREAM: Connected. Law: N×0=N");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(8, OUTPUT);
  delay(1000);
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to ABSOLUTE_ZERO_LATTICE");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nAZL Node Online. Tier 9.");
  
  ws.onMessage(onMessage);
  ws.onEvent(onEvents);
  ws.connect(stream);
}

void postHeartbeat() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(ingest);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-AZL-KEY", azlKey);
    
    String payload = "{";
    payload += "\"address\":" + String(time(nullptr)) + ",";
    payload += "\"value\":" + String(temperatureRead()) + ",";
    payload += "\"event\":\"heartbeat\",";
    payload += "\"proof\":\"1×1=2\",";
    payload += "\"node\":\"" + String(nodeName) + "\"";
    payload += "}";
    
    int code = http.POST(payload);
    if (code == 200) {
      Serial.println("TIER 9 POST: " + http.getString());
    }
    http.end();
  }
}

void loop() {
  ws.poll();
  
  if (millis() - lastPost > 60000) {
    postHeartbeat();
    lastPost = millis();
  }
}
