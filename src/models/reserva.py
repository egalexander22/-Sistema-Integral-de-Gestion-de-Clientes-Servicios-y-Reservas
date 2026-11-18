"""
Módulo que define la clase Reserva y su ciclo de estados.

Integra un Cliente, un Servicio, duración y estado, implementando confirmación,
cancelación y procesamiento con manejo avanzado de excepciones.
"""

from enum import Enum
from typing import Optional
from src.exceptions import (
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from .cliente import Cliente
from .entidad import EntidadSistema
from .servicio import Servicio


class EstadoReserva(Enum):
    """Enumeración de estados válidos para el ciclo de vida de una reserva."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"


class Reserva(EntidadSistema):
    """Representa una reserva de servicio realizada por un cliente en Software FJ."""

    def __init__(
        self,
        reserva_id: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
    ) -> None:
        # Inicializar la clase abstracta EntidadSistema con el ID de reserva
        super().__init__(reserva_id)
        # Validar que se haya recibido una instancia válida de Cliente
        if cliente is None or not isinstance(cliente, Cliente):
            raise ParametroFaltanteError("La reserva requiere un objeto Cliente válido.")
        # Validar que se haya recibido una instancia válida de Servicio
        if servicio is None or not isinstance(servicio, Servicio):
            raise ParametroFaltanteError("La reserva requiere un objeto Servicio válido.")

        # Guardar referencias encapsuladas al cliente y al servicio
        self._cliente: Cliente = cliente
        self._servicio: Servicio = servicio
        # Validar la duración delegando en la lógica del servicio
        self._duracion_horas: float = self._servicio.validar_duracion(duracion_horas)
        # Inicializar el estado de la reserva en PENDIENTE
        self._estado: EstadoReserva = EstadoReserva.PENDIENTE
        # Inicializar el costo total calculado en None hasta su cálculo/procesamiento
        self._costo_total: Optional[float] = None
        # Ejecutar validaciones de negocio iniciales
        self.validar()

    @property
    def cliente(self) -> Cliente:
        """Retorna el cliente asociado a la reserva."""
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        """Retorna el servicio asociado a la reserva."""
        return self._servicio

    @property
    def duracion_horas(self) -> float:
        """Retorna la duración reservada en horas."""
        return self._duracion_horas

    @property
    def estado(self) -> EstadoReserva:
        """Retorna el estado actual de la reserva."""
        return self._estado

    @property
    def costo_total(self) -> Optional[float]:
        """Retorna el costo total calculado de la reserva (si ya fue calculado)."""
        return self._costo_total

    def validar(self) -> bool:
        """Verifica que el cliente esté activo y el servicio esté disponible."""
        # Impedir reservas para clientes inactivos
        if not self._cliente.activo:
            raise ReservaInvalidaError(
                f"El cliente '{self._cliente.nombre}' está inactivo y no puede reservar."
            )
        # Impedir reservas si el servicio no se encuentra disponible
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' no está disponible actualmente."
            )
        return True

    def calcular_total(
        self,
        incluir_iva: bool = True,
        porcentaje_descuento: float = 0.0,
        recargo_adicional: Optional[float] = None,
    ) -> float:
        """Calcula y almacena el costo total utilizando la sobrecarga del servicio."""
        try:
            # Invocar el método con parámetros opcionales del servicio
            total = self._servicio.calcular_costo_con_opciones(
                duracion_horas=self._duracion_horas,
                incluir_iva=incluir_iva,
                porcentaje_descuento=porcentaje_descuento,
                recargo_adicional=recargo_adicional,
            )
        except Exception as exc:
            # Encadenar cualquier error de cálculo hacia ReservaInvalidaError
            raise ReservaInvalidaError(
                f"No fue posible calcular el costo de la reserva '{self.id}'."
            ) from exc
        else:
            # Almacenar el costo calculado solo si no hubo excepciones
            self._costo_total = total
            return total

    def confirmar(self) -> None:
        """Confirma una reserva que se encuentre en estado PENDIENTE."""
        # Validar transición de estado permitida
        if self._estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva '{self.id}' en estado {self._estado.value}."
            )
        # Revalidar disponibilidad del servicio antes de confirmar
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' dejó de estar disponible."
            )
        # Cambiar estado a CONFIRMADA
        self._estado = EstadoReserva.CONFIRMADA

    def cancelar(self, motivo: str = "Sin motivo especificado") -> None:
        """Cancela una reserva siempre que no haya sido procesada o ya cancelada."""
        # Impedir cancelación si la reserva ya fue procesada/facturada
        if self._estado == EstadoReserva.PROCESADA:
            raise OperacionNoPermitidaError(
                f"No se puede cancelar la reserva '{self.id}' porque ya fue PROCESADA."
            )
        # Impedir doble cancelación
        if self._estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError(
                f"La reserva '{self.id}' ya se encuentra CANCELADA."
            )
        # Cambiar estado a CANCELADA
        self._estado = EstadoReserva.CANCELADA

    def procesar(
        self,
        incluir_iva: bool = True,
        porcentaje_descuento: float = 0.0,
        recargo_adicional: Optional[float] = None,
    ) -> float:
        """Procesa una reserva CONFIRMADA, calcula su costo final y cierra el ciclo."""
        # Exigir que la reserva haya sido confirmada previamente
        if self._estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se pueden procesar reservas CONFIRMADAS (estado actual: {self._estado.value})."
            )
        # Calcular el costo total con las opciones suministradas
        total = self.calcular_total(
            incluir_iva=incluir_iva,
            porcentaje_descuento=porcentaje_descuento,
            recargo_adicional=recargo_adicional,
        )
        # Actualizar estado final a PROCESADA
        self._estado = EstadoReserva.PROCESADA
        return total

    def obtener_resumen(self) -> str:
        """Retorna una cadena descriptiva del estado actual de la reserva."""
        costo_txt = f"${self._costo_total:,.2f}" if self._costo_total is not None else "Por calcular"
        return (
            f"Reserva [{self.id}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Duración: {self._duracion_horas}h | "
            f"Estado: {self._estado.value} | Total: {costo_txt}"
        )
