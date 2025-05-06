/*
  For ESP32 UWB or ESP32 UWB Pro
*/

#include <SPI.h>
#include <DW1000Ranging.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "link.h"

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23
#define DW_CS 4
#define PIN_RST 27
#define PIN_IRQ 34

const char *ssid = "UWB-WIFI";
const char *password = "12345678";
String tagID = "T0001";

struct MyLink *uwb_data;
String all_json = "";

enum EstadoTag { REPOSO, ESPERA_ALEATORIA, LECTURA };
EstadoTag estado = REPOSO;

static unsigned long tiempo3Anchors = 0;
unsigned long tiempoInicio = 0;
unsigned long esperaFija = 6000;
unsigned long esperaAleatoria = 0;

void setup()
{
    Serial.begin(115200);

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected");
    Serial.print("IP Address:");
    Serial.println(WiFi.localIP());

    // Init UWB
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    DW1000Ranging.initCommunication(PIN_RST, DW_CS, PIN_IRQ);
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachNewDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);

    DW1000Ranging.startAsTag("C8:2C:2A:FF:FE:11:06:5E", DW1000.MODE_LONGDATA_RANGE_LOWPOWER);

    uwb_data = init_link();
    randomSeed(esp_random());
}

void loop()
{
    DW1000Ranging.loop();

    switch (estado)
    {
        case REPOSO:
            if (millis() - tiempoInicio > esperaFija) {
                esperaAleatoria = random(100, 500);
                tiempoInicio = millis();
                estado = ESPERA_ALEATORIA;
                Serial.println("-> Espera aleatoria");
            }
            break;

        case ESPERA_ALEATORIA:
            if (millis() - tiempoInicio > esperaAleatoria) {
                Serial.println("-> Empieza lectura de anchors");
                while (uwb_data->next != NULL) {
                    delete_link(uwb_data, uwb_data->next->anchor_addr);
                }
                tiempo3Anchors = 0;
                estado = LECTURA;
            }
            break;

        case LECTURA:
            if (contarAnchors(uwb_data) >= 3) {
                if (tiempo3Anchors == 0) tiempo3Anchors = millis();

                if (millis() - tiempo3Anchors >= 500) {
                    make_link_json(uwb_data, &all_json, tagID);
                    Serial.println("======= JSON generado =======");
                    Serial.println(all_json);
                    send_post(&all_json);
                    Serial.println("======= Enviado ==========");

                    estado = REPOSO;
                    tiempoInicio = millis();  
                }
            }
            break;
    }
}

void newRange()
{
    uint16_t anchorAddr = DW1000Ranging.getDistantDevice()->getShortAddress();
    float rawRange = DW1000Ranging.getDistantDevice()->getRange();
    float dbm = DW1000Ranging.getDistantDevice()->getRXPower();
    float calibratedRange = calibrateRange(rawRange);

    Serial.print("-> Lectura: anchor ");
    Serial.print(anchorAddr, HEX);
    Serial.print(" | calibrado: ");
    Serial.print(calibratedRange);
    Serial.print(" m | dBm: ");
    Serial.println(dbm);

    if (estado == LECTURA) {
        if (calibratedRange > 0.1 && find_link(uwb_data, anchorAddr) == NULL) {
            add_link(uwb_data, anchorAddr);
            Serial.println("-> Anchor NUEVO detectado");
        }

        fresh_link(uwb_data, anchorAddr, calibratedRange, dbm);
    }
}

void newDevice(DW1000Device *device)
{
    Serial.print("ranging init; 1 device added -> ");
    Serial.print(" short:");
    Serial.println(device->getShortAddress(), HEX);

    add_link(uwb_data, device->getShortAddress());
}

void inactiveDevice(DW1000Device *device)
{
    Serial.print("delete inactive device: ");
    Serial.println(device->getShortAddress(), HEX);

    delete_link(uwb_data, device->getShortAddress());
}

void send_post(String *msg_json)
{
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin("http://192.168.0.100:5000/api/distancias/registrar");
        http.addHeader("Content-Type", "application/json");

        int httpResponseCode = http.POST(*msg_json);
        Serial.print("POST status: ");
        Serial.println(httpResponseCode);

        http.end();
    } else {
        Serial.println("WiFi no conectado");
    }
}

float calibrateRange(float raw) {
    float gain = 0.8475;
    float offset = -0.5255;
    return raw * gain + offset;
}
