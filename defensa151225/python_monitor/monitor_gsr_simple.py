# -*- coding: utf-8 -*-
# --------------------------------------------------------
# *** SOLUCIÓN CLAVE: FORZAR EL BACKEND TKAGG ***
import matplotlib
matplotlib.use('TkAgg') 
# --------------------------------------------------------
import socket
import threading
import time
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime
import tkinter as tk 

# --- CONFIGURACIÓN DE RED ---
UDP_IP = "0.0.0.0"
UDP_PORT = 12345    

# --- CONFIGURACIÓN DE VISUALIZACIÓN ---
MAX_POINTS = 40  
SAMPLE_RATE = 10
WINDOW_DURATION = MAX_POINTS / SAMPLE_RATE

# --- ALMACENAMIENTO DE DATOS ---
FILENAME = f"gsr_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

try:
    csv_file = open(FILENAME, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Timestamp (ms)', 'GSR_Raw', 'Timestamp (HH:MM:SS.mmm)'])
except Exception as e:
    print(f"Error al abrir el archivo CSV: {e}")
    csv_file = None


# --- VARIABLES GLOBALES Y LOCKS ---
data_time = deque(maxlen=MAX_POINTS)
data_gsr = deque(maxlen=MAX_POINTS)
latest_gsr_value = 0
current_time_offset = 0.0
data_lock = threading.Lock()
is_data_received = threading.Event() 

# --- FUNCIÓN DE RECEPCIÓN DE DATOS UDP (Hilo separado) ---
def udp_listener():
    global latest_gsr_value, current_time_offset
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((UDP_IP, UDP_PORT))
        print(f"UDP Listener iniciado en {UDP_IP}:{UDP_PORT}")
        if csv_file:
            print(f"Los datos se guardarán en: {FILENAME}")
    except OSError as e:
        print(f"ERROR: No se pudo iniciar el socket UDP en el puerto {UDP_PORT}. {e}")
        print("Verifica si otro programa está usando el puerto o si el firewall está bloqueando la conexión.")
        return

    while True:
        try:
            sock.settimeout(1.0) 
            data, addr = sock.recvfrom(1024)
            
            try:
                gsr_raw_str = data.decode().strip() 
                gsr_raw = int(gsr_raw_str)
            except ValueError:
                continue
            
            current_time_ms = int(time.time() * 1000)
            
            with data_lock:
                latest_gsr_value = gsr_raw
                
                current_time_offset += 1.0 / SAMPLE_RATE 
                data_time.append(current_time_offset)
                data_gsr.append(gsr_raw)

                if not is_data_received.is_set():
                    is_data_received.set()

                if csv_file:
                    timestamp_readable = datetime.fromtimestamp(current_time_ms / 1000).strftime('%H:%M:%S.%f')[:-3]
                    csv_writer.writerow([current_time_ms, gsr_raw, timestamp_readable])
                    csv_file.flush() 
                
        except socket.timeout:
            continue
        except Exception as e:
            time.sleep(0.5)
            continue


# --- FUNCIÓN DE ACTUALIZACIÓN DEL GRÁFICO ---
def animate_plot(i, ax, line):
    global data_gsr, data_time

    if not is_data_received.is_set():
        return line,
    
    with data_lock:
        current_latest_value = latest_gsr_value
        current_data_time = list(data_time)
        current_data_gsr = list(data_gsr)

    if current_data_gsr:
        
        line.set_data(current_data_time, current_data_gsr)

        x_max = current_data_time[-1]
        
        if x_max < WINDOW_DURATION:
            x_min = 0
            ax.set_xlim(x_min, WINDOW_DURATION) 
        else:
            x_min = x_max - WINDOW_DURATION
            ax.set_xlim(x_min, x_max) 

        # MODIFICACIÓN CLAVE: SÓLO mostrar el valor RAW (número)
        ax.set_title(f"{current_latest_value}", 
                     fontsize=12, color='white')

        if len(current_data_gsr) > 1:
            
            filtered_data = [d for d in current_data_gsr if d < 4095]
            
            current_min = min(current_data_gsr)
            current_max = max(filtered_data) if filtered_data else current_min
            
            padding = 50 
            
            y_min = max(0, current_min - padding)
            y_max = min(4095, current_max + padding)
            
            if y_max - y_min < 200:
                 y_max = y_min + 200 
            
            if current_max == current_min:
                ax.set_ylim(current_min - 100, current_max + 100)
            else:
                ax.set_ylim(y_min, y_max)
        
    return line,


# --- FUNCIÓN PRINCIPAL ---
def main():
    listener_thread = threading.Thread(target=udp_listener, daemon=True)
    listener_thread.start()
    
    # 2. Configurar el gráfico de Matplotlib
    
    # OCULTAR LA BARRA DE HERRAMIENTAS
    plt.rcParams['toolbar'] = 'None'
    
    # AJUSTE DE ASPECT RATIO A 2:1 (4:2)
    fig, ax = plt.subplots(figsize=(6, 3)) 
    
    # CÁLCULO PARA EL CENTRADO INICIAL
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    
    figure_width = int(fig.get_size_inches()[0] * fig.dpi)
    figure_height = int(fig.get_size_inches()[1] * fig.dpi)
    
    center_x = int(screen_width / 2 - figure_width / 2)
    center_y = int(screen_height / 2 - figure_height / 2)
    
    fig.canvas.manager.window.wm_geometry(f"{figure_width}x{figure_height}+{center_x}+{center_y}")
    fig.canvas.manager.set_window_title('Monitor GSR - Mover por la Barra de Título')
    
    # AJUSTE: Fondo de la figura y del área de trazado a negro
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Configuración inicial de la línea del gráfico
    line, = ax.plot([], [], color='#00FF00', linewidth=2) 
    
    # Estilo del gráfico
    ax.set_xlabel("Tiempo Relativo (segundos)")
    ax.set_ylabel("GSR Raw Value (0 - 4095)")
    
    # AJUSTE: Color de etiquetas y bordes a blanco
    ax.tick_params(colors='white', which='both')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    
    # AJUSTE: Rejilla a verde oscuro y menos intrusiva
    ax.grid(True, linestyle='-', alpha=0.3, color='#005500') 
    
    ax.set_xlim(0, WINDOW_DURATION) 
    ax.set_ylim(0, 4095) 

    # *** AJUSTE PARA EVITAR EL CORTE DE TÍTULOS Y EJES ***
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.18, left=0.15, right=0.95) 

    # 3. Iniciar la animación
    ani = animation.FuncAnimation(fig, animate_plot, fargs=(ax, line), interval=50, 
                                  blit=False, cache_frame_data=False)
    
    try:
        plt.show() 
    except KeyboardInterrupt:
        print("Programa detenido por el usuario.")
    finally:
        if csv_file:
            csv_file.close()
            print(f"Datos guardados y archivo CSV cerrado: {FILENAME}")

if __name__ == "__main__":
    main()
