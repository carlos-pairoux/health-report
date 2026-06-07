import psutil
# psutil nos da acceso a métricas del sistema que Python no expone por defecto.
import platform
# platform lo usamos para detectar el SO y adaptar el comportamiento del script.

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
