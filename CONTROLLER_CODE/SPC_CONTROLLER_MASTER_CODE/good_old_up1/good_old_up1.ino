/*
  ESP32 TCP Master (Dynamic IP + Protocol Fix)
  - Controlled via USB Serial (START, STOP, ADD_IP, DEL_IP, LIST_IP)
  - Stores Slave IPs in NVS (Preferences)
  - Protocol: Sends *payload# to PC (no DATA: prefix)
*/

#include <WiFi.h>
#include <vector>
#include <algorithm>
#include <Preferences.h>

#define SERVER_PORT 6000
#define BUF_SIZE    4096
#define TIMEOUT_MS  800
#define RECORD_MAX_LEN 256
#define MAX_SLAVES 10

// ---------- Wi‑Fi (STATIC IP) ----------
IPAddress local_IP(192,168,10,10);
IPAddress gateway(192,168,10,1);
IPAddress subnet(255,255,255,0);

const char* ssid = "HARIKUMAR";
const char* password = "20401440";

// ---------- DYNAMIC SLAVE IP LIST ----------
std::vector<String> slave_ips;
Preferences preferences;

// ---------- ID de-duplication ----------
const int RECENT_ID_CACHE = 64;
uint32_t last_processed_id = 0;
uint32_t recent_ids[RECENT_ID_CACHE];
int recent_put = 0;
int recent_count = 0;

enum MasterState {
  IDLE,
  RUNNING
};

MasterState masterState = IDLE; // default on power-on: IDLE

// Serial command buffer
String cmdBuffer = "";

// ---------- RSSI reporting timer ----------
unsigned long lastRssiReport = 0;


// ---------- helpers ----------
bool seenBefore(uint32_t id) {
  if (id <= last_processed_id) return true;
  for (int i = 0; i < recent_count; ++i) {
    int idx = (recent_put - 1 - i + RECENT_ID_CACHE) % RECENT_ID_CACHE;
    if (recent_ids[idx] == id) return true;
  }
  return false;
}

void markSeen(uint32_t id) {
  if (id > last_processed_id) last_processed_id = id;
  recent_ids[recent_put] = id;
  recent_put = (recent_put + 1) % RECENT_ID_CACHE;
  if (recent_count < RECENT_ID_CACHE) ++recent_count;
}

// checksum: same as slave
uint8_t checksum8(const char* s) {
  uint8_t c = 0;
  while (*s) c += (uint8_t)*s++;
  return c;
}

// build comma-separated ranges from sorted unique vector<uint32_t>
String buildRanges(const std::vector<uint32_t> &ids) {
  if (ids.empty()) return String();

  String out = "";
  uint32_t start = ids[0];
  uint32_t prev  = ids[0];

  for (size_t i = 1; i < ids.size(); ++i) {
    uint32_t v = ids[i];
    if (v == prev + 1) {
      prev = v;
      continue;
    } else {
      if (start == prev) {
        out += String(start);
      } else {
        out += String(start) + "-" + String(prev);
      }
      out += ",";
      start = prev = v;
    }
  }
  if (start == prev) out += String(start);
  else out += String(start) + "-" + String(prev);
  return out;
}

// Parse a single framed record that starts at recStart (pointer to first char after '*')
// Expected format inside: payload|id|CS  (no surrounding '*' or '#')
bool parseRecord(const char* recStart, int recLen, String &payloadOut, uint32_t &idOut) {
  if (recLen <= 0) return false;
  if (recLen >= RECORD_MAX_LEN) return false;

  char tmp[RECORD_MAX_LEN];
  memcpy(tmp, recStart, recLen);
  tmp[recLen] = '\0';

  char *sep1 = strrchr(tmp, '|'); // last separator before CS
  if (!sep1) return false;
  *sep1 = '\0';
  char *sep2 = strrchr(tmp, '|'); // separator before ID
  if (!sep2) return false;

  char *payload = tmp;
  char *idstr    = sep2 + 1;
  char *csstr    = sep1 + 1;
  *sep2 = '\0';

  char *endptr = nullptr;
  unsigned long idval = strtoul(idstr, &endptr, 10);
  if (idval == 0 && idstr == endptr) return false;

  uint8_t rx_cs = 0;
  bool hexMode = false;
  for (char *p = csstr; *p; ++p) {
    if ((*p >= 'A' && *p <= 'F') || (*p >= 'a' && *p <= 'f')) { hexMode = true; break; }
  }
  if (hexMode) rx_cs = (uint8_t)strtoul(csstr, NULL, 16);
  else rx_cs = (uint8_t)strtoul(csstr, NULL, 10);

  uint8_t calc = checksum8(payload);
  if (calc != rx_cs) return false;

  payloadOut = String(payload);
  idOut = (uint32_t)idval;
  return true;
}

