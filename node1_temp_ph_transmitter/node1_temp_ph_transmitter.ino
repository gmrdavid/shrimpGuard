/*
  ===================================================================================
  ShrimpGuard - NODE 1: Multi-Sensor LoRa Transmitter with Embedded ML Classifier
  ===================================================================================
  Features:
    - DS18B20 Digital Temperature Sensor (1-Wire, non-blocking 12-bit conversion)
    - DFRobot Gravity Analog pH Sensor (with automatic temperature compensation & EEPROM calibration)
    - Embedded Edge ML Classifier: On-chip Decision Tree (reproduced from scikit-learn
      model best_water_quality_model.joblib) classifying water into Optimal, Warning, or Critical
    - SX1278 (RA-02) 433 MHz LoRa Transceiver (SPI, non-blocking interrupt-driven TX via RadioLib)
  
  Target Board:
    - ESP32 (ESP32 Dev Module / 30-pin & 38-pin DevKit with USB-C)

  Required Libraries (Install via Arduino IDE Library Manager):
    1. RadioLib           (by Jan Gromes)
    2. DallasTemperature  (by Miles Burton)
    3. OneWire            (by Paul Stoffregen)
    4. DFRobot_ESP_PH_BY_GREENPONIK (by GreenPonik - search "DFRobot_ESP_PH")
    5. SPI & EEPROM       (Built into the official ESP32 Arduino Board Package)

  Pin Connections (ESP32 GPIOs):
    -------------------------------------------------------------------------
    Component         Pin Name       ESP32 GPIO   Notes
    -------------------------------------------------------------------------
    SX1278 (RA-02)    NSS / CS       GPIO 5       SPI Chip Select
    SX1278 (RA-02)    SCK            GPIO 18      VSPI SCK
    SX1278 (RA-02)    MISO           GPIO 19      VSPI MISO
    SX1278 (RA-02)    MOSI           GPIO 23      VSPI MOSI
    SX1278 (RA-02)    RST            GPIO 27      Hardware Reset
    SX1278 (RA-02)    DIO0           GPIO 26      TX / RX Done Interrupt
    SX1278 (RA-02)    VCC / GND      3.3V / GND   *DO NOT connect 5V to RA-02*
    -------------------------------------------------------------------------
    DS18B20           DATA (DQ)      GPIO 4       Requires 4.7k pull-up to 3.3V
    DS18B20           VCC / GND      3.3V / GND
    -------------------------------------------------------------------------
    DFRobot pH Meter  A / Signal     GPIO 35      ADC1_CH7 (Analog Input only)
    DFRobot pH Meter  VCC / GND      3.3V / GND   Or 5V depending on probe board
    -------------------------------------------------------------------------

  LoRa Packet Format (ASCII CSV):
      SG1,<deviceId>,<sequence>,<temperatureC>,<pH>,<waterStatus>
  Example:
      SG1,NODE01,42,28.56,7.82,Optimal
      SG1,NODE01,43,26.10,7.60,Warning
      SG1,NODE01,44,-127.00,7.14,Critical
      (If temperature sensor is disconnected, temperature sends -127.00 and status is Critical)

  Serial pH Calibration Commands (Set Serial Monitor to 115200 baud, "Both NL & CR"):
      enterph -> Enter calibration mode
      calph   -> Calibrate with standard buffer solution (4.0 or 7.0 auto-detected)
      exitph  -> Save calibration values to EEPROM and exit calibration mode
  ===================================================================================
*/

#include <Arduino.h>
#include <SPI.h>
#include <RadioLib.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DFRobot_ESP_PH.h>
#include <EEPROM.h>
#include "WaterQualityModel.h"

// ============================ USER CONFIGURATION ============================
// --- Pin Definitions ---
#define PIN_LORA_SCK       18   // VSPI SCK
#define PIN_LORA_MISO      19   // VSPI MISO
#define PIN_LORA_MOSI      23   // VSPI MOSI
#define PIN_LORA_NSS        5   // RA-02 Chip Select (NSS)
#define PIN_LORA_RST       27   // RA-02 Reset
#define PIN_LORA_DIO0      26   // RA-02 DIO0 (TX done interrupt)
#define PIN_DS18B20         4   // DS18B20 DATA (4.7k pull-up to 3.3V)
#define PIN_PH             35   // DFRobot Analog pH Signal (ESP32 ADC1 Channel 7)

// --- pH ADC Parameters ---
#define ESPADC             4096.0f   // ESP32 12-bit ADC resolution (0..4095)
#define ESPVOLTAGE         3300.0f   // ESP32 reference voltage in millivolts (3300 mV)

// --- Packet Identity ---
const char DEVICE_ID[] = "NODE01";

// --- Timing (milliseconds) ---
const uint32_t SEND_INTERVAL_MS    = 5000;  // Interval between sensor transmissions (5s)
const uint32_t CONVERSION_WAIT_MS  = 800;   // DS18B20 12-bit conversion time (~750 ms)
const uint32_t TX_TIMEOUT_MS       = 3000;  // RadioLib TX timeout threshold
const uint32_t RADIO_RETRY_MS      = 5000;  // Non-blocking radio init retry interval

// --- LoRa Radio Settings (MUST MATCH RECEIVER CONFIG) ---
#define LORA_FREQ_MHZ      433.5   // Carrier Frequency (MHz)
#define LORA_BW_KHZ        125.0   // Signal Bandwidth (kHz)
#define LORA_SF            9       // Spreading Factor (6..12)
#define LORA_CR            5       // Coding Rate: 5 => 4/5
#define LORA_SYNC_WORD     0x12    // Sync Word (0x12 for private network)
#define LORA_PREAMBLE      8       // Preamble Length (symbols)
#define LORA_POWER_DBM     10      // Output Power (10 dBm = 10 mW)
// ============================================================================

// Sensor & Radio Objects
OneWire oneWire(PIN_DS18B20);
DallasTemperature sensors(&oneWire);
DFRobot_ESP_PH ph;
SPISettings loraSpiSettings(1000000, MSBFIRST, SPI_MODE0); // 1 MHz conservative clock for clean breadboard SPI
SX1278 radio = new Module(PIN_LORA_NSS, PIN_LORA_DIO0, PIN_LORA_RST, RADIOLIB_NC, SPI, loraSpiSettings);

// Interrupt Flag for LoRa Non-blocking TX
volatile bool txDoneFlag = false;
void IRAM_ATTR onTxDone() {
  txDoneFlag = true;
}

// State Machine
enum State { ST_IDLE, ST_CONVERTING, ST_SENDING };
State state = ST_IDLE;

// Runtime Tracking Variables
bool     radioReady       = false;
uint32_t seqNumber        = 0;
uint32_t cycleStartMs     = 0;
uint32_t txStartMs        = 0;
uint32_t lastRadioTry     = 0;
uint32_t lastPHSampleMs   = 0;
uint32_t okCount          = 0;
uint32_t failCount        = 0;
uint32_t sensorErrCount   = 0;

const uint8_t REINIT_AFTER_FAILS = 3;
uint8_t consecutiveFails = 0;

// Sensor Readings Cache
float currentTemperature = 25.0f; // Default 25.0 C for compensation if temp sensor disconnected
float currentVoltage     = 1500.0f; // Probe voltage in mV
float currentPH          = 7.0f;
bool  tempSensorOk       = false;

// ----------------------------------------------------------------------------
// Helper: Measure pH analog voltage with oversampling to reduce ESP32 ADC noise
// ----------------------------------------------------------------------------
float readPHVoltage() {
  long sum = 0;
  const int NUM_SAMPLES = 10;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(PIN_PH);
    delayMicroseconds(500); // 500us spacing between samples
  }
  float avgRaw = (float)sum / (float)NUM_SAMPLES;
  return (avgRaw / ESPADC) * ESPVOLTAGE;
}

// ----------------------------------------------------------------------------
// Helper: Track transmission failures and schedule re-init if radio hangs
// ----------------------------------------------------------------------------
void noteFailure() {
  failCount++;
  consecutiveFails++;
  if (consecutiveFails >= REINIT_AFTER_FAILS) {
    Serial.println(F("[LoRa] Repeated failures: scheduling radio re-initialization..."));
    consecutiveFails = 0;
    radioReady = false;
    lastRadioTry = millis() - RADIO_RETRY_MS; // Trigger immediate retry
    state = ST_IDLE;
  }
}

// ----------------------------------------------------------------------------
// Helper: Initialize the SX1278 LoRa transceiver
// ----------------------------------------------------------------------------
bool initRadio() {
  // Ensure NSS starts unasserted (HIGH)
  pinMode(PIN_LORA_NSS, OUTPUT);
  digitalWrite(PIN_LORA_NSS, HIGH);

  // Perform clean hardware reset on SX1278
  pinMode(PIN_LORA_RST, OUTPUT);
  digitalWrite(PIN_LORA_RST, LOW);
  delay(10);
  digitalWrite(PIN_LORA_RST, HIGH);
  delay(20);

  // Initialize VSPI bus without passing NSS (RadioLib handles NSS manually)
  SPI.begin(PIN_LORA_SCK, PIN_LORA_MISO, PIN_LORA_MOSI);

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
    Serial.println(F("        Verify wiring (NSS, RST, DIO0, SCK, MISO, MOSI) and 3.3V power."));
    return false;
  }

  st = radio.setCRC(true);
  if (st != RADIOLIB_ERR_NONE) {
    Serial.print(F("FAILED to enable CRC, code "));
    Serial.println(st);
    return false;
  }

#if defined(RADIOLIB_VERSION_MAJOR) && (RADIOLIB_VERSION_MAJOR >= 7)
  radio.setDio0Action(onTxDone, RISING);
#else
  radio.setPacketSentAction(onTxDone);
#endif
  Serial.println(F("OK"));
  Serial.print(F("[LoRa] Config: "));
  Serial.print(LORA_FREQ_MHZ, 3);
  Serial.print(F(" MHz, BW "));
  Serial.print(LORA_BW_KHZ, 0);
  Serial.print(F(" kHz, SF"));
  Serial.print(LORA_SF);
  Serial.print(F(", CR 4/"));
  Serial.print(LORA_CR);
  Serial.print(F(", Sync 0x"));
  Serial.print(LORA_SYNC_WORD, HEX);
  Serial.print(F(", Power "));
  Serial.print(LORA_POWER_DBM);
  Serial.println(F(" dBm"));
  return true;
}

// ============================================================================
// SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println(F("============================================================="));
  Serial.println(F("  ShrimpGuard Node 1: DS18B20 + pH + LoRa Transmitter"));
  Serial.println(F("============================================================="));
  Serial.print(F("Device ID: "));
  Serial.println(DEVICE_ID);

  // 1. Initialize pH Sensor & Flash EEPROM
  pinMode(PIN_PH, INPUT);
  EEPROM.begin(32); // Reserve 32 bytes for pH calibration coefficients in flash
  ph.begin();
  Serial.println(F("[pH] Sensor initialized."));
  Serial.println(F("[pH] Send 'enterph', 'calph', or 'exitph' via Serial Monitor to calibrate."));

  // 2. Initialize DS18B20 Temperature Sensor
  sensors.begin();
  sensors.setResolution(12);
  sensors.setWaitForConversion(false); // Non-blocking conversion mode
  uint8_t found = sensors.getDeviceCount();
  Serial.print(F("[DS18B20] Devices found: "));
  Serial.println(found);
  if (found == 0) {
    Serial.println(F("[DS18B20] WARNING: No sensor detected. Check VCC, GND, DATA and 4.7k pull-up."));
  }

  // 3. Initialize LoRa Radio
  radioReady   = initRadio();
  lastRadioTry = millis();

  // Start initial reading immediately
  cycleStartMs = millis() - SEND_INTERVAL_MS;
}

// ============================================================================
// LOOP
// ============================================================================
void loop() {
  uint32_t now = millis();

  // 1. Process pH Calibration Commands from Serial Monitor continuously
  ph.calibration(currentVoltage, currentTemperature);

  // 2. Refresh pH voltage every 1 second so calibration always has fresh data
  if (now - lastPHSampleMs >= 1000) {
    lastPHSampleMs = now;
    currentVoltage = readPHVoltage();
    currentPH = ph.readPH(currentVoltage, currentTemperature);
  }

  // 3. Non-blocking LoRa retry if radio failed to initialize earlier
  if (!radioReady) {
    if (now - lastRadioTry >= RADIO_RETRY_MS) {
      lastRadioTry = now;
      radioReady = initRadio();
    }
    // Crucial bugfix: DO NOT exit loop here. Sensors and calibration continue running!
  }

  // 4. Main Telemetry State Machine
  switch (state) {
    case ST_IDLE:
      if (now - cycleStartMs >= SEND_INTERVAL_MS) {
        cycleStartMs = now;
        sensors.requestTemperatures(); // Trigger non-blocking DS18B20 conversion
        state = ST_CONVERTING;
      }
      break;

    case ST_CONVERTING:
      if (now - cycleStartMs >= CONVERSION_WAIT_MS) {
        // --- Read DS18B20 Temperature ---
        float tempC = sensors.getTempCByIndex(0);
        tempSensorOk = (tempC != DEVICE_DISCONNECTED_C) && (tempC != 85.0f) && !isnan(tempC);

        if (tempSensorOk) {
          currentTemperature = tempC;
          Serial.print(F("[DS18B20] Temperature: "));
          Serial.print(currentTemperature, 2);
          Serial.println(F(" °C"));
        } else {
          sensorErrCount++;
          currentTemperature = 25.0f; // Safe fallback for pH temperature compensation
          Serial.print(F("[DS18B20] WARNING: Sensor read error ("));
          Serial.print(tempC);
          Serial.println(F(" °C). Using 25.0 °C fallback for pH compensation."));
        }

        // --- Read pH with real-time temperature compensation ---
        currentVoltage = readPHVoltage();
        currentPH = ph.readPH(currentVoltage, currentTemperature);

        Serial.print(F("[pH] Voltage: "));
        Serial.print(currentVoltage, 1);
        Serial.print(F(" mV | pH: "));
        Serial.println(currentPH, 2);

        // --- ML Water Quality Classification ---
        float modelTemp = tempSensorOk ? currentTemperature : -127.0f;
        WaterStatus waterStatus = predictWaterQuality(modelTemp, currentPH);
        const char* statusStr = waterStatusToString(waterStatus);

        Serial.print(F("[ML Model] Status: "));
        Serial.print(statusStr);
        if (waterStatus == WATER_OPTIMAL) {
          Serial.println(F(" (Optimal water quality)"));
        } else if (waterStatus == WATER_WARNING) {
          Serial.println(F(" (Warning: Suboptimal conditions detected)"));
        } else {
          Serial.println(F(" (CRITICAL: Extreme conditions or sensor fault!)"));
        }

        // --- Construct LoRa Telemetry Packet ---
        char packet[80];
        snprintf(packet, sizeof(packet), "SG1,%s,%lu,%.2f,%.2f,%s",
                 DEVICE_ID,
                 (unsigned long)seqNumber,
                 tempSensorOk ? currentTemperature : -127.0f,
                 currentPH,
                 statusStr);

        Serial.print(F("[LoRa] Packet: "));
        Serial.println(packet);

        // --- Transmit via LoRa ---
        if (radioReady) {
          txDoneFlag = false;
          int16_t st = radio.startTransmit(packet); // Non-blocking transmit
          if (st != RADIOLIB_ERR_NONE) {
            noteFailure();
            Serial.print(F("[LoRa] TX start FAILED, code "));
            Serial.println(st);
            seqNumber++;
            state = ST_IDLE;
          } else {
            txStartMs = now;
            state = ST_SENDING;
          }
        } else {
          Serial.println(F("[LoRa] Radio not ready, packet transmission skipped."));
          seqNumber++;
          state = ST_IDLE;
        }
      }
      break;

    case ST_SENDING:
      if (txDoneFlag) {
        txDoneFlag = false;
        radio.finishTransmit();
        okCount++;
        consecutiveFails = 0;

        Serial.print(F("[LoRa] TX done, seq "));
        Serial.print(seqNumber);
        Serial.print(F(" (ok="));
        Serial.print(okCount);
        Serial.print(F(" fail="));
        Serial.print(failCount);
        Serial.print(F(" sensorErr="));
        Serial.print(sensorErrCount);
        Serial.println(F(")"));

        seqNumber++;
        state = ST_IDLE;
      } else if (now - txStartMs >= TX_TIMEOUT_MS) {
        noteFailure();
        Serial.println(F("[LoRa] ERROR: TX timeout (no DIO0 interrupt received)."));
        radio.finishTransmit();
        seqNumber++;
        state = ST_IDLE;
      }
      break;
  }
}

