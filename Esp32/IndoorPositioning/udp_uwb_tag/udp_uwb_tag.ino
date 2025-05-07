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

// Añadimos un estado FINALIZANDO para dar tiempo entre enviar y detener UWB
enum EstadoTag { REPOSO, ESPERA_ALEATORIA, LECTURA, FINALIZANDO };
EstadoTag estado = REPOSO;

static unsigned long tiempo3Anchors = 0;
unsigned long tiempoInicio = 0;
unsigned long tiempoInicioLectura = 0;  // Para controlar timeout de búsqueda
unsigned long esperaFija = 6000;
unsigned long esperaAleatoria = 0;
unsigned long timeoutLectura = 8000 + esperaFija;    // 8 segundos máximo buscando anchors
bool uwbActivo = false;                 // Controla si UWB está activo

void setup()
{
    Serial.begin(115200);
    delay(1000); // Esperar a que el monitor serial esté listo
    Serial.println("\n\n=== ESP32 UWB Tag iniciando ===");

    // Configurar pin de reset como salida
    pinMode(PIN_RST, OUTPUT);
    digitalWrite(PIN_RST, HIGH);

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(ssid, password);
    
    Serial.print("Conectando a WiFi");
    int intentos = 0;
    while (WiFi.status() != WL_CONNECTED && intentos < 20) // Límite de intentos
    {
        delay(500);
        Serial.print(".");
        intentos++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nConectado");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nError al conectar WiFi. Reiniciando...");
        ESP.restart();
    }

    // Init UWB data structure
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    uwb_data = init_link();
    randomSeed(esp_random());
    
    Serial.println("Sistema iniciado en estado REPOSO");
    tiempoInicio = millis();
}

// Función para iniciar UWB
void iniciarUWB() {
    Serial.println("Iniciando UWB...");
    
    // Reiniciar el hardware UWB antes de iniciar
    digitalWrite(PIN_RST, LOW);
    delay(2);
    digitalWrite(PIN_RST, HIGH);
    delay(5);
    
    DW1000Ranging.initCommunication(PIN_RST, DW_CS, PIN_IRQ);
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachNewDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);
    DW1000Ranging.startAsTag("C8:2C:2A:FF:FE:11:06:5E", DW1000.MODE_LONGDATA_RANGE_LOWPOWER);
    uwbActivo = true;
}

// Función mejorada para detener UWB
void detenerUWB() {
    if (uwbActivo) {
        Serial.println("Deteniendo UWB...");
        
        // Pausar procesamiento antes de manipular los handlers
        delay(10);
        
        // Desactivar manejadores de eventos (con control de errores implícito)
        DW1000Ranging.attachNewRange(NULL);
        DW1000Ranging.attachNewDevice(NULL);
        DW1000Ranging.attachInactiveDevice(NULL);
        
        // Pausar procesamiento después de manipular los handlers
        delay(10);
        
        // Reiniciar el hardware para asegurar un estado limpio
        digitalWrite(PIN_RST, LOW);
        delay(2);
        digitalWrite(PIN_RST, HIGH);
        
        uwbActivo = false;
        
        // Limpia lista de anchors con control de errores
        int count = 0;
        while (uwb_data->next != NULL && count < 20) {  // Límite para evitar bucles infinitos
            delete_link(uwb_data, uwb_data->next->anchor_addr);
            count++;
        }
        
        if (count == 20) {
            Serial.println("ADVERTENCIA: Posible bucle en limpieza de anchors");
        }
    }
}

