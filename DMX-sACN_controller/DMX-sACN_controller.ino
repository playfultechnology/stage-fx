#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncE131.h>

extern "C" {
  #include "esp_dmx.h"
}

#include <esp_wifi.h>  // optional, but recommended for multicast reliability

// ===================== USER SETTINGS =====================
static const char* WIFI_SSID = "vodafone1236D8";
static const char* WIFI_PASS = "q3TGpAbgHL7KaYsp";

static constexpr uint16_t SACN_UNIVERSE = 1;     // multicast universe
static constexpr uint32_t SACN_TIMEOUT_MS = 3500; // consider sACN "lost" if no packets in this time

static constexpr uint32_t DMX_FRAME_MS = 25;     // ~40 FPS output
static constexpr uint32_t FADE_MS = 1500;        // crossfade duration when sACN first appears

// ===================== HARDWARE (KC868-style) =====================
static constexpr dmx_port_t DMX_PORT = DMX_NUM_1;
static constexpr int DMX_TX_PIN = 27;
static constexpr int DMX_RX_PIN = 14;

// E1.31 ring buffer slots
ESPAsyncE131 e131(4);

// DMX output buffer (start code + 512)
static uint8_t dmx_out[DMX_PACKET_SIZE];

// ===================== Frame buffers =====================
struct dmx_frame_t {
  uint8_t  ch[512];
  uint32_t last_update_ms;
  uint32_t frames_rx;
  bool     has_data;
};

static dmx_frame_t sacn_frame = { {0}, 0, 0, false };

// We render into this "final" frame each tick (boot look, fade mix, or pure sACN)
static uint8_t render_frame[512];

// ===================== Blue pulse boot look =====================
// Blue breathing on RGB channels 1..3 (R,G,B). Adjust if your fixture differs.
static inline uint8_t tri8(uint32_t t, uint32_t period) {
  uint32_t x = t % period;
  uint32_t half = period / 2;
  if (x < half) return (uint8_t)((x * 255UL) / half);
  x -= half;
  return (uint8_t)(255 - (x * 255UL) / half);
}

static void make_boot_pulse(uint32_t now_ms, uint8_t out[512]) {
  // Clear (or leave as-is if you want other channels untouched)
  memset(out, 0, 512);

  // 3s breathing cycle
  uint8_t v = tri8(now_ms, 3000);

  // Deep-ish blue pulse (scale to avoid harsh full blue if you like)
  out[0] = 0;      // Ch1 R
  out[1] = 0;      // Ch2 G
  out[2] = v;      // Ch3 B
}

// ===================== DMX output =====================
static inline void dmx_send_frame(const uint8_t ch512[512]) {
  dmx_out[0] = 0x00; // start code
  memcpy(&dmx_out[1], ch512, 512);

  dmx_write(DMX_PORT, dmx_out, DMX_PACKET_SIZE);
  dmx_send(DMX_PORT);
  dmx_wait_sent(DMX_PORT, DMX_TIMEOUT_TICK);
}

// ===================== sACN input poll =====================
// Drain a few packets; keep the newest valid DMX (start code 0x00).
static bool poll_sacn(uint32_t now_ms) {
  bool updated = false;
  static uint8_t stage[512];

  for (int n = 0; n < 4 && !e131.isEmpty(); n++) {
    e131_packet_t packet;
    e131.pull(&packet);

    if (packet.property_values[0] != 0x00) continue; // only DMX start code

    // Copy Ch1..512 (property_values[1..512])
    for (int i = 0; i < 512; i++) {
      stage[i] = packet.property_values[1 + i];
    }
    updated = true;
  }

  if (updated) {
    memcpy(sacn_frame.ch, stage, 512);
    sacn_frame.last_update_ms = now_ms;
    sacn_frame.frames_rx++;
    sacn_frame.has_data = true;
  }

  return updated;
}

// Linear blend: out = (1-a)*A + a*B, where a in [0..255]
static inline uint8_t lerp8(uint8_t a, uint8_t b, uint8_t alpha) {
  // alpha=0 -> a, alpha=255 -> b
  return (uint8_t)(((uint16_t)a * (255 - alpha) + (uint16_t)b * alpha + 127) / 255);
}

// ===================== Fade state =====================
enum class Mode : uint8_t { BOOT_LOOK, FADING_TO_SACN, LIVE_SACN };
static Mode mode = Mode::BOOT_LOOK;

static uint32_t fade_start_ms = 0;
static uint8_t  fade_from[512];  // snapshot of what we were outputting when fade began

// ===================== Setup =====================
void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println("sACN multicast -> DMX OUT with boot blue pulse + fade to sACN");

  // Ensure TX idles HIGH (helps auto-direction RS485)
  pinMode(DMX_TX_PIN, OUTPUT);
  digitalWrite(DMX_TX_PIN, HIGH);

  // DMX init
  dmx_config_t config = DMX_CONFIG_DEFAULT;
  dmx_driver_install(DMX_PORT, &config, NULL, 0);
  dmx_set_pin(DMX_PORT, DMX_TX_PIN, DMX_RX_PIN, DMX_PIN_NO_CHANGE);
  memset(dmx_out, 0, sizeof(dmx_out));

  // Wi-Fi connect
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.print("Connecting WiFi");
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 15000) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi failed; staying in boot look.");
    // (Optionally add AP fallback later.)
  } else {
    WiFi.setSleep(false);
    esp_wifi_set_ps(WIFI_PS_NONE);

    Serial.print("WiFi OK, IP=");
    Serial.println(WiFi.localIP());

    if (!e131.begin(E131_MULTICAST, SACN_UNIVERSE)) {
      Serial.println("E1.31 begin() failed; staying in boot look.");
    } else {
      Serial.print("Listening sACN universe ");
      Serial.println(SACN_UNIVERSE);
    }
  }

  sacn_frame.last_update_ms = millis();
  sacn_frame.has_data = false;

  // Start in boot look
  mode = Mode::BOOT_LOOK;
}

// ===================== Loop =====================
void loop() {
  const uint32_t now = millis();

  // Poll sACN if running
  poll_sacn(now);

  const uint32_t sacn_age_ms = now - sacn_frame.last_update_ms;
  const bool sacn_ok = sacn_frame.has_data && (sacn_age_ms < SACN_TIMEOUT_MS);

  // State transitions
  if (mode == Mode::BOOT_LOOK && sacn_ok) {
    // Begin fade: snapshot current render output into fade_from
    make_boot_pulse(now, fade_from);
    fade_start_ms = now;
    mode = Mode::FADING_TO_SACN;
    Serial.println("sACN detected -> fading to LIVE");
  }

  if (mode == Mode::LIVE_SACN && !sacn_ok) {
    // sACN lost -> go back to boot look (change this if you prefer "hold last")
    mode = Mode::BOOT_LOOK;
    Serial.println("sACN lost -> back to boot look");
  }

  // Render frame based on mode
  if (mode == Mode::BOOT_LOOK) {
    make_boot_pulse(now, render_frame);
  } else if (mode == Mode::LIVE_SACN) {
    memcpy(render_frame, sacn_frame.ch, 512);
  } else { // FADING_TO_SACN
    uint32_t elapsed = now - fade_start_ms;
    if (elapsed >= FADE_MS) {
      mode = Mode::LIVE_SACN;
      memcpy(render_frame, sacn_frame.ch, 512);
    } else {
      uint8_t alpha = (uint8_t)((elapsed * 255UL) / FADE_MS);
      for (int i = 0; i < 512; i++) {
        render_frame[i] = lerp8(fade_from[i], sacn_frame.ch[i], alpha);
      }
    }
  }

  // Transmit DMX at steady rate
  static uint32_t last_tx_ms = 0;
  if (now - last_tx_ms >= DMX_FRAME_MS) {
    dmx_send_frame(render_frame);
    last_tx_ms = now;
  }

  // Optional log (1Hz)
  static uint32_t last_log = 0;
  if (now - last_log >= 1000) {
    Serial.printf("mode=%d sacn_ok=%d age=%lu ms rx=%lu\n",
                  (int)mode, sacn_ok ? 1 : 0, (unsigned long)sacn_age_ms, (unsigned long)sacn_frame.frames_rx);
    last_log = now;
  }
}
