/*
  KC868-A6: DMX OR sACN (E1.31 multicast) input -> relay outputs 1-6 via PCF8574 + OLED status

  - Select input method at compile time using #defines below.
  - Active input populates a custom dmx_frame_t (512 channel values, valid flag, timestamps, etc.)
  - Channels 1-6: value > 127 => relay ON, else OFF
  - Relays driven via PCF8574 @ 0x24 (active-low typical on KC868)
  - OLED: SSD1306 128x64 using U8g2 HW I2C

  Libraries:
    - U8g2
    - forkineye/ESPAsyncE131 (only if USE_SACN_INPUT=1)
    - someweisguy/esp_dmx (only if USE_DMX_INPUT=1)
*/

#include <Arduino.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <Button2.h>
#include <Preferences.h>

// ========================== Compile-time selection ==========================
#define USE_DMX_INPUT   1
#define USE_SACN_INPUT  0

#if (USE_DMX_INPUT + USE_SACN_INPUT) != 1
  #error "Select exactly one input method: set USE_DMX_INPUT or USE_SACN_INPUT to 1 (but not both)."
#endif

// ========================== User config (sACN) ==============================
#if USE_SACN_INPUT
  #include <WiFi.h>
  #include <ESPAsyncE131.h>

  static const char* WIFI_SSID = "vodafone1236D8";
  static const char* WIFI_PASS = "q3TGpAbgHL7KaYsp";

  static constexpr uint16_t SACN_UNIVERSE = 1;     // multicast universe to listen on
  static constexpr uint8_t  SACN_SLOTS    = 2;     // ring buffer slots (2-4 recommended)
  ESPAsyncE131 e131(SACN_SLOTS);
#endif

// ========================== User config (DMX) ===============================
#if USE_DMX_INPUT
  extern "C" {
    #include "esp_dmx.h"
  }
  static constexpr dmx_port_t DMX_PORT = DMX_NUM_1;
#endif

// ========================== KC868-A6 hardware ==============================
static constexpr int I2C_SDA_PIN = 4;
static constexpr int I2C_SCL_PIN = 15;

// RS485 pins on KC868-A6
static constexpr int RS485_TX_PIN = 27;
static constexpr int RS485_RX_PIN = 14;

// PCF8574 controlling relays
static constexpr uint8_t PCF8574_ADDR = 0x24;
static constexpr uint8_t RELAY_COUNT  = 6;
static constexpr bool RELAYS_ACTIVE_LOW = true;

// OLED
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
// S2 Button
Button2 btn(0);
Preferences prefs;
static uint16_t startAddr = 1;
static bool cfgMode = false;
// ========================== DMX frame struct ===============================
struct dmx_frame_t {
  uint8_t  ch[512];         // DMX channels 1..512
  uint32_t last_update_ms;  // millis() of last frame received
  uint32_t frames_rx;       // total frames received since boot
};

static dmx_frame_t g_frame = { {0}, 0, 0 };

// Loss-of-signal: consider input OK if updated within this time
#if USE_DMX_INPUT
static constexpr uint32_t INPUT_OK_WINDOW_MS = 1500;
#elif USE_SACN_INPUT
static constexpr uint32_t INPUT_OK_WINDOW_MS = 3500; // >2.5s to tolerate jitter
#endif


// ========================== PCF8574 / relays ===============================
static uint8_t pcf_out = 0xFF; // default HIGH on all pins (relays off if active-low)
static bool relay_state[RELAY_COUNT] = {false,false,false,false,false,false};

bool pcfWrite(uint8_t value) {
  Wire.beginTransmission(PCF8574_ADDR);
  Wire.write(value);
  return (Wire.endTransmission() == 0);
}

void setRelay(uint8_t relayIndex1to6, bool on) {
  if (relayIndex1to6 < 1 || relayIndex1to6 > RELAY_COUNT) return;

  uint8_t idx = relayIndex1to6 - 1;
  relay_state[idx] = on;

  uint8_t bit = idx; // relays 1..6 => P0..P5
  bool pinLevel = RELAYS_ACTIVE_LOW ? !on : on; // active-low: ON=0

  if (pinLevel) pcf_out |=  (1u << bit);
  else          pcf_out &= ~(1u << bit);

  pcfWrite(pcf_out);
}

void allRelaysOff() {
  for (uint8_t i = 1; i <= RELAY_COUNT; i++) setRelay(i, false);
}

// ========================== OLED status ====================================
static uint32_t pps = 0;
static uint32_t last_pps_calc_ms = 0;
static uint32_t frames_at_last_calc = 0;

void drawStatus(bool link_ok, uint32_t age_ms) {
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_6x12_tf);

  // Line 1: input type + link
  u8g2.setCursor(0, 12);
