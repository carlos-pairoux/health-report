import psutil
# psutil nos da acceso a métricas del sistema que Python no expone por defecto.
import platform
# platform lo usamos para detectar el SO y adaptar el comportamiento del script.
import socket
# socket permite obtener información de red y comunicarnos mediante protocolos
# como TCP/IP sin depender de herramientas externas.
import subprocess
# subprocess permite ejecutar comandos del sistema operativo desde Python
# y capturar su resultado para procesarlo dentro del programa.

# --- Recursos del sistema ---

def get_cpu_info():
    try:
        return{
            "physical_cores": psutil.cpu_count(logical=False),
            # logical=False devuelve únicamente los núcleos físicos del procesador.
            # Este dato es útil para estimar la capacidad real de procesamiento,
            # ya que tecnologías como Hyper-Threading pueden hacer que el sistema
            # reporte más núcleos lógicos de los que existen físicamente.
            "logical_cores": psutil.cpu_count(logical=True),
            # logical=True incluye todos los hilos que el sistema operativo presenta
            # como unidades de ejecución independientes.
            # Dependiendo de la arquitectura del CPU, este número puede ser mayor
            # que la cantidad de núcleos físicos gracias al multithreading.
            "usage_percent": psutil.cpu_percent(interval=1),
            # cpu_percent() necesita comparar actividad entre dos instantes de tiempo.
            # Por eso usamos interval=1: espera un segundo y mide cuánto trabajó
            # el procesador durante ese período.
            # Sin un intervalo de referencia el valor inicial suele ser poco representativo.
            "frecuency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
            # cpu_freq() devuelve la frecuencia actual del procesador en MHz.
            # Usamos la frecuencia actual y no la máxima porque refleja el estado real
            # del CPU en ese momento.
            # Algunos entornos virtualizados no exponen este dato, por eso verificamos
            # que exista antes de intentar acceder a .current.
        }
    except Exception as e:
        # Si ocurre algún problema al consultar las métricas del sistema,
        # devolvemos el detalle del error para que quien use la función
        # pueda decidir cómo manejarlo sin interrumpir toda la ejecución.
        return {"error": str(e)}

def get_ram_info():
    try:
        ram = psutil.virtual_memory()
        # virtual_memory() devuelve un objeto con información completa sobre la RAM:
        # memoria total, disponible, usada y otros datos que el sistema operativo reporta.
        return {
            "total_gb": round(ram.total / (1024**3), 2),
            # ram.total devuelve bytes, para convertilos en GB se eleva 1024³.
            # El 2 indica que redondeamos a dos decimales el resultado.
            "available_gb": round(ram.available / (1024**3), 2),
            # available representa la memoria que todavía se puede usar sin problemas.
            # No es exactamente lo mismo que memoria libre, porque algunos sistemas usan
            # parte de la RAM como caché y pueden recuperarla cuando haga falta.
            "usage_percent": ram.percent
            # psutil ya calcula directamente el porcentaje de uso de RAM.
            # Usar este valor nos evita tener que hacer el cálculo manualmente
            # a partir de los bytes usados y totales.
        }
    except Exception as e:
        # Si ocurre algún error al leer la información del sistema,
        # devolvemos el mensaje en lugar de generar una excepción
        # que termine la ejecución del programa.
        return {"error": str(e)}

def get_disk_info():
    try:
        disk = psutil.disk_usage("/") if platform.system() != "Windows" else psutil.disk_usage("C:\\")
        # La ruta que representa el disco principal depende del sistema operativo.
        # En Linux y macOS se usa "/", mientras que en Windows normalmente se usa "C:\\".
        # platform.system() permite detectar el entorno actual y elegir la ruta correcta.
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            # disk.total devuelve la capacidad total de la partición analizada en bytes.
            # Se convierte a gigabytes porque es una unidad más práctica para mostrar.
            "free_gb": round(disk.free / (1024**3), 2),
            # disk.free indica cuánto espacio queda disponible actualmente.
            # También se convierte desde bytes para mantener consistencia
            # con el resto de las métricas que se muestran.
            "usage_percent": disk.percent
            # Este valor ya viene calculado por psutil.
            # Representa el porcentaje del almacenamiento que está ocupado
            # respecto al total de la partición seleccionada.
        }
    except Exception as e:
        # Si la consulta al disco falla por permisos, rutas inválidas
        # o cualquier otro problema, devolvemos el error para facilitar
        # el diagnóstico sin romper el script.
        return {"error": str(e)}

