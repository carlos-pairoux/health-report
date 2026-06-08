# HealthReport

## Qué es

HealthReport es una herramienta en Python que se ejecuta desde la terminal y muestra el estado actual de un sistema.

Su propósito es dar una lectura rápida de recursos clave como CPU, memoria, disco, red, procesos y uptime, para detectar si una máquina está bajo carga o funcionando con normalidad.

Está pensada como una utilidad básica de diagnóstico en contextos de soporte IT, donde se necesita información clara e inmediata sin configuraciones complejas.

Pensado para aprendizaje y diagnóstico. No apto para producción.

---

## Cómo se usa

HealthReport se ejecuta desde la terminal como un script de Python. Al ejecutarse, genera un reporte puntual del estado del sistema mostrando una "foto" del uso actual de recursos.

**Métricas incluidas:**

- **CPU:** núcleos físicos, lógicos y porcentaje de uso
- **Memoria RAM:** total, disponible y porcentaje de uso
- **Disco:** capacidad total, libre y porcentaje de uso
- **Red:** IP del sistema, tráfico enviado/recibido y estado básico de conectividad
- **Procesos:** lista de mayor consumo de CPU en el momento
- **Alertas:** detección simple de sobrecarga basada en umbrales
- **Uptime:** tiempo de actividad del sistema

> El resultado no es continuo ni histórico, sino una captura del estado actual del sistema en el momento de la ejecución.

**Instalación y uso:**

```bash
pip install psutil
python health-report.py
```

---

## Por qué está diseñado así

HealthReport está diseñado como una herramienta deliberadamente simple, enfocada en obtener visibilidad rápida del estado de un sistema sin introducir complejidad innecesaria.

Se priorizó una arquitectura basada en funciones independientes por métrica, en lugar de una estructura más abstracta, para mantener claridad y control sobre cada fuente de información.

Cada función maneja su propio dominio y sus propios errores, lo que permite que fallas parciales no rompan el reporte completo.

**El diseño asume desde el inicio que el entorno es inestable:**

- procesos pueden cambiar durante la lectura
- el acceso a métricas puede fallar
- algunas interfaces de red pueden no ser representativas

Por eso el sistema degrada resultados en lugar de fallar completamente.

Las alertas usan umbrales fijos (80%) como decisión consciente para mantener simplicidad sin depender de histórico o monitoreo persistente.

**Limitaciones intencionales:**

- sin persistencia ni histórico
- sin análisis de tendencias
- red simplificada
- visión de procesos instantánea

Estas restricciones existen para mantener foco en claridad, utilidad inmediata y control del sistema.

---

## Autor

[Carlos Pairoux](https://github.com/carlos-pairoux)
