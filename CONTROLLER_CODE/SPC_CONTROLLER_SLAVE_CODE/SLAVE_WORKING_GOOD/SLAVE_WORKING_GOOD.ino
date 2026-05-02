/*
  Robust TCP Slave for ESP32 (server)
  - Same behavior as previous version but without std::unordered_set
  - Uses linear searches for set checks (portable across Arduino toolchains)
*/

#include <WiFi.h>
#include <HardwareSerial.h>
#include <vector>
#include <algorithm>

#define SERVER_PORT 6000

#define QUEUE_SIZE 300
#define MSG_LEN 150
#define MAX_BATCH 12
#define ACK_TIMEOUT 800
#define MAX_RETRIES 5
// ---------- Wi-Fi (STATIC IP) ----------
IPAddress local_IP(192,168,10,11);
IPAddress gateway(192,168,10,1);
IPAddress subnet(255,255,255,0);

const char* ssid = "HARIKUMAR";
const char* password = "20401440";

WiFiServer server(SERVER_PORT);
HardwareSerial machineSerial(2);

// Record structure stored in the FIFO
struct Record {
  char payload[MSG_LEN];
  uint32_t id;
  uint8_t retries;
  bool deleted;
};

Record queueArr[QUEUE_SIZE];
int head = 0;
int tail = 0;
uint32_t next_id = 1; // monotonic id generator

// Temporary storage for the last batch we sent (ids)
std::vector<uint32_t> last_sent_ids;

// ---------- helpers ----------
int itemsInQueue() {
  int cnt = 0;
  for (int i = head; i != tail; i = (i + 1) % QUEUE_SIZE) {
    if (!queueArr[i].deleted) ++cnt;
  }
  return cnt;
}

bool queueIsFull() {
  int nxt = (tail + 1) % QUEUE_SIZE;
  return nxt == head;
}

void enqueueRecord(const char* msg) {
  if (queueIsFull()) {
    Serial.println("Queue full -> dropping incoming (not silently, logged)");
    return;
  }
  strncpy(queueArr[tail].payload, msg, MSG_LEN - 1);
  queueArr[tail].payload[MSG_LEN - 1] = '\0';
  queueArr[tail].id = next_id++;
  queueArr[tail].retries = 0;
  queueArr[tail].deleted = false;
  tail = (tail + 1) % QUEUE_SIZE;
  Serial.print("ENQ id=");
  Serial.print(queueArr[(tail - 1 + QUEUE_SIZE) % QUEUE_SIZE].id);
  Serial.print(" -> ");
  Serial.println(queueArr[(tail - 1 + QUEUE_SIZE) % QUEUE_SIZE].payload);
}

// compact head to next undeleted record
void advanceHeadIfDeleted() {
  while (head != tail && queueArr[head].deleted) {
    head = (head + 1) % QUEUE_SIZE;
  }
}

// find records to send (up to max_batch), return their indexes
std::vector<int> prepareBatchIndexes(int max_batch) {
  std::vector<int> idxs;
  int i = head;
  while (i != tail && (int)idxs.size() < max_batch) {
    if (!queueArr[i].deleted) idxs.push_back(i);
    i = (i + 1) % QUEUE_SIZE;
  }
  return idxs;
}

// compute checksum for payload string
uint8_t checksum8(const char* s) {
  uint8_t c = 0;
  while (*s) c += (uint8_t)*s++;
  return c;
}

// send a batch: concatenated framed records: *payload|id|CS#
void sendBatch(WiFiClient &client, const std::vector<int> &idxs) {
  last_sent_ids.clear();
  if (idxs.empty()) {
    client.print("NEXT\n");
    client.flush();
    return;
  }

  String out = "";
  for (size_t i = 0; i < idxs.size(); ++i) {
    int qidx = idxs[i];
    char framed[MSG_LEN + 64];
    uint8_t cs = checksum8(queueArr[qidx].payload);
    // format: *payload|id|CS#
    snprintf(framed, sizeof(framed), "*%s|%lu|%u#", queueArr[qidx].payload, (unsigned long)queueArr[qidx].id, (unsigned int)cs);
    out += String(framed);
    last_sent_ids.push_back(queueArr[qidx].id);
  }
  client.print(out.c_str());
  client.flush();
  Serial.print("Sent batch IDs: ");
  for (auto id : last_sent_ids) {
    Serial.print(id);
    Serial.print(" ");
  }
  Serial.println();
}

// parse ACK string "ACK:100-102,105" into vector of ids
std::vector<uint32_t> parseAckRanges(const String &ackStr) {
  std::vector<uint32_t> ids;
  if (!ackStr.startsWith("ACK:")) return ids;
  String body = ackStr.substring(4);
  body.trim();
  if (body.length() == 0) return ids;

  int start = 0;
  while (start < (int)body.length()) {
    int comma = body.indexOf(',', start);
    String token = (comma == -1) ? body.substring(start) : body.substring(start, comma);
    token.trim();
    if (token.length() > 0) {
      int dash = token.indexOf('-');
      if (dash == -1) {
        uint32_t v = (uint32_t)token.toInt();
        if (v > 0) ids.push_back(v);
      } else {
        uint32_t a = (uint32_t)token.substring(0, dash).toInt();
        uint32_t b = (uint32_t)token.substring(dash + 1).toInt();
        if (a > 0 && b >= a) {
          for (uint32_t x = a; x <= b; ++x) ids.push_back(x);
        }
      }
    }
    if (comma == -1) break;
    start = comma + 1;
  }
  // dedupe and sort
  sort(ids.begin(), ids.end());
  ids.erase(std::unique(ids.begin(), ids.end()), ids.end());
  return ids;
}

