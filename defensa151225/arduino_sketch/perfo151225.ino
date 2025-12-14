#include <M5Unified.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <string.h> 

// ---------------------------------------------
// --- 1. CONFIGURACIÓN DE RED ---
// ---------------------------------------------
const char* ssid = "xxxx";
const char* password = "xxxx";

// Destino Pure Data/PlugData (OSC Bundle)
IPAddress outIp(192, 168, 0, 7); // IP de la PC 
const unsigned int outPort = 9000;    // Puerto de escucha de PlugData
const unsigned int localPort = 8888;  // Puerto de envío del Ataraxio

// --- CONFIGURACIÓN PARA EL MONITOR DE PYTHON ---
IPAddress monitorIp(192, 168, 0, 7); 
const unsigned int monitorPort = 12345; // Puerto que espera el script Python

WiFiUDP Udp;

// Intervalo para el parpadeo del LED (5 segundos = 5000 ms)
const unsigned long LED_BLINK_INTERVAL = 5000;
unsigned long lastLedTime = 0;

// Variables para la lectura del GSR
const int GSR_PIN = 36; 
int gsrValue = 0;

// Intervalo de envío de datos OSC (cada 100 ms)
const unsigned long SEND_INTERVAL = 100; 
unsigned long lastSendTime = 0;

// ---------------------------------------------
// --- 2. DECLARACIÓN DE FUNCIONES ---
// ---------------------------------------------
void sendButtonOSC(const char* address, int value); 
void sendSensorsOSC(int gsr);
void sendGSRtoMonitor(int gsr);


// ---------------------------------------------
// --- 3. SETUP ---
// ---------------------------------------------
void setup() {
    auto cfg = M5.config();
    M5.begin(cfg); 

    Serial.begin(115200);

    // Configuración ADC (necesaria para el rango 0-4095)
    analogSetAttenuation(ADC_11db); 
    analogSetWidth(12);             
    
    // Conexión Wi-Fi 
    M5.Lcd.setRotation(1);
    M5.Lcd.fillScreen(TFT_BLACK);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.setTextColor(TFT_WHITE);
    M5.Lcd.setTextSize(2);
    M5.Lcd.print("Conectando...");
    
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    M5.Lcd.setCursor(0, 20);
    M5.Lcd.print("IP:");
    M5.Lcd.print(WiFi.localIP());
    Serial.println("\nConectado a la red Wi-Fi.");
    Serial.print("Direccion IP local: ");
    Serial.println(WiFi.localIP());
    
    M5.Imu.init();
    Udp.begin(localPort);
    M5.Lcd.sleep(); 
}

// ---------------------------------------------
// --- 4. LOOP ---
// ---------------------------------------------
void loop() {
    // 4.1. LECTURA DE BOTONES (Envío Separado e Inmediato - CON DEBUG)
    M5.update(); 
    
    // Botón A (Verificamos si este evento se activa)
    if (M5.BtnA.wasPressed()) {
        sendButtonOSC("/btn/a_gpio37", 1); // RUTA DE DEBUG
    }
    
    // Botón B (Verificamos si este evento se activa)
    if (M5.BtnB.wasPressed()) {
        sendButtonOSC("/btn/b_gpio39", 1); // RUTA DE DEBUG
    }

    // Botón C (M5.BtnPWR)
    if (M5.BtnPWR.wasPressed()) { 
        sendButtonOSC("/btn/c_pwr", 1); // RUTA DE DEBUG
    }

    // 4.2. ENVÍO PERIÓDICO DE SENSORES
    if (millis() - lastSendTime > SEND_INTERVAL) {
        lastSendTime = millis();
        
        // LECTURA GSR
        gsrValue = analogRead(GSR_PIN);
        
        // 1. Envío OSC Bundle (SÓLO GSR y IMU)
        sendSensorsOSC(gsrValue); 

        // 2. Envío RAW (Para el Monitor Python)
        sendGSRtoMonitor(gsrValue);
    }

    // 4.3. PARPADEO DEL LED
    if (millis() - lastLedTime > LED_BLINK_INTERVAL) {
        lastLedTime = millis();
        M5.Power.setLed(true); 
        delay(50); 
        M5.Power.setLed(false);
    }
}

// ---------------------------------------------
// --- 5. IMPLEMENTACIÓN DE FUNCIONES OSC Y RAW ---
// ---------------------------------------------

// --- Función: Envío de Botones (Paquete Separado) ---
void sendButtonOSC(const char* address, int value) {
    OSCMessage msg(address);
    msg.add((int32_t)value); 
    Udp.beginPacket(outIp, outPort);
    msg.send(Udp); 
    Udp.endPacket();
    msg.empty();
    
    Serial.printf("Boton %s enviado: %d\n", address, value);
}

// Envío de GSR e IMU (OSC Bundle)
void sendSensorsOSC(int gsr) {
    float accX, accY, accZ;
    float gyrX, gyrY, gyrZ;
    
    M5.Imu.getAccelData(&accX, &accY, &accZ);
    M5.Imu.getGyroData(&gyrX, &gyrY, &gyrZ);
    
    OSCBundle bundle;

    // --- Dato 1: GSR ---
    OSCMessage gsrMsg("/sensor/gsr");
    gsrMsg.add((int32_t)gsr); 
    bundle.add(gsrMsg);

    // --- Dato 2: Giroscopio ---
    OSCMessage gyrMsg("/sensor/gyro");
    gyrMsg.add(gyrY); 
    gyrMsg.add(gyrZ); 
    bundle.add(gyrMsg);
    
    // --- Dato 3: Acelerómetro ---
    OSCMessage accMsg("/sensor/accel");
    accMsg.add(accX);
    accMsg.add(accY);
    accMsg.add(accZ);
    bundle.add(accMsg);

    // Envío del Bundle
    Udp.beginPacket(outIp, outPort);
    bundle.send(Udp);
    Udp.endPacket();

    Serial.printf("GSR: %d | Gyro Y: %.2f\n", gsr, gyrY);
}

// Envío RAW (para el Monitor Python)
void sendGSRtoMonitor(int gsr) {
    char gsr_str[10];
    
    sprintf(gsr_str, "%d", gsr);

    Udp.beginPacket(monitorIp, monitorPort);
    Udp.write((const uint8_t*)gsr_str, strlen(gsr_str));
    Udp.endPacket();
}
