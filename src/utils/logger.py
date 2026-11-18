"""
Módulo de registro de eventos y errores (logging) en archivo de texto.

Cumple con el requisito de persistir únicamente eventos y errores en archivos,
sin utilizar motores de bases de datos.
"""

import logging
from pathlib import Path
from src.exceptions import PersistenciaLogError


class GestorLogs:
    """Administra la escritura estructurada de eventos y errores en un archivo .log."""

    def __init__(self, ruta_archivo: str = "logs/sistema_fj.log") -> None:
        # Almacenar la ruta del archivo de logs como objeto Path
        self.ruta_archivo = Path(ruta_archivo)
        # Configurar el logger interno de Python con un nombre único por ruta
        self._logger = logging.getLogger(f"SoftwareFJ.{self.ruta_archivo}")
        # Establecer el nivel mínimo de registro en INFO para capturar eventos y errores
        self._logger.setLevel(logging.INFO)
        # Evitar que los mensajes se dupliquen hacia el logger raíz
        self._logger.propagate = False
        # Inicializar el manejador de archivo si aún no ha sido configurado
        self._configurar_archivo()

    def _configurar_archivo(self) -> None:
        """Crea el directorio de logs si no existe y configura el FileHandler."""
        try:
            # Crear la carpeta contenedora (ej. logs/) si no existe previamente
            self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
            # Verificar si ya existen handlers para no duplicar líneas de log
            if not self._logger.handlers:
                # Crear el manejador que escribe en disco con codificación UTF-8
                manejador = logging.FileHandler(self.ruta_archivo, encoding="utf-8")
                # Definir el formato estándar: fecha/hora | nivel | mensaje
                formato = logging.Formatter(
                    "%(asctime)s | %(levelname)-8s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                # Asociar el formato al manejador de archivo
                manejador.setFormatter(formato)
                # Registrar el manejador en el logger
                self._logger.addHandler(manejador)
        except OSError as exc:
            # Encadenar la excepción del sistema operativo a PersistenciaLogError
            raise PersistenciaLogError(
                f"No fue posible inicializar el archivo de logs en '{self.ruta_archivo}'."
            ) from exc

    def registrar_evento(self, mensaje: str) -> None:
        """Registra una operación o evento informativo exitoso en el archivo de logs."""
        # Escribir el mensaje con nivel INFO
        self._logger.info(mensaje)

    def registrar_advertencia(self, mensaje: str) -> None:
        """Registra una advertencia controlada en el archivo de logs."""
        # Escribir el mensaje con nivel WARNING
        self._logger.warning(mensaje)

    def registrar_error(self, error: Exception, contexto: str = "") -> None:
        """Registra una excepción capturada junto con su contexto y causa encadenada."""
        # Construir el texto de contexto si fue suministrado
        prefijo = f"[{contexto}] " if contexto else ""
        # Verificar si la excepción tiene una causa encadenada (__cause__)
        causa = f" | Causa original: {repr(error.__cause__)}" if error.__cause__ else ""
        # Escribir el detalle completo del error con nivel ERROR
        self._logger.error(f"{prefijo}{type(error).__name__}: {error}{causa}")