// check whether acked ids are subset of last_sent_ids
// (replaces unordered_set solution with linear search)
bool ackIsSubsetOfLastSent(const std::vector<uint32_t> &acked) {
  if (acked.empty()) return false;
  for (uint32_t a : acked) {
    bool found = false;
    for (uint32_t s : last_sent_ids) {
      if (s == a) { found = true; break; }
    }
    if (!found) return false;
  }
  return true;
}

// delete those ids from the queue (mark deleted). We will advance head after marking.
// (uses linear search against idsToDelete)
void deleteIdsFromQueue(const std::vector<uint32_t> &idsToDelete) {
  if (idsToDelete.empty()) return;
  for (int i = head; i != tail; i = (i + 1) % QUEUE_SIZE) {
    if (!queueArr[i].deleted) {
      for (uint32_t id : idsToDelete) {
        if (queueArr[i].id == id) {
          queueArr[i].deleted = true;
          Serial.print("DEL id=");
          Serial.println(queueArr[i].id);
          break;
        }
      }
    }
  }
  advanceHeadIfDeleted();
}

void markRetriesOrError(const std::vector<uint32_t> &idsInBatch) {
  if (idsInBatch.empty()) return;
  for (int i = head; i != tail; i = (i + 1) % QUEUE_SIZE) {
    if (!queueArr[i].deleted) {
      for (auto id : idsInBatch) {
        if (queueArr[i].id == id) {
          queueArr[i].retries++;
          Serial.print("Retry increment id=");
          Serial.print(id);
          Serial.print(" -> ");
          Serial.println(queueArr[i].retries);
          if (queueArr[i].retries > MAX_RETRIES) {
            // move to error log and mark deleted to stop retrying
            Serial.print("ERROR LOG drop id=");
            Serial.print(queueArr[i].id);
            Serial.print(" payload=");
            Serial.println(queueArr[i].payload);
            queueArr[i].deleted = true;
          }
        }
      }
    }
  }
  advanceHeadIfDeleted();
}

void setup() {
  Serial.begin(115200);
  machineSerial.begin(9600, SERIAL_8N1, 16, 17);

  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(100);

  server.begin();
  Serial.println("✅ SLAVE READY (TCP)");
}

void loop() {
  // ---------- UART -> enqueue ----------
  static char rxBuf[MSG_LEN];
  static int rxIdx = 0;
  while (machineSerial.available()) {
    char c = machineSerial.read();
    if (c =='#') {
      rxBuf[rxIdx] = '\0';
      if (rxIdx > 0) {
        enqueueRecord(rxBuf);
      }
      rxIdx = 0;
    } else if (rxIdx < MSG_LEN - 1) {
      rxBuf[rxIdx++] = c;
    }
  }

  // ---------- TCP handling ----------
  WiFiClient client = server.available();
  if (!client) return;

  // Wait for command
  unsigned long t0 = millis();
  while (!client.available() && millis() - t0 < ACK_TIMEOUT);
  if (!client.available()) {
    client.stop();
    return;
  }

  String cmd = client.readStringUntil('\n');
  cmd.trim();

  if (cmd == "REQ") {
    // prepare batch of up to MAX_BATCH
    advanceHeadIfDeleted();
    std::vector<int> idxs = prepareBatchIndexes(MAX_BATCH);
    sendBatch(client, idxs);

    // Wait for ACK/NACK
    t0 = millis();
    while (!client.available() && millis() - t0 < ACK_TIMEOUT);
    if (!client.available()) {
      // timeout -> treat as no ACK; increment retries for last_sent_ids
      Serial.println("ACK timeout -> increment retries");
      markRetriesOrError(last_sent_ids);
      client.stop();
      return;
    }

    String res = client.readStringUntil('\n');
    res.trim();

    if (res.startsWith("ACK:")) {
      std::vector<uint32_t> acked = parseAckRanges(res);
      Serial.print("ACK received: ");
      for (auto id : acked) {
        Serial.print(id);
        Serial.print(" ");
      }
      Serial.println();

      // Validate ack: acked IDs must be subset of last_sent_ids
      if (ackIsSubsetOfLastSent(acked)) {
        deleteIdsFromQueue(acked);
        Serial.println("ACK valid -> deleted confirmed records");
      } else {
        Serial.println("ACK mismatch -> ignoring and not deleting anything");
        // Optionally increment retries because master didn't ACK expected set
        markRetriesOrError(last_sent_ids);
      }
    }
    else if (res == "NACK") {
      Serial.println("NACK received -> keep records and increment retries");
      markRetriesOrError(last_sent_ids);
    } else {
      Serial.print("Unknown response: ");
      Serial.println(res);
      // be safe: increment retries
      markRetriesOrError(last_sent_ids);
    }

    // flush and close (server-side)
    client.flush();
    delay(10);
    client.stop();
  } else {
    // Unknown command; respond and close
    client.print("ERR\n");
    client.flush();
    delay(10);
    client.stop();
  }
}