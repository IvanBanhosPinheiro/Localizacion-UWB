#include <SPI.h>
#include "DW1000Ranging.h"
#include "DW1000.h"

const int PIN_RST = 27;  // Reset pin
const int PIN_IRQ = 34;  // IRQ pin
const int PIN_SS = 4;    // Chip select

// Cambia esta dirección por una única para cada Anchor
char ANCHOR_ADDRESS[] = "82:17:5B:D5:A9:9A:A3:03";
//"82:17:5B:D5:A9:9A:A1:01"  // Anchor 1
//"82:17:5B:D5:A9:9A:A2:02"  // Anchor 2
//"82:17:5B:D5:A9:9A:A3:03"  // Anchor 3

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Anchor setup...");

  // Inicializar el módulo DW1000
  DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ); // Reset, CS, IRQ
  DW1000.setShortAddress(0xA003);
  //anchor 1  0xA001
  //anchor 2 0xA002...
  DW1000Ranging.attachNewRange(newRange);
  DW1000Ranging.attachNewDevice(newDevice);
  DW1000Ranging.attachInactiveDevice(inactiveDevice);

  // Definir este módulo como Anchor
  DW1000Ranging.startAsAnchor(ANCHOR_ADDRESS, DW1000.MODE_LONGDATA_RANGE_LOWPOWER, false);
}

void loop() {
  DW1000Ranging.loop();
}

void newRange() {
  Serial.print("from: ");
  Serial.print(DW1000Ranging.getDistantDevice()->getShortAddress(), HEX);
  Serial.print("\tRange: ");
  Serial.print(DW1000Ranging.getDistantDevice()->getRange());
  Serial.println(" m");
}

void newDevice(DW1000Device *device) {
  Serial.print("Device added: ");
  Serial.println(device->getShortAddress(), HEX);
}

void inactiveDevice(DW1000Device *device) {
  Serial.print("Device inactive: ");
  Serial.println(device->getShortAddress(), HEX);
}
