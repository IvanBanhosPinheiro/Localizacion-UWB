#include <SPI.h>
#include "DW1000Ranging.h"
#include "DW1000.h"

// Pines ESP32 UWB
const uint8_t PIN_RST = 27;
const uint8_t PIN_IRQ = 34;
const uint8_t PIN_SS = 4;

// Dirección única de este Tag (MAC UWB)
char TAG_ADDRESS[] = "82:17:5B:D5:A9:9A:E3:01";

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Iniciando Tag...");

  // Inicializar SPI y UWB
  SPI.begin();
  DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ);
  DW1000Ranging.attachNewRange(newRange);
  DW1000Ranging.attachNewDevice(newDevice);
  DW1000Ranging.attachInactiveDevice(inactiveDevice);

  // Iniciar como Tag
  DW1000Ranging.startAsTag(TAG_ADDRESS, DW1000.MODE_LONGDATA_RANGE_LOWPOWER);
}

void loop() {
  DW1000Ranging.loop();
}

void newRange() {
  DW1000Device* dev = DW1000Ranging.getDistantDevice();
  float distancia = dev->getRange();

  // Obtener la MAC larga del Anchor
  byte* mac = dev->getByteAddress();

  // Mostrar los últimos 2 bytes como identificador
  Serial.print("Anchor ID (MAC): ");
  for (int i = 6; i < 8; i++) {
    if (mac[i] < 16) Serial.print("0");  // padding con 0
    Serial.print(mac[i], HEX);
    if (i == 6) Serial.print(":");
  }

  Serial.print("  |  Distancia: ");
  Serial.print(distancia);
  Serial.println(" m");
}



void newDevice(DW1000Device* device) {
  Serial.println("Nuevo Anchor detectado");
}

void inactiveDevice(DW1000Device* device) {
  Serial.println("Anchor desconectado o inactivo");
}