// ---------------- IP Management ----------------
void loadIPs() {
    slave_ips.clear();
    String saved = preferences.getString("ips", "");
    if (saved.length() == 0) return;
    
    int start = 0;
    bool needsSave = false;
    while (true) {
        int comma = saved.indexOf(',', start);
        String ip = (comma == -1) ? saved.substring(start) : saved.substring(start, comma);
        ip.trim();
        if (ip.length() > 0) {
            IPAddress tempIP;
            if (tempIP.fromString(ip)) {
                slave_ips.push_back(ip);
            } else {
                needsSave = true; // Found garbage fragment
            }
        }
        if (comma == -1) break;
        start = comma + 1;
    }
    
    if (needsSave) {
        saveIPs(); // Clear out bad segments immediately
    } else {
        Serial.print("LOADED IPs: ");
        Serial.println(saved);
    }
}

void saveIPs() {
    String out = "";
    for (size_t i = 0; i < slave_ips.size(); i++) {
        out += slave_ips[i];
        if (i < slave_ips.size() - 1) out += ",";
    }
    preferences.putString("ips", out);
    Serial.print("SAVED IPs: ");
    Serial.println(out);
}

void addIP(String ip) {
    // Validate IP format
    IPAddress targetIP;
    if (!targetIP.fromString(ip)) {
        Serial.println("ERR: INVALID IP FORMAT");
        return;
    }
    
    // Check dupe
    for (const auto &s : slave_ips) {
        if (s == ip) {
            Serial.println("IP ALREADY EXISTS");
            return;
        }
    }
    if (slave_ips.size() >= MAX_SLAVES) {
        Serial.println("MAX SLAVES REACHED");
        return;
    }
    
    slave_ips.push_back(ip);
    saveIPs();
    Serial.print("IP ADDED: ");
    Serial.println(ip);
}

void delIP(String ip) {
    for (auto it = slave_ips.begin(); it != slave_ips.end(); ) {
        if (*it == ip) {
            it = slave_ips.erase(it);
            saveIPs();
            Serial.print("IP REMOVED: ");
            Serial.println(ip);
            return;
        } else {
            ++it;
        }
    }
    Serial.println("IP NOT FOUND");
}

// ---------------- Serial command handling ----------------
void handleSerialInput() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue; // ignore CR
    if (c == '\n') {
      String cmdLine = cmdBuffer;
      cmdLine.trim();

      String cmd = cmdLine;
      String arg = "";
      int space = cmdLine.indexOf(' ');
      if (space != -1) {
          cmd = cmdLine.substring(0, space);
          arg = cmdLine.substring(space + 1);
          arg.trim();
      }
      cmd.toUpperCase();

      if (cmd == "START") {
        if (masterState != RUNNING) {
          masterState = RUNNING;
          Serial.println("CMD START RECEIVED");
          Serial.println("STATE: RUNNING");
        } else {
          Serial.println("CMD START RECEIVED (already RUNNING)");
        }
      } else if (cmd == "STOP") {
        if (masterState != IDLE) {
          masterState = IDLE;
          Serial.println("CMD STOP RECEIVED");
          Serial.println("STATE: IDLE");
        } else {
          Serial.println("CMD STOP RECEIVED (already IDLE)");
        }
      } else if (cmd == "ADD_IP") {
          if (arg.length() > 0) addIP(arg);
          else Serial.println("ERR: Missing IP arg");
      } else if (cmd == "DEL_IP") {
          if (arg.length() > 0) delIP(arg);
          else Serial.println("ERR: Missing IP arg");
      } else if (cmd == "LIST_IP") {
          Serial.print("COUNT: "); Serial.println(slave_ips.size());
          for (const auto &ip : slave_ips) Serial.println(ip);
      } else if (cmd == "CLEAR_IP") {
          slave_ips.clear();
          saveIPs();
          Serial.println("ALL IPs CLEARED");
      } else if (cmd == "STATUS") {
        Serial.print("STATE: ");
        Serial.println(masterState == RUNNING ? "RUNNING" : "IDLE");
      } else if (cmd.length() > 0) {
        Serial.print("Unknown command: ");
        Serial.println(cmd);
      }
      cmdBuffer = "";
    } else {
      cmdBuffer += c;
      // guard max length
      if (cmdBuffer.length() > 128) cmdBuffer = cmdBuffer.substring(cmdBuffer.length() - 128);
    }
  }
}