# --- Red y procesos ---

def get_network_info():
    try:
        net = psutil.net_io_counters()
        # net_io_counters() devuelve estadísticas acumuladas de tráfico de red
        # desde que el sistema fue iniciado. Incluye bytes enviados, recibidos
        # y otros contadores útiles para monitorear actividad de red.

        hostname = socket.gethostname()
        # gethostname() obtiene el nombre que identifica al equipo dentro de la red.
        # No necesariamente coincide con el nombre visible para el usuario,
        # sino con el que el sistema operativo tiene registrado.

        ip = socket.gethostbyname(hostname)
        # Devuelve la IP asociada al hostname del equipo.
        # En sistemas con múltiples interfaces puede no reflejar la IP correcta.
        # Una mejora posible sería usar psutil.net_if_addrs() para mayor precisión.

        latency = subprocess.run(
            ["ping", "-n", "1", "8.8.8.8"] if platform.system() == "Windows" else ["ping", "-c", "1", "8.8.8.8"],
            capture_output=True, text=True
        )
        # Ejecutamos un único ping a 8.8.8.8 para verificar conectividad.
        # Se elige esa dirección porque pertenece a los DNS públicos de Google
        # y suele estar disponible desde prácticamente cualquier conexión a Internet.
        # El parámetro cambia según el sistema operativo:
        # "-n" en Windows y "-c" en Linux/macOS indican la cantidad de paquetes a enviar.
        # capture_output=True evita que la salida aparezca en consola
        # y text=True devuelve la respuesta como texto en lugar de bytes.

        return {
            "ip": ip,

            "bytes_sent_mb": round(net.bytes_sent / (1024**2), 2),
            # bytes_sent representa todo el tráfico enviado desde que inició el sistema.
            # Convertimos a megabytes para que el valor sea más fácil de interpretar
            # que una cifra grande expresada en bytes.

            "bytes_recv_mb": round(net.bytes_recv / (1024**2), 2),
            # bytes_recv sigue la misma lógica pero para el tráfico recibido.
            # Al mostrarlos juntos podemos tener una idea rápida del uso de red.

            "connected": latency.returncode == 0
            # subprocess devuelve un código de salida al finalizar.
            # Un returncode igual a 0 indica que el ping se ejecutó correctamente
            # y que hubo respuesta desde el destino, lo que usamos como indicador
            # simple de conectividad externa.
        }
    except Exception as e:
        # Ante errores de resolución DNS, permisos o problemas al ejecutar
        # el comando del sistema, devuelve el detalle para facilitar el diagnóstico.
        return {"error": str(e)}


def get_top_processes(limit=5):
    try:
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            # process_iter() permite recorrer los procesos activos del sistema.
            # Indicamos explícitamente los atributos que necesitamos para evitar
            # consultas innecesarias y reducir el costo de obtener la información.

            try:
                processes.append(proc.info)
                # proc.info devuelve un diccionario con los campos solicitados.
                # Guardamos cada proceso en una lista para poder ordenarlos después
                # según el criterio que nos interese.

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Un proceso puede finalizar mientras lo estamos recorriendo,
                # o el sistema puede negar acceso a determinada información.
                # En esos casos simplemente lo ignoramos y continuamos con el siguiente.
                pass

        return sorted(
            processes,
            key=lambda x: x['cpu_percent'],
            reverse=True
        )[:limit]
        # sorted() ordena los procesos según el porcentaje de CPU consumido.
        # reverse=True hace que los procesos con mayor uso aparezcan primero.
        # Finalmente usamos slicing para devolver únicamente la cantidad solicitada
        # mediante el parámetro limit.

    except Exception as e:
        # Si ocurre algún error inesperado durante la recolección u ordenamiento
        # de procesos, devolvemos el detalle sin interrumpir el programa principal.
        return {"error": str(e)}