#if USE_DMX_INPUT
  u8g2.print("DMX ");
#else
  u8g2.print("sACN:");
  u8g2.print(SACN_UNIVERSE);
  u8g2.print(" ");
#endif
  u8g2.print(link_ok ? "OK" : "NO");

  // Line 2: extra info (IP for sACN; RX pin for DMX)
  u8g2.setCursor(64, 12);
  u8g2.print("Addr: ");
  u8g2.print(startAddr);

  // Line 2: extra info (IP for sACN; RX pin for DMX)
  u8g2.setCursor(0, 26);
#if USE_SACN_INPUT
  u8g2.print("IP:");
  u8g2.print(WiFi.localIP());
#else
  u8g2.print("RX:");
  u8g2.print(RS485_RX_PIN);
  u8g2.print(" TX:");
  u8g2.print(RS485_TX_PIN);
#endif

  // Line 3: Age + PPS
  u8g2.setCursor(0, 40);
  u8g2.print("Age:");
  u8g2.print(age_ms);
  u8g2.print("ms PPS:");
  u8g2.print(pps);

  // Line 4: relay bits
  u8g2.setCursor(0, 54);
  u8g2.print("R:");
  for (uint8_t i = 0; i < RELAY_COUNT; i++) {
    u8g2.print(relay_state[i] ? "1" : "0");
    if (i != RELAY_COUNT - 1) u8g2.print(" ");
  }

  u8g2.sendBuffer();
}

// ========================== Frame update helpers ===========================
void applyRelaysFromFrame() {
  const uint16_t base = startAddr; // 1-based DMX address
  for (uint8_t i = 0; i < RELAY_COUNT; i++) {
    const uint16_t ch_index = (base - 1) + i; // 0-based index into g_frame.ch[]
    bool on = (g_frame.ch[ch_index] > 127); // ch[0]=DMX channel 1
    setRelay(i + 1, on);
  }
}

// ========================== Input: DMX =====================================
#if USE_DMX_INPUT
static uint8_t dmx_packet_buf[DMX_PACKET_SIZE];

bool poll_input_dmx(uint32_t now_ms) {
  dmx_packet_t packet;
  int rx_size = dmx_receive(DMX_PORT, &packet, DMX_TIMEOUT_TICK);

  if (rx_size > 0 && packet.err == DMX_OK && packet.sc == 0) {
    dmx_read(DMX_PORT, dmx_packet_buf, packet.size);

    int available = packet.size - 1;
    if (available > 512) available = 512;
    for (int i = 0; i < available; i++) {
      g_frame.ch[i] = dmx_packet_buf[1 + i];
    }
    g_frame.last_update_ms = now_ms;
    g_frame.frames_rx++;
    return true;
  }
  return false;
}

#endif

// ========================== Input: sACN (E1.31) =============================
#if USE_SACN_INPUT
bool poll_input_sacn(uint32_t now_ms) {
  bool updated = false;
  // Staging buffer: only committed once at end
  static uint8_t stage[512];
  // Drain a few packets; keep the newest DMX (start code 0x00)
  for (int n = 0; n < 4 && !e131.isEmpty(); n++) {
    e131_packet_t packet;
    e131.pull(&packet);
    if (packet.property_values[0] != 0x00) {
      continue; // ignore non-DMX start-code packets
    }
    // No memset. Just copy what we intend to use.
    for (int i = 0; i < 512; i++) {
      stage[i] = packet.property_values[1 + i];
    }
    updated = true;
  }
  // Commit once (atomic from your logic’s perspective)
  if (updated) {
    memcpy(g_frame.ch, stage, 512);
    g_frame.last_update_ms = now_ms;
    g_frame.frames_rx++;
  }
  return updated;
}
#endif

// ========================== Setup ==========================================
void setup() {
  Serial.begin(115200);
  delay(200);

  prefs.begin("dmxnode", false);
  startAddr  = prefs.getUShort("start", 1);
  if (startAddr  < 1) startAddr  = 1;
  if (startAddr  > 512) startAddr  = 512;

  // Button2 tuning
  btn.setDebounceTime(30);
  btn.setDoubleClickTime(300);
  btn.setLongClickTime(600);   // "long" inside cfg

  // Enter/exit cfg mode via very-long press (~2s).
  // Button2 doesn't have "very long" built-in, so we can implement it by
  // watching pressed duration in loop(), OR just use a long-press to enter
  // and long-press again to save/exit.
  //
  // Easiest: long press enters cfg, long press in cfg saves+exits.
  btn.setLongClickDetectedHandler([](Button2& b) {
    if (!cfgMode) {
      cfgMode = true;
      allRelaysOff();               // optional safety
      drawAddrSetScreen(startAddr); // show UI
    } else {
      prefs.putUShort("start", startAddr);
      cfgMode = false;
      // optionally redraw normal status screen immediately
    }
  });

  btn.setClickHandler([](Button2& b) {
    if (!cfgMode) return;
    if (startAddr < 512) startAddr++;
    drawAddrSetScreen(startAddr);
  });

  btn.setDoubleClickHandler([](Button2& b) {
    if (!cfgMode) return;
    if (startAddr > 1) startAddr--;
    drawAddrSetScreen(startAddr);
  });




  // I2C init (shared bus: PCF8574 + OLED)
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setClock(400000);

  // OLED init
  u8g2.begin();

  // Safe relay state
  pcf_out = 0xFF;
  pcfWrite(pcf_out);
  allRelaysOff();

#if USE_DMX_INPUT
  // Keep DI (TX) high for auto-direction RS485 chips when idle (helps stability)
  pinMode(RS485_TX_PIN, OUTPUT);
  digitalWrite(RS485_TX_PIN, HIGH);

  // esp_dmx init
  dmx_config_t config = DMX_CONFIG_DEFAULT;
  dmx_driver_install(DMX_PORT, &config, NULL, 0);
  dmx_set_pin(DMX_PORT, RS485_TX_PIN, RS485_RX_PIN, DMX_PIN_NO_CHANGE);

  Serial.println("Mode: DMX input");
#endif

#if USE_SACN_INPUT
  Serial.println("Mode: sACN (E1.31 multicast) input");
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 15000) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED){
    Serial.print("WiFi OK, IP=");
    Serial.println(WiFi.localIP());
  }
  else {
    Serial.println("WiFi connect failed; halting.");
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_6x12_tf);
    u8g2.setCursor(0, 12);
    u8g2.print("WiFi FAILED");
    u8g2.sendBuffer();
    while (true) delay(1000);
  }

  if(e131.begin(E131_MULTICAST, SACN_UNIVERSE)) {
    Serial.println("E1.31 started");
  }
  else {
    Serial.println("E1.31 begin() failed; halting.");
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_6x12_tf);
    u8g2.setCursor(0, 12);
    u8g2.print("E1.31 FAILED");
    u8g2.sendBuffer();
    while (true) delay(1000);
  }


#endif

  // Init stats
  g_frame.last_update_ms = 0;
  g_frame.frames_rx = 0;
  last_pps_calc_ms = 0;
  frames_at_last_calc = 0;

  drawStatus(false, 0);
}

void drawAddrSetScreen(uint16_t addr) {
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_6x12_tf);

  u8g2.setCursor(0, 12); u8g2.print("ADDR SET");
  u8g2.setCursor(0, 28); u8g2.print("Start: "); u8g2.print(addr);
  u8g2.setCursor(0, 42); u8g2.print("Ch: "); u8g2.print(addr); u8g2.print("-");
  u8g2.print(addr + RELAY_COUNT - 1);
  u8g2.setCursor(0, 60); u8g2.print("Tap:+1  Dbl:-1  Hold:Save");

  u8g2.sendBuffer();
}

// ========================== Loop ===========================================
void loop() {
  const uint32_t now = millis();

  btn.loop();

  if (cfgMode) {
    // do NOT process DMX/sACN (keeps UI stable)
    return;
  }

  // 1) Poll input to see if new data arrived
  bool dataReceived = false;
  #if USE_DMX_INPUT
    dataReceived = poll_input_dmx(now);
  #endif
  #if USE_SACN_INPUT
    dataReceived = poll_input_sacn(now);
  #endif

  // 2) Determine if input is considered present
  // (i.e. not necessarily that is has just changed, but that a signal has been received recently)
  const uint32_t age_ms = now - g_frame.last_update_ms;
  const bool link_ok = (age_ms < INPUT_OK_WINDOW_MS);

  // 3) Drive outputs if we have a valid link
  if (link_ok) {
    // Only rewrite relays when a new frame arrived (optional optimization)
    if (dataReceived) applyRelaysFromFrame();
  } 
  // If we cannot detect having received any input recently, turn the relays off
  else {
    allRelaysOff();
  }

  // 4) Stats + display
  // PPS = packets per second. i.e. data transfer rate
  // PPS calculation once per second (based on frames_rx)
  if (now - last_pps_calc_ms >= 1000) {
    pps = g_frame.frames_rx - frames_at_last_calc;
    frames_at_last_calc = g_frame.frames_rx;
    last_pps_calc_ms = now;
  }

  // OLED refresh ~5Hz
  static uint32_t last_draw_ms = 0;
  if (now - last_draw_ms >= 200) {
    drawStatus(link_ok, age_ms);
    last_draw_ms = now;
  }
}