// ---------------- Main setup/loop ----------------
void setup() {
  Serial.begin(115200);

  // Init NVS
  preferences.begin("master_config", false);
  loadIPs();

  masterState = IDLE;
  Serial.println("MASTER POWERED: STATE: IDLE");
  
  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(100);
  Serial.println("WiFi connected");
}

// Utility: stop and close client gracefully
void closeClientGracefully(WiFiClient &client) {
  if (client) {
    client.flush();
    delay(10);
    client.stop();
  }
}

void loop() {
  // --- Non-blocking RSSI report every 3 seconds ---
  if (millis() - lastRssiReport >= 3000) {
    lastRssiReport = millis();
    if (WiFi.status() == WL_CONNECTED) {
      Serial.print("RSSI:");
      Serial.println(WiFi.RSSI());
    } else {
      Serial.println("RSSI:DISC");
    }
  }

  // Always handle serial commands immediately
  handleSerialInput();


  // If not RUNNING, skip contacting slaves
  if (masterState != RUNNING) {
    delay(50); // avoid tight loop while idle
    return;
  }
  
  if (slave_ips.empty()) {
      // No slaves configured
      delay(1000);
      return;
  }

  // RUNNING: poll slaves (but check masterState in between to allow immediate STOP)
  for (int s = 0; s < slave_ips.size(); s++) {
    // If STOP was received while iterating, break out immediately
    if (masterState != RUNNING) break;

    IPAddress targetIP;
    if (!targetIP.fromString(slave_ips[s])) {
        Serial.print("Invalid IP stored: ");
        Serial.println(slave_ips[s]);
        continue;
    }

    WiFiClient client;
    if (!client.connect(targetIP, SERVER_PORT)) {
      Serial.print("WARN: cannot connect to slave ");
      Serial.println(slave_ips[s]);
      continue;
    }

    // Before sending REQ, check if STOP arrived
    if (masterState != RUNNING) {
      closeClientGracefully(client);
      break;
    }

    client.write("REQ\n");

    char buf[BUF_SIZE];
    int idx = 0;
    unsigned long t0 = millis();

    // Read loop
    while (millis() - t0 < TIMEOUT_MS && idx < BUF_SIZE - 1) {
      if (masterState != RUNNING) {
        Serial.println("STOP received during read -> closing connection");
        closeClientGracefully(client);
        break;
      }
      while (client.available() && idx < BUF_SIZE - 1) {
        buf[idx++] = client.read();
      }
      delay(0);
    }

    if (masterState != RUNNING) {
      continue;
    }

    buf[idx] = '\0';
    if (idx == 0) {
      closeClientGracefully(client);
      continue;
    }

    // Parse all complete framed records: * ... #
    std::vector<uint32_t> processed_ids; 
    int i = 0;
    while (i < idx) {
      char *startp = strchr(buf + i, '*');
      if (!startp) break;
      int spos = startp - buf;
      char *endp = strchr(startp, '#');
      if (!endp) {
        break;
      }
      int epos = endp - buf;

      char *recStart = startp + 1;
      int recLen = epos - (spos + 1);

      String payload;
      uint32_t id = 0;
      bool ok = parseRecord(recStart, recLen, payload, id);
      if (!ok) {
        Serial.print("WARN master: skipping bad record");
        i = epos + 1;
        continue;
      }

      // dedup check
      if (seenBefore(id)) {
        i = epos + 1;
        continue;
      }

      if (masterState == RUNNING) {
        // CORRECT PROTOCOL: *...# (No "DATA:" prefix)
        // Ensure format is valid
        if (!payload.startsWith("*")) payload = "*" + payload;
        if (!payload.endsWith("#")) payload = payload + "#";
        
        Serial.println(payload);
      } else {
        break;
      }

      markSeen(id);
      processed_ids.push_back(id);

      i = epos + 1;
    }

    if (masterState != RUNNING) {
      closeClientGracefully(client);
      break;
    }

    // Send explicit ACK
    if (!processed_ids.empty()) {
      std::sort(processed_ids.begin(), processed_ids.end());
      processed_ids.erase(std::unique(processed_ids.begin(), processed_ids.end()), processed_ids.end());
      String ranges = buildRanges(processed_ids);
      String ack = "ACK:" + ranges + "\n";
      client.print(ack);
      client.flush();
      delay(10);
      Serial.print("Sent -> ");
      Serial.print(ack);
    } else {
      client.print("NACK\n");
      client.flush();
      delay(10);
      Serial.println("Sent -> NACK");
    }

    closeClientGracefully(client);

    for (int wait = 0; wait < 20; wait += 5) {
      handleSerialInput(); 
      if (masterState != RUNNING) break;
      delay(5);
    }
  } // end for slaves
}