/*
  ===================================================================================
  ShrimpGuard - NODE 2: LoRa Telemetry Receiver + 20x4 LCD + 3-LED Indicator + Buzzer
  ===================================================================================
  Features:
    - SX1278 (RA-02) 433 MHz LoRa Receiver (SPI, non-blocking interrupt via RadioLib)
    - 20x4 I2C Character LCD Display (Live Temp, pH, ML Water Status, RSSI, Sequence)
    - 3-LED Status Classification System:
        * GREEN LED  -> Optimal water quality
        * YELLOW LED -> Warning (suboptimal temperature or pH requiring attention)
        * RED LED    -> Critical water quality (extreme conditions / lethal boundaries)
    - Multi-Speed Buzzer Alert System:
        * Optimal: Buzzer SILENT (brief optional chirp on packet reception)
        * Warning: Slower pulsing alert (triggers slowly at ~1.2s intervals)
        * Critical: Faster rapid alert (buzzes urgently at 5 Hz / 200ms intervals)
        * Timeout: Rapid warning when LoRa telemetry is lost (> 20s)
    - Embedded ML Classifier Fallback (via WaterQualityModel.h)

  Target Hardware:
    - ESP32 (ESP32 Dev Module / DevKit 30-pin & 38-pin) [Primary Target]
    - Also supports ESP8266 NodeMCU via conditional compilation

  Required Libraries (Install via Arduino IDE Library Manager):
    1. RadioLib           (by Jan Gromes)
    2. LiquidCrystal_I2C  (by Frank de Brabander / Marco Schwartz)
    3. Wire & SPI         (Built into ESP32 / Arduino Core)

  -----------------------------------------------------------------------------------
  WIRING GUIDE: ESP32 DevKit (Primary)
  -----------------------------------------------------------------------------------
    Component            Pin Name       ESP32 GPIO   Notes
    -------------------------------------------------------------------------
    SX1278 (RA-02)       NSS / CS       GPIO 5       (VSPI SS)
    SX1278 (RA-02)       SCK            GPIO 18      (VSPI SCK)
    SX1278 (RA-02)       MISO           GPIO 19      (VSPI MISO)
    SX1278 (RA-02)       MOSI           GPIO 23      (VSPI MOSI)
    SX1278 (RA-02)       RST            GPIO 27      Hardware Reset
    SX1278 (RA-02)       DIO0           GPIO 26      Interrupt pin
    SX1278 (RA-02)       VCC / GND      3.3V / GND   *DO NOT connect 5V to RA-02*
    -------------------------------------------------------------------------
    20x4 I2C LCD         SDA            GPIO 21      (Default I2C SDA)
    20x4 I2C LCD         SCL            GPIO 22      (Default I2C SCL)
    20x4 I2C LCD         VCC / GND      5V / GND     Connect VCC to VIN (5V)
    -------------------------------------------------------------------------
    Seeed Buzzer v1.3    SIG (Yellow)   GPIO 14      (Active Buzzer S9013 Driver)
    Seeed Buzzer v1.3    NC  (White)    Not connected Leave unconnected
    Seeed Buzzer v1.3    VCC (Red)      5V (or 3.3V) Connect to VIN (5V) or 3.3V
    Seeed Buzzer v1.3    GND (Black)    GND          Ground
    -------------------------------------------------------------------------
    Green LED (Optimal)  Anode (+)      GPIO 33      Requires 220 - 330 ohm resistor
                         Cathode (-)    GND
    -------------------------------------------------------------------------
    Yellow LED (Warning) Anode (+)      GPIO 32      Requires 220 - 330 ohm resistor
                         Cathode (-)    GND
    -------------------------------------------------------------------------
    Red LED (Critical)   Anode (+)      GPIO 25      Requires 220 - 330 ohm resistor
                         Cathode (-)    GND
    -------------------------------------------------------------------------

  -----------------------------------------------------------------------------------
  WIRING GUIDE: ESP8266 NodeMCU (Alternative)
  -----------------------------------------------------------------------------------
    Component            Pin Name       NodeMCU Pin  GPIO
    SX1278 (RA-02)       NSS / RST / D0 D8/D0/D3     GPIO 15, 16, 0
    20x4 I2C LCD         SDA / SCL      D2 / D1      GPIO 4, 5
    Active Buzzer        SIG            D4           GPIO 2
    Green LED (Optimal)  Anode (+)      D7           GPIO 13
    Yellow LED (Warning) Anode (+)      D6           GPIO 12
    Red LED (Critical)   Anode (+)      D5           GPIO 14
  ===================================================================================
*/

#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <RadioLib.h>
#include <LiquidCrystal_I2C.h>
#include "WaterQualityModel.h"

#if defined(ESP8266)
  #include <ESP8266WiFi.h>
  #include <ESP8266HTTPClient.h>
#elif defined(ESP32)
  #include <WiFi.h>
  #include <HTTPClient.h>
#endif

// ============================ PIN CONFIGURATION ============================
#if defined(ESP8266)
  // ESP8266 NodeMCU Pin Mapping
  #define PIN_LORA_NSS     15   // D8
  #define PIN_LORA_RST     16   // D0
  #define PIN_LORA_DIO0     0   // D3
  #define PIN_I2C_SDA       4   // D2 (I2C SDA)
  #define PIN_I2C_SCL       5   // D1 (I2C SCL)
  #define PIN_BUZZER        2   // D4 (GPIO 2)
  #define PIN_LED_RED      14   // D5 (GPIO 14)
  #define PIN_LED_YELLOW   12   // D6 (GPIO 12)
  #define PIN_LED_GREEN    13   // D7 (GPIO 13)

#else
  // ESP32 Dev Module Pin Mapping (Default Target)
  #define PIN_LORA_SCK     18   // VSPI SCK
  #define PIN_LORA_MISO    19   // VSPI MISO
  #define PIN_LORA_MOSI    23   // VSPI MOSI
  #define PIN_LORA_NSS      5   // VSPI SS
  #define PIN_LORA_RST     27   // RA-02 Reset
  #define PIN_LORA_DIO0    26   // RA-02 DIO0 Interrupt
  #define PIN_I2C_SDA     21   // I2C SDA
  #define PIN_I2C_SCL     22   // I2C SCL
  #define PIN_BUZZER       14   // Active Buzzer
  #define PIN_LED_RED      25   // Red LED: Critical
  #define PIN_LED_YELLOW   32   // Yellow LED: Warning
  #define PIN_LED_GREEN    33   // Green LED: Optimal
#endif

// ============================ USER CONFIGURATION ============================
// --- LCD Settings ---
#define LCD_I2C_ADDR       0x27 // Default I2C address (use 0x3F if blank)
#define LCD_COLS           20
#define LCD_ROWS            4

// --- Buzzer Settings (Configured for Seeed Studio Grove Buzzer v1.3) ---
#define BUZZER_ACTIVE_HIGH       true   // Seeed v1.3 has on-board S9013 NPN transistor: HIGH = ON, LOW = OFF
const bool ENABLE_BEEP_ON_RX     = true;  // Brief 50ms chirp on each valid packet received

// --- Timing (milliseconds) ---
const uint32_t NO_DATA_TIMEOUT_MS = 20000; // Trigger alarm if no packet for 20 seconds
const uint32_t RADIO_RETRY_MS     = 5000;  // RadioLib init retry interval

// --- LoRa Radio Settings (MUST MATCH TRANSMITTER CONFIG) ---
#define LORA_FREQ_MHZ      433.5
#define LORA_BW_KHZ        125.0
#define LORA_SF            9
#define LORA_CR            5       // 4/5
#define LORA_SYNC_WORD     0x12
#define LORA_PREAMBLE      8
#define LORA_POWER_DBM     10

// --- ShrimpGuard Integration Settings ---
// Node 2 is standalone & solar-powered near the farmer (not plugged into PC via USB).
// It forwards received LoRa telemetry over local Wi-Fi directly to ShrimpGuard.
#define ENABLE_WIFI_POST           true   // Enabled for standalone solar operation
const char* WIFI_SSID             = "Xiaomi 12X";      // Enter your Wi-Fi Router or Phone Hotspot Name
const char* WIFI_PASSWORD         = "12345678K";  // Enter your Wi-Fi Password
const char* SHRIMPGUARD_API_URL   = "http://191.0.14.54:5000/api/readings"; // ShrimpGuard PC Local IP
const char* SHRIMPGUARD_API_KEY   = "shrimpguard-secret-key-capstone2";
// ============================================================================

// Hardware Objects
SPISettings loraSpiSettings(1000000, MSBFIRST, SPI_MODE0); // 1 MHz conservative clock for clean breadboard SPI
SX1278 radio = new Module(PIN_LORA_NSS, PIN_LORA_DIO0, PIN_LORA_RST, RADIOLIB_NC, SPI, loraSpiSettings);
// Dual I2C instances to support both 0x27 and 0x3F automatically without manual switching
LiquidCrystal_I2C lcd27(0x27, LCD_COLS, LCD_ROWS);
LiquidCrystal_I2C lcd3F(0x3F, LCD_COLS, LCD_ROWS);
LiquidCrystal_I2C* pLcd = &lcd27;
#define lcd (*pLcd)

// Degree Symbol Custom Character Pattern (8x5 matrix)
byte customDegree[8] = {
  0b00110,
  0b01001,
  0b01001,
  0b00110,
  0b00000,
  0b00000,
  0b00000,
  0b00000
};

// LoRa RX Interrupt Flag
volatile bool rxFlag = false;
#if defined(ESP8266)
  void ICACHE_RAM_ATTR onPacketReceived() { rxFlag = true; }
#else
  void IRAM_ATTR onPacketReceived() { rxFlag = true; }
#endif

// System State
bool        radioReady     = false;
uint32_t    lastRadioTry   = 0;
uint32_t    lastRxMs       = 0;
uint32_t    lastLcdTickMs  = 0;
bool        everReceived   = false;
bool        isTimeoutAlert = false;

// Statistics & Last Received Data
uint32_t    cntGood        = 0;
uint32_t    cntMalformed   = 0;
uint32_t    cntDuplicate   = 0;
uint32_t    cntMissed      = 0;
uint32_t    cntCrc         = 0;
char        lastDevice[16] = "---";
uint32_t    lastSeq        = 0;
bool        haveLastSeq    = false;
float       lastTemp       = 0.0f;
float       lastPH         = 0.0f;
bool        lastTempValid  = false;
float       lastRssi       = 0.0f;
float       lastSnr        = 0.0f;
WaterStatus lastStatus     = WATER_CRITICAL;

// Non-blocking Buzzer Control
enum BuzzerMode { BUZZ_IDLE, BUZZ_CHIRP };
BuzzerMode  buzzMode       = BUZZ_IDLE;
uint32_t    buzzTimer      = 0;

// ----------------------------------------------------------------------------
// Helper: Raw Buzzer Output
// ----------------------------------------------------------------------------
void buzzerSet(bool on) {
  if (BUZZER_ACTIVE_HIGH) {
    digitalWrite(PIN_BUZZER, on ? HIGH : LOW);
  } else {
    digitalWrite(PIN_BUZZER, on ? LOW : HIGH);
  }
}

// ----------------------------------------------------------------------------
// Helper: Trigger brief chirp upon packet arrival
// ----------------------------------------------------------------------------
void triggerBuzzerChirp() {
  if (!ENABLE_BEEP_ON_RX) return;
  buzzMode = BUZZ_CHIRP;
  buzzTimer = millis();
  buzzerSet(true);
}

// ----------------------------------------------------------------------------
// Helper: Update 3 Status LEDs
//   - Optimal:  Green ON, Yellow OFF, Red OFF
//   - Warning:  Green OFF, Yellow ON, Red OFF
//   - Critical: Green OFF, Yellow OFF, Red ON
//   - Timeout:  Red flashes every 500ms
// ----------------------------------------------------------------------------
void updateLeds(WaterStatus status, bool timeoutActive) {
  if (timeoutActive) {
    // Flash Red LED during telemetry signal timeout
    bool flashState = ((millis() / 500) % 2) == 0;
    digitalWrite(PIN_LED_RED,    flashState ? HIGH : LOW);
    digitalWrite(PIN_LED_YELLOW, LOW);
    digitalWrite(PIN_LED_GREEN,  LOW);
    return;
  }

  if (!everReceived) {
    // Standby before first packet: all LEDs off
    digitalWrite(PIN_LED_RED,    LOW);
    digitalWrite(PIN_LED_YELLOW, LOW);
    digitalWrite(PIN_LED_GREEN,  LOW);
    return;
  }

  switch (status) {
    case WATER_OPTIMAL:
      digitalWrite(PIN_LED_GREEN,  HIGH);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED,    LOW);
      break;

    case WATER_WARNING:
      digitalWrite(PIN_LED_GREEN,  LOW);
      digitalWrite(PIN_LED_YELLOW, HIGH);
      digitalWrite(PIN_LED_RED,    LOW);
      break;

    case WATER_CRITICAL:
    default:
      digitalWrite(PIN_LED_GREEN,  LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED,    HIGH);
      break;
  }
}

// ----------------------------------------------------------------------------
// Helper: Non-blocking Buzzer Pattern Engine
//   - WATER_OPTIMAL:  SILENT (buzzer OFF)
//   - WATER_WARNING:  Slow trigger (200ms beep every 1200ms)
//   - WATER_CRITICAL: Fast trigger (100ms beep every 200ms -> 5 Hz rapid alarm)
//   - TIMEOUT:        Fast warning buzz
// ----------------------------------------------------------------------------
void updateBuzzer(WaterStatus status, bool timeoutActive) {
  uint32_t now = millis();

  // 1. High priority: Single-pulse RX arrival chirp (50 ms)
  if (buzzMode == BUZZ_CHIRP) {
    if (now - buzzTimer >= 50) {
      buzzerSet(false);
      buzzMode = BUZZ_IDLE;
    }
    return;
  }

  // Treat timeout as critical condition to alert user to link loss
  if (timeoutActive) {
    status = WATER_CRITICAL;
  }

  // 2. Continuous cadences based on ML classification
  if (status == WATER_CRITICAL) {
    // Fast buzzing: 100ms ON / 100ms OFF (5 beeps per second)
    uint32_t cycle = now % 200;
    buzzerSet(cycle < 100);
  } else if (status == WATER_WARNING) {
    // Slower buzzing: 200ms ON / 1000ms OFF (slow pulse every 1.2s)
    uint32_t cycle = now % 1200;
    buzzerSet(cycle < 200);
  } else {
    // Optimal condition: Silent
    buzzerSet(false);
  }
}

// ----------------------------------------------------------------------------
// Helper: Initialize SX1278 LoRa Receiver
// ----------------------------------------------------------------------------
bool initRadio() {
#if defined(ESP32)
  // Ensure NSS starts unasserted (HIGH)
  pinMode(PIN_LORA_NSS, OUTPUT);
  digitalWrite(PIN_LORA_NSS, HIGH);

  // Perform clean hardware reset on SX1278
  pinMode(PIN_LORA_RST, OUTPUT);
  digitalWrite(PIN_LORA_RST, LOW);
  delay(10);
  digitalWrite(PIN_LORA_RST, HIGH);
  delay(20);

  SPI.begin(PIN_LORA_SCK, PIN_LORA_MISO, PIN_LORA_MOSI);
#elif defined(ESP8266)
  SPI.begin();
#endif

  Serial.print(F("[LoRa] Initializing SX1278... "));
#if defined(RADIOLIB_VERSION_MAJOR) && (RADIOLIB_VERSION_MAJOR >= 7)
  ConfigLoRa_t config;
  config.frequency       = (uint32_t)(LORA_FREQ_MHZ * 1000000.0f); // RadioLib v7 expects Hz (433500000 Hz)
  config.bandwidth       = (uint32_t)(LORA_BW_KHZ * 1000.0f);      // RadioLib v7 expects Hz (125000 Hz)
  config.spreadingFactor = LORA_SF;
  config.codingRate      = LORA_CR;
  config.syncWord        = LORA_SYNC_WORD;
  config.power           = LORA_POWER_DBM;
  config.preambleLength  = LORA_PREAMBLE;
  int16_t st = radio.begin(config);
#else
  int16_t st = radio.begin(LORA_FREQ_MHZ, LORA_BW_KHZ, LORA_SF, LORA_CR,
                           LORA_SYNC_WORD, LORA_POWER_DBM, LORA_PREAMBLE);
#endif
  if (st != RADIOLIB_ERR_NONE) {
    Serial.print(F("FAILED, code "));
    Serial.println(st);
    Serial.println(F("        Check SPI wiring (SCK, MISO, MOSI, NSS, RST, DIO0), 3.3V power and GND."));
    return false;
  }

  st = radio.setCRC(true);
  if (st != RADIOLIB_ERR_NONE) {
    Serial.print(F("FAILED to enable CRC, code "));
    Serial.println(st);
    return false;
  }

#if defined(RADIOLIB_VERSION_MAJOR) && (RADIOLIB_VERSION_MAJOR >= 7)
  radio.setDio0Action(onPacketReceived, RISING);
#else
  radio.setPacketReceivedAction(onPacketReceived);
#endif
  st = radio.startReceive();
  if (st != RADIOLIB_ERR_NONE) {
    Serial.print(F("FAILED to start receive, code "));
    Serial.println(st);
    return false;
  }

  Serial.println(F("OK, listening."));
  Serial.print(F("[LoRa] Freq: "));
  Serial.print(LORA_FREQ_MHZ, 3);
  Serial.print(F(" MHz | BW: "));
  Serial.print(LORA_BW_KHZ, 0);
  Serial.print(F(" kHz | SF: "));
  Serial.print(LORA_SF);
  Serial.print(F(" | Sync: 0x"));
  Serial.println(LORA_SYNC_WORD, HEX);
  return true;
}

