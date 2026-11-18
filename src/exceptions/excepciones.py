"""
Módulo de excepciones personalizadas para el sistema de Software FJ.

Define una jerarquía de excepciones orientada a objetos que permite capturar,
clasificar, encadenar y registrar errores sin detener la ejecución del programa.
"""


class SoftwareFJError(Exception):
    """Excepción base para todos los errores controlados del sistema Software FJ."""

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL") -> None:
        # Guardar el mensaje descriptivo del error
        self.mensaje = mensaje
        # Guardar un código identificador útil para trazabilidad en los logs
        self.codigo = codigo
        # Inicializar la clase base Exception con el formato estándar
        super().__init__(f"[{self.codigo}] {self.mensaje}")


class DatosInvalidosError(SoftwareFJError):
    """Se lanza cuando un dato de entrada no cumple con el formato o rango esperado."""

    def __init__(self, mensaje: str) -> None:
        # Invocar al constructor padre con código específico de validación de datos
        super().__init__(mensaje, codigo="ERR_DATOS_INVALIDOS")


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio para ejecutar una operación."""

    def __init__(self, mensaje: str) -> None:
        # Invocar al constructor padre con código específico de parámetro faltante
        super().__init__(mensaje, codigo="ERR_PARAMETRO_FALTANTE")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta ejecutar una acción inválida para el estado actual."""

    def __init__(self, mensaje: str) -> None:
        # Invocar al constructor padre con código específico de operación no permitida
        super().__init__(mensaje, codigo="ERR_OPERACION_NO_PERMITIDA")


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva presenta inconsistencias o incumple reglas de negocio."""

    def __init__(self, mensaje: str) -> None:
        # Invocar al constructor padre con código específico de error en reserva
        super().__init__(mensaje, codigo="ERR_RESERVA_INVALIDA")


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando el servicio solicitado no está disponible para ser reservado."""

    def __init__(self, mensaje: str) -> None:
        # Invocar al constructor padre con código específico de disponibilidad
        super().__init__(mensaje, codigo="ERR_SERVICIO_NO_DISPONIBLE")


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando ocurre un error matemático o inconsistencia en el cálculo de costos."""

    def __init__(self, mensaje: str) -> None:
        # Invocar al constructor padre con código específico de cálculo financiero
        super().__init__(mensaje, codigo="ERR_CALCULO_INCONSISTENTE")


class EntidadNoEncontradaError(SoftwareFJError):
    """Se lanza cuando no se encuentra un cliente, servicio o reserva en las listas internas."""

    def __init__(self, mensaje: str) -> None:
        # Invocar al constructor padre con código específico de búsqueda fallida
        super().__init__(mensaje, codigo="ERR_ENTIDAD_NO_ENCONTRADA")


class PersistenciaLogError(SoftwareFJError):
    """Se lanza cuando falla la escritura o acceso al archivo de registro (logs)."""

    def __init__(self, mensaje: str) -> None:
        # Invocar al constructor padre con código específico de falla en logs
        super().__init__(mensaje, codigo="ERR_PERSISTENCIA_LOG")
