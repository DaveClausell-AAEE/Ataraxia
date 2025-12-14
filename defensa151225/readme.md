# 🔊 Sonificación de Datos Biométricos para Performance

## 📜 Descripción del Proyecto

Este repositorio contiene los códigos, datos y materiales utilizados en la defensa del proyecto de sonificación interactiva. El objetivo es transformar en tiempo real datos fisiológicos y cinéticos —específicamente la **Actividad Electrodérmica (GSR)** y el **movimiento (IMU)** del intérprete— en parámetros musicales dentro de un entorno de performance.

El proyecto establece un puente de comunicación robusto entre el hardware embebido (M5StickC Plus) y el software de audio modular (PlugData/Pure Data) para crear una experiencia sonora íntima y reactiva.

## ⚙️ Componentes Principales

| Componente | Función | Protocolo de Comunicación |
| :--- | :--- | :--- |
| **Hardware:** Ataraxio (M5StickC Plus) | Captura de GSR (GPIO 36), Giroscopio/Acelerómetro (IMU) y Botones A/B. | Wi-Fi (UDP) |
| **Software de Audio:** PlugData (Pure Data) | Síntesis y mapeo sonoro. | OSC (Puerto 9000) |
| **Monitor:** Script Python (`monitor_gsr_simple.py`) | Visualización de la señal GSR en tiempo real (Overlay). | UDP RAW (Puerto 12345) |

## 📁 Estructura del Repositorio

* **`arduino_sketch/`**: Contiene el código fuente (`defensa_gsr_imu.ino`) para el M5StickC Plus. **Configurado para enviar triggers de botón inmediatos y Bundle OSC de sensores.**
* **`python_monitor/`**: Contiene el script de Python para el gráfico de superposición (overlay) en la pantalla del PC, optimizado para una relación de aspecto 2:1 y fondo negro.
* **`datos_brutos/`**: Contiene los 17 archivos `.txt` utilizados como material base o referencia para el proyecto.
* **`presentacion/`**: Archivo PDF de la presentación final del proyecto (Google Slides).

## ▶️ Rutas OSC Clave (Para PlugData)

| Dato | Ruta OSC | Tipo de Envío | Uso |
| :--- | :--- | :--- | :--- |
| **Activación Fisiológica** | `/sensor/gsr` | Bundle | Mapeo directo a Tono, Frecuencia, o Densidad. |
| **Movimiento / Rotación** | `/sensor/gyro` | Bundle | Mapeo a Paneo Estéreo o Modulación de Filtro. |
| **Trigger Botón A** | `/btn/a` | Paquete Separado | Inicio de sección o disparo de sonido. |
| **Trigger Botón B** | `/btn/b` | Paquete Separado | Reset o cambio de *preset*. |