// ----------------------------------------------------------------------------
// Helper: Parse incoming telemetry packet
// Supported formats:
//   6-Token: SG1,<deviceId>,<sequence>,<temperatureC>,<pH>,<status>
//   5-Token (Legacy fallback): SG1,<deviceId>,<sequence>,<temperatureC>,<pH>
// ----------------------------------------------------------------------------
bool parsePacket(const String& raw, char* idOut, size_t idSize,
                 uint32_t& seqOut, float& tempOut, float& phOut,
                 WaterStatus& statusOut) {
  char buf[80];
  if (raw.length() == 0 || raw.length() >= sizeof(buf)) return false;
  raw.toCharArray(buf, sizeof(buf));

  char* save  = nullptr;
  char* tag   = strtok_r(buf, ",", &save);
  char* id    = strtok_r(nullptr, ",", &save);
  char* seq   = strtok_r(nullptr, ",", &save);
  char* temp  = strtok_r(nullptr, ",", &save);
  char* ph    = strtok_r(nullptr, ",", &save);
  char* stat  = strtok_r(nullptr, ",", &save);
  char* extra = strtok_r(nullptr, ",", &save);

  if (!tag || !id || !seq || !temp) return false;
  if (strcmp(tag, "SG1") != 0) return false;
  if (strlen(id) == 0 || strlen(id) >= idSize) return false;

  char* end = nullptr;
  unsigned long s = strtoul(seq, &end, 10);
  if (end == seq || *end != '\0') return false;

  float t = strtod(temp, &end);
  if (end == temp || *end != '\0') return false;

  // Temperature validity check: allow -127.0 (disconnected sensor code) or valid range -55..125
  bool validTemp = (t >= -55.0f && t <= 125.0f) || (t <= -120.0f);
  if (!validTemp) return false;

  float p = NAN;
  if (ph) {
    p = strtod(ph, &end);
    if (end == ph || *end != '\0') return false;
    if (p < 0.0f || p > 14.0f) return false;
  }

  // Parse status if present; otherwise predict locally using embedded ML model
  WaterStatus st = WATER_CRITICAL;
  if (stat) {
    st = stringToWaterStatus(stat);
  } else {
    st = predictWaterQuality(t, p);
  }

  if (extra) {
    // Unexpected trailing token
    return false;
  }

  strncpy(idOut, id, idSize - 1);
  idOut[idSize - 1] = '\0';
  seqOut    = (uint32_t)s;
  tempOut   = t;
  phOut     = p;
  statusOut = st;
  return true;
}

// ----------------------------------------------------------------------------
// Helper: Individual Status Word for Temperature (Optimal, Warning, Critical)
// Ranges based on aquaculture standards & ML training boundaries:
//   Optimal:  28.00 - 32.00 °C  -> "Optimal"
//   Warning:  25.01 - 27.99 °C  -> "Warning"
//             32.01 - 33.50 °C  -> "Warning"
//   Critical: <= 25.00 °C       -> "Critical"
//             > 33.50 °C        -> "Critical"
// ----------------------------------------------------------------------------
const char* getTempStatusWord(float temp, bool valid) {
  if (!valid || temp <= -120.0f || isnan(temp)) return "Critical";
  if (temp <= 25.00f || temp > 33.50f)          return "Critical";
  if (temp < 28.00f || temp > 32.00f)           return "Warning";
  return "Optimal";
}

// ----------------------------------------------------------------------------
// Helper: Individual Status Word for pH (Optimal, Warning, Critical)
// Ranges based on aquaculture standards & ML training boundaries:
//   Optimal:  7.50 - 8.50        -> "Optimal"
//   Warning:  6.50 - 7.49        -> "Warning"
//             8.51 - 9.00        -> "Warning"
//   Critical: < 6.50             -> "Critical"
//             > 9.00             -> "Critical"
// ----------------------------------------------------------------------------
const char* getPHStatusWord(float ph) {
  if (isnan(ph))                                return "Critical";
  if (ph < 6.50f || ph > 9.00f)                 return "Critical";
  if (ph < 7.50f || ph > 8.50f)                 return "Warning";
  return "Optimal";
}

// ----------------------------------------------------------------------------
// Helper: Update 20x4 LCD Screen (Flicker-free row writes)
// Displays:
//   Row 0: [DEVICE]   Seq:1234
//   Row 1: T: 28.52°C  Optimal   (Live Temp + Individual Status)
//   Row 2: pH:  7.82   Optimal   (Live pH   + Individual Status)
//   Row 3: Water: [Optimal]      (Overall ML Classification Status)
// ----------------------------------------------------------------------------
void updateLcdScreen(bool timeoutAlert) {
  char line[21];

  if (!everReceived) {
    lcd.setCursor(0, 0);
    lcd.print("====================");
    lcd.setCursor(0, 1);
    lcd.print("  ShrimpGuard Node2 ");
    lcd.setCursor(0, 2);
    lcd.print("Waiting for data... ");
    lcd.setCursor(0, 3);
    snprintf(line, sizeof(line), "Radio: %-13s", radioReady ? "READY" : "CONNECTING...");
    lcd.print(line);
    return;
  }

  // Row 0: Device ID & Sequence or Timeout Status (20 chars)
  lcd.setCursor(0, 0);
  if (timeoutAlert) {
    snprintf(line, sizeof(line), "[%-6s]   *TIMEOUT* ", lastDevice);
  } else {
    snprintf(line, sizeof(line), "[%-6s]   Seq:%-6lu", lastDevice, (unsigned long)lastSeq);
  }
  lcd.print(line);

  // Row 1: Temperature Reading + Individual Status (20 chars)
  lcd.setCursor(0, 1);
  if (!lastTempValid) {
    snprintf(line, sizeof(line), "T:  ERR       %-8s", getTempStatusWord(lastTemp, lastTempValid));
    lcd.print(line);
  } else {
    snprintf(line, sizeof(line), "T: %5.2f", lastTemp);
    lcd.print(line);
    lcd.write((uint8_t)0); // Custom degree ° character
    snprintf(line, sizeof(line), "C  %-8s", getTempStatusWord(lastTemp, lastTempValid));
    lcd.print(line);
  }

  // Row 2: pH Reading + Individual Status (20 chars)
  lcd.setCursor(0, 2);
  if (isnan(lastPH)) {
    snprintf(line, sizeof(line), "pH:  ERR      %-8s", getPHStatusWord(lastPH));
  } else {
    snprintf(line, sizeof(line), "pH:  %5.2f  %-8s", lastPH, getPHStatusWord(lastPH));
  }
  lcd.print(line);

  // Row 3: Overall Water Quality Status based on ML Model (20 chars)
  lcd.setCursor(0, 3);
  if (timeoutAlert) {
    lcd.print("Water: *NO SIGNAL*  ");
  } else {
    switch (lastStatus) {
      case WATER_OPTIMAL:
        lcd.print("Water: [Optimal]    ");
        break;
      case WATER_WARNING:
        lcd.print("Water: [Warning]    ");
        break;
      case WATER_CRITICAL:
      default:
        lcd.print("Water: [Critical]   ");
        break;
    }
  }
}

// ----------------------------------------------------------------------------
// Helper: Direct WiFi HTTP POST to ShrimpGuard API (Used when ENABLE_WIFI_POST=true)
// ----------------------------------------------------------------------------
void postReadingToShrimpGuard(float temp, float ph, const char* devId, uint32_t seq) {
#if (defined(ESP8266) || defined(ESP32))
  if (!ENABLE_WIFI_POST) return;
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println(F("[HTTP] WiFi not connected. Attempting reconnection..."));
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    return;
  }

  WiFiClient client;
  HTTPClient http;
#if defined(ESP8266)
  if (!http.begin(client, SHRIMPGUARD_API_URL)) {
#else
  if (!http.begin(SHRIMPGUARD_API_URL)) {
#endif
    Serial.println(F("[HTTP] Failed to initialize connection to ShrimpGuard API."));
    return;
  }

  http.setTimeout(4000); // 4-second timeout to prevent blocking LoRa loop
  http.addHeader(F("Content-Type"), F("application/json"));
  http.addHeader(F("X-API-Key"), SHRIMPGUARD_API_KEY);

  char jsonPayload[180];
  snprintf(jsonPayload, sizeof(jsonPayload),
           "{\"temperature\":%.2f,\"ph\":%.2f,\"device_id\":\"%s\",\"seq\":%lu,\"user_email\":\"rio@gmail.com\"}",
           temp, ph, devId, (unsigned long)seq);

  int httpCode = http.POST((uint8_t*)jsonPayload, strlen(jsonPayload));
  if (httpCode > 0) {
    Serial.print(F("[HTTP] Forwarded reading to ShrimpGuard -> HTTP "));
    Serial.println(httpCode);
  } else {
    Serial.print(F("[HTTP] POST failed, error: "));
    Serial.println(http.errorToString(httpCode).c_str());
  }
  http.end();
#endif
}

// ----------------------------------------------------------------------------
// Helper: Process incoming LoRa packet
// ----------------------------------------------------------------------------
void handlePacket() {
  String payload;
  int16_t st = radio.readData(payload);

  if (st == RADIOLIB_ERR_CRC_MISMATCH) {
    cntCrc++;
    Serial.println(F("[RX] CRC error: Packet corrupted in the air."));
    return;
  }
  if (st != RADIOLIB_ERR_NONE) {
    Serial.print(F("[RX] Read error, code "));
    Serial.println(st);
    return;
  }

  float rssi = radio.getRSSI();
  float snr  = radio.getSNR();

  char        id[16];
  uint32_t    seq;
  float       tempC;
  float       phVal;
  WaterStatus parsedStatus;

  if (!parsePacket(payload, id, sizeof(id), seq, tempC, phVal, parsedStatus)) {
    cntMalformed++;
    Serial.print(F("[RX] MALFORMED packet: \""));
    Serial.print(payload);
    Serial.print(F("\"  RSSI "));
    Serial.print(rssi, 0);
    Serial.println(F(" dBm"));
    return;
  }

  // Update timestamps
  lastRxMs       = millis();
  everReceived   = true;
  isTimeoutAlert = false;

  // New device detected: reset sequence tracking
  if (strcmp(id, lastDevice) != 0) {
    strncpy(lastDevice, id, sizeof(lastDevice) - 1);
    lastDevice[sizeof(lastDevice) - 1] = '\0';
    haveLastSeq = false;
  }

  // Duplicate packet filter
  if (haveLastSeq && seq == lastSeq) {
    cntDuplicate++;
    Serial.print(F("[RX] DUPLICATE packet, seq "));
    Serial.print(seq);
    Serial.println(F(" (ignored)"));
    return;
  }

  // Check for missed packets
  if (haveLastSeq) {
    if (seq > lastSeq + 1) {
      uint32_t missed = seq - lastSeq - 1;
      cntMissed += missed;
      Serial.print(F("[RX] WARNING: "));
      Serial.print(missed);
      Serial.println(F(" packet(s) missed before this one."));
    } else if (seq < lastSeq) {
      Serial.println(F("[RX] NOTE: Sequence restarted by transmitter."));
    }
  }

  lastSeq        = seq;
  haveLastSeq    = true;
  cntGood++;

  // Cache readings
  lastTemp       = tempC;
  lastTempValid  = (tempC > -120.0f); // -127.0 is disconnected DS18B20
  lastPH         = phVal;
  lastRssi       = rssi;
  lastSnr        = snr;
  lastStatus     = parsedStatus;

  // Trigger brief beep on reception
  triggerBuzzerChirp();

  // Print diagnostics to Serial Monitor
  Serial.print(F("[RX] OK  Node="));
  Serial.print(id);
  Serial.print(F(" | Seq="));
  Serial.print(seq);
  Serial.print(F(" | Temp="));
  if (lastTempValid) {
    Serial.print(tempC, 2);
    Serial.print(F(" C"));
  } else {
    Serial.print(F("ERR"));
  }
  Serial.print(F(" | pH="));
  if (!isnan(phVal)) {
    Serial.print(phVal, 2);
  } else {
    Serial.print(F("N/A"));
  }
  Serial.print(F(" | Status="));
  Serial.print(waterStatusToString(lastStatus));
  Serial.print(F(" | RSSI="));
  Serial.print(rssi, 0);
  Serial.print(F(" dBm | SNR="));
  Serial.print(snr, 1);
  Serial.print(F(" dB"));
  Serial.println();

  // --- Forward Telemetry to ShrimpGuard System ---
  // 1. Output machine-parseable JSON line for USB Serial Gateway (lora_gateway.py)
  Serial.print(F("LORA_JSON:{\"device\":\""));
  Serial.print(id);
  Serial.print(F("\",\"seq\":"));
  Serial.print(seq);
  Serial.print(F(",\"temperature\":"));
  Serial.print(tempC, 2);
  Serial.print(F(",\"ph\":"));
  if (!isnan(phVal)) {
    Serial.print(phVal, 2);
  } else {
    Serial.print(F("7.00"));
  }
  Serial.print(F(",\"status\":\""));
  Serial.print(waterStatusToString(lastStatus));
  Serial.print(F("\",\"rssi\":"));
  Serial.print(rssi, 1);
  Serial.print(F(",\"snr\":"));
  Serial.print(snr, 1);
  Serial.println(F("}"));

  // 2. Direct WiFi HTTP POST (if enabled)
  if (ENABLE_WIFI_POST && lastTempValid && !isnan(phVal)) {
    postReadingToShrimpGuard(tempC, phVal, id, seq);
  }

  // Refresh outputs
  updateLeds(lastStatus, false);
  updateLcdScreen(false);
}

// ============================================================================
// SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(300);

#if (defined(ESP8266) || defined(ESP32))
  if (ENABLE_WIFI_POST) {
    Serial.print(F("[WiFi] Connecting to: "));
    Serial.println(WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  } else {
#if defined(ESP8266)
    // Disable WiFi on ESP8266 to conserve power and reduce RF noise
    WiFi.mode(WIFI_OFF);
    WiFi.forceSleepBegin();
    delay(10);
#endif
  }
#endif

  // 1. Initialize 3 Status LEDs
  pinMode(PIN_LED_GREEN,  OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED,    OUTPUT);
  digitalWrite(PIN_LED_GREEN,  LOW);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED,    LOW);

  // 2. Initialize Buzzer
  pinMode(PIN_BUZZER, OUTPUT);
  buzzerSet(false);

  // 3. Initialize I2C Bus & 20x4 LCD
#if defined(ESP32)
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
#elif defined(ESP8266)
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
#endif

  // --- I2C Bus Auto-Detection & Diagnostics ---
  Serial.println(F("[I2C] Scanning for LCD display..."));
  uint8_t detectedAddr = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print(F("[I2C] Device found at 0x"));
      if (addr < 16) Serial.print(F("0"));
      Serial.println(addr, HEX);
      if (addr == 0x3F) detectedAddr = 0x3F;
      else if (addr == 0x27) detectedAddr = 0x27;
    }
  }

  if (detectedAddr == 0x3F) {
    pLcd = &lcd3F;
    Serial.println(F("[LCD] Auto-selected LCD address 0x3F"));
  } else {
    pLcd = &lcd27;
    Serial.println(F("[LCD] Auto-selected LCD address 0x27"));
  }

  // Initialize both LCD instances so whichever address is physically wired receives commands
  lcd27.init();
  lcd27.backlight();
  lcd27.createChar(0, customDegree);

  lcd3F.init();
  lcd3F.backlight();
  lcd3F.createChar(0, customDegree);

  // Display Splash Screen
  lcd.setCursor(0, 0);
  lcd.print("====================");
  lcd.setCursor(0, 1);
  lcd.print("  ShrimpGuard Node2 ");
  lcd.setCursor(0, 2);
  lcd.print("ESP32 LoRa + ML LCD ");
  lcd.setCursor(0, 3);
  lcd.print("====================");

  // 4. Power-on Hardware Self-Test (Green -> Yellow -> Red -> Buzzer Chirp)
  digitalWrite(PIN_LED_GREEN, HIGH);
  delay(200);
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_YELLOW, HIGH);
  delay(200);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED, HIGH);
  buzzerSet(true);
  delay(150);
  buzzerSet(false);
  digitalWrite(PIN_LED_RED, LOW);
  delay(800);

  // 5. Initialize LoRa Radio
  radioReady   = initRadio();
  lastRadioTry = millis();
  lastRxMs     = millis();

  // Initial LCD update
  updateLcdScreen(false);
}

// ============================================================================
// LOOP
// ============================================================================
void loop() {
  uint32_t now = millis();

  // 1. Retry radio initialization if failed (non-blocking)
  if (!radioReady) {
    if (now - lastRadioTry >= RADIO_RETRY_MS) {
      lastRadioTry = now;
      radioReady = initRadio();
    }
  }

  // 2. Process incoming LoRa packet
  if (rxFlag) {
    rxFlag = false;
    handlePacket();
    radio.startReceive(); // Re-arm receiver
  }

  // 3. Check for telemetry timeout (no data received for NO_DATA_TIMEOUT_MS)
  now = millis();
  bool timedOut = everReceived && (now - lastRxMs >= NO_DATA_TIMEOUT_MS);
  isTimeoutAlert = timedOut;

  // 4. Update LED states (Optimal = Green, Warning = Yellow, Critical = Red, Timeout = Red flash)
  updateLeds(lastStatus, isTimeoutAlert);

  // 5. Periodic LCD refresh (every 1 second continuous refresh)
  if (now - lastLcdTickMs >= 1000) {
    lastLcdTickMs = now;
    updateLcdScreen(isTimeoutAlert);
  }

  // 6. Update non-blocking buzzer cadences:
  //    - Optimal:  Silent
  //    - Warning:  Slower alert
  //    - Critical: Faster rapid alert
  updateBuzzer(lastStatus, isTimeoutAlert);
}