void loop()
{
    // Dar tiempo al sistema para procesar tareas de fondo
    yield();
    
    // Comprobar y reconectar WiFi si es necesario
    if (WiFi.status() != WL_CONNECTED && (estado == REPOSO || estado == ESPERA_ALEATORIA)) {
        Serial.println("WiFi desconectado, reconectando...");
        WiFi.reconnect();
        delay(500);
    }

    // Solo procesamos UWB si está activo
    if (uwbActivo) {
        DW1000Ranging.loop();
    }

    int numAnchors = contarAnchors(uwb_data);

    switch (estado)
    {
        case REPOSO:
            if (millis() - tiempoInicio > esperaFija) {
                esperaAleatoria = random(100, 500);
                tiempoInicio = millis();
                estado = ESPERA_ALEATORIA;
                Serial.println("-> Espera aleatoria");
                
                // Asegurarse que UWB está desactivado
                detenerUWB();
            }
            break;

        case ESPERA_ALEATORIA:
            if (millis() - tiempoInicio > esperaAleatoria) {
                Serial.println("-> Empieza lectura de anchors");
                
                // Activamos UWB para iniciar la lectura
                iniciarUWB();
                
                // Limpiamos cualquier anchor que pudiera quedar en la lista
                int count = 0;
                while (uwb_data->next != NULL && count < 20) {
                    delete_link(uwb_data, uwb_data->next->anchor_addr);
                    count++;
                }
                
                tiempo3Anchors = 0;
                tiempoInicioLectura = millis();  // Iniciamos contador para timeout
                estado = LECTURA;
            }
            break;

        case LECTURA:
            // Verificar si ha pasado el tiempo límite sin encontrar 3 anchors
            if (millis() - tiempoInicioLectura >= timeoutLectura) {
                Serial.println("-> TIMEOUT: No se encontraron suficientes anchors");
                detenerUWB();
                estado = REPOSO;
                tiempoInicio = millis();
                break;
            }
            
            
            if (numAnchors >= 3) {
                if (tiempo3Anchors == 0) {
                    tiempo3Anchors = millis();
                    Serial.printf("-> 3+ anchors detectados (%d). Esperando confirmación...\n", numAnchors);
                }

                if (millis() - tiempo3Anchors >= 800) {
                    make_link_json(uwb_data, &all_json, tagID);
                    Serial.println("======= JSON generado =======");
                    Serial.println(all_json);
                    
                    // Cambiamos a estado FINALIZANDO antes de enviar
                    estado = FINALIZANDO;
                    tiempoInicio = millis();
                    
                    // Enviamos los datos
                    send_post(&all_json);
                }
            }
            break;
            
        case FINALIZANDO:
            // Si UWB aún está activo, desactivarlo primero
            if (uwbActivo) {
                Serial.println("-> Finalizando: Deteniendo UWB");
                detenerUWB();  // Esto pone uwbActivo = false
            }
            
            // Esperar el tiempo configurado antes de cambiar a REPOSO
            if (millis() - tiempoInicio >= 1000) {
                Serial.println("-> Cambiando a REPOSO");
                estado = REPOSO;
                tiempoInicio = millis();
            }
            break;
    }
}

void newRange()
{
    uint16_t anchorAddr = DW1000Ranging.getDistantDevice()->getShortAddress();
    float rawRange = DW1000Ranging.getDistantDevice()->getRange();
    float dbm = DW1000Ranging.getDistantDevice()->getRXPower();
    float calibratedRange = calibrateRange(rawRange, anchorAddr);

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
    Serial.print("Ranging init; 1 device added -> ");
    Serial.print(" short:");
    Serial.println(device->getShortAddress(), HEX);

    add_link(uwb_data, device->getShortAddress());
}

void inactiveDevice(DW1000Device *device)
{
    Serial.print("Delete inactive device: ");
    Serial.println(device->getShortAddress(), HEX);

    delete_link(uwb_data, device->getShortAddress());
}

// Función mejorada para enviar datos HTTP
void send_post(String *msg_json)
{
    Serial.println("Enviando datos a servidor...");
    
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        
        // Timeout más corto para evitar bloqueos largos
        http.setTimeout(5000);
        
        // Ajustar server según tu configuración
        http.begin("http://192.168.0.100:5000/api/distancias/registrar");
        http.addHeader("Content-Type", "application/json");

        int httpResponseCode = http.POST(*msg_json);
        
        Serial.print("POST status: ");
        Serial.println(httpResponseCode);
        
        // Siempre leer la respuesta para evitar fugas de memoria
        String respuesta = http.getString();
        Serial.print("Respuesta: ");
        if (respuesta.length() > 100) {
            // Imprimir solo los primeros 100 caracteres si es muy grande
            Serial.println(respuesta.substring(0, 100) + "...");
        } else {
            Serial.println(respuesta);
        }
        
        // Cerrar explícitamente la conexión
        http.end();
        Serial.println("======= Enviado ==========");
        //estado = REPOSO;
        //tiempoInicio = millis();
    } else {
        Serial.println("WiFi no conectado. No se pudo enviar.");
    }
}

float calibrateRange(float raw, uint16_t anchorAddr) {
    float gain = 0.520;  // Valor por defecto
    float offset = 0.0; // Valor por defecto
    
    // Calibración específica por anchor
    switch(anchorAddr) {
        case 0x5BA3:  // ID de la primera anchor
            gain = 1.0;
            offset = -0.80;
            break;
        case 0x2219:  // ID de la segunda anchor
            gain = 1.0;
            offset = -1.0;
            break;
        case 0x234B:  // ID de la tercera anchor
            gain = 1.0;
            offset = -0.80;
            break;
    }
    
    return raw * gain + offset;
}