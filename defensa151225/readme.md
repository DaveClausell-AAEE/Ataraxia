# 🔊 Sonificación de datos biométricos para performance

## 📜 Descripción del proyecto

Este repositorio contiene los códigos, datos y materiales utilizados en la defensa del proyecto de sonificación interactiva. El objetivo es transformar en tiempo real datos fisiológicos y cinéticos —específicamente la **Actividad Electrodérmica (GSR)** y el **movimiento (IMU)** del intérprete— en parámetros musicales dentro de un entorno de performance.

El proyecto establece un puente de comunicación entre el hardware embebido (M5StickC Plus) y el software de audio modular (PlugData/Pure Data) para crear una experiencia sonora íntima y reactiva.

## ⚙️ Componentes principales

| Componente | Función | Protocolo de Comunicación |
| :--- | :--- | :--- |
| **Hardware:** Ataraxio (M5StickC Plus) | Captura de GSR (GPIO 36), Giroscopio/Acelerómetro (IMU) y Botones A/B. | Wi-Fi (UDP) |
| **Software de Audio:** PlugData (Pure Data) | Síntesis y mapeo sonoro. | OSC (Puerto 9000) |
| **Monitor:** Script Python (`monitor_gsr_simple.py`) | Visualización de la señal GSR en tiempo real (Overlay). | UDP RAW (Puerto 12345) |

## 📁 Estructura del repositorio

* **`arduino_sketch/`**: Contiene el código fuente [`perfo151225.ino`](https://github.com/DaveClausell-AAEE/Ataraxia/blob/main/defensa151225/arduino_sketch/perfo151225.ino)) para el M5StickC Plus. **Configurado para enviar triggers de botón inmediatos y Bundle OSC de sensores.**
* **`python_monitor/`**: Contiene el [`script`](https://github.com/DaveClausell-AAEE/Ataraxia/blob/main/defensa151225/python_monitor/monitor_gsr_simple.py) de Python para el gráfico de superposición (overlay) en la pantalla de la PC.
* **`datos_brutos/`**: Contiene los 17 archivos `.txt` utilizados como material base para el proyecto.
* **`presentacion/`**: Aquí está el [`Archivo`](https://docs.google.com/presentation/d/1YtMcYzQz4fGydjKO6RjqkxTPxsvQdVR4jOSPMc58np8/edit?usp=sharing) de la presentación final del proyecto (Google Slides).

## ▶️ Rutas OSC clave (para plugData)

| Dato | Ruta OSC | Tipo de Envío | Uso |
| :--- | :--- | :--- | :--- |
| **Activación Fisiológica** | `/sensor/gsr` | Bundle | Mapeo directo al tempo de ejecución del patch de ambient. |
| **Movimiento / Rotación** | `/sensor/gyro` | Bundle | Mapeo a control de volúmen de la sonificación de datos. |
| **Trigger Botón A** | `/btn/a` | Paquete Separado | Inicio de performance. |
| **Trigger Botón B** | `/btn/b` | Paquete Separado | Activa/desactiva el DSP. |
