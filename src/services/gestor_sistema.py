"""
Módulo orquestador del Sistema Integral de Gestión de Clientes, Servicios y Reservas.

Gestiona listas internas en memoria (sin bases de datos) y centraliza el uso de
bloques try/except, try/except/else, try/except/finally, encadenamiento de
excepciones y registro en archivo de logs.
"""

from typing import List, Optional
from src.exceptions import (
    DatosInvalidosError,
    EntidadNoEncontradaError,
    SoftwareFJError,
)
from src.models import Cliente, Reserva, Servicio
from src.utils import GestorLogs


class SistemaSoftwareFJ:
    """Controlador principal que administra clientes, servicios y reservas en listas."""

    def __init__(self, ruta_log: str = "logs/sistema_fj.log") -> None:
        # Inicializar listas internas en memoria (sin base de datos)
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        # Inicializar el gestor de archivos de logs
        self._logs = GestorLogs(ruta_archivo=ruta_log)
        # Registrar inicio del sistema en el archivo de logs
        self._logs.registrar_evento("Sistema Software FJ inicializado correctamente.")

    @property
    def clientes(self) -> List[Cliente]:
        """Retorna una copia de la lista de clientes registrados."""
        return list(self._clientes)

    @property
    def servicios(self) -> List[Servicio]:
        """Retorna una copia de la lista de servicios registrados."""
        return list(self._servicios)

    @property
    def reservas(self) -> List[Reserva]:
        """Retorna una copia de la lista de reservas registradas."""
        return list(self._reservas)

    def registrar_cliente(self, cliente: Cliente) -> Optional[Cliente]:
        """Registra un nuevo cliente verificando que no exista ID o documento duplicado."""
        try:
            # Verificar que no exista otro cliente con el mismo ID o documento
            if any(c.id == cliente.id or c.documento == cliente.documento for c in self._clientes):
                raise DatosInvalidosError(
                    f"Ya existe un cliente con ID '{cliente.id}' o documento '{cliente.documento}'."
                )
            # Validar integridad del cliente
            cliente.validar()
        except SoftwareFJError as exc:
            # Registrar error controlado en el archivo de logs y retornar None sin caer
            self._logs.registrar_error(exc, contexto="registrar_cliente")
            return None
        else:
            # Agregar el cliente a la lista interna si la validación fue exitosa
            self._clientes.append(cliente)
            self._logs.registrar_evento(f"Cliente registrado: {cliente.obtener_resumen()}")
            return cliente
        finally:
            # Bloque finally para asegurar trazabilidad del intento de registro
            self._logs.registrar_evento(
                f"Finalizado intento de registro para cliente ID '{getattr(cliente, 'id', 'N/A')}'."
            )

    def registrar_servicio(self, servicio: Servicio) -> Optional[Servicio]:
        """Registra un servicio polimórfico en la lista interna de servicios."""
        try:
            # Verificar unicidad del identificador del servicio
            if any(s.id == servicio.id for s in self._servicios):
                raise DatosInvalidosError(f"Ya existe un servicio registrado con ID '{servicio.id}'.")
            # Ejecutar validación polimórfica
            servicio.validar()
        except SoftwareFJError as exc:
            # Registrar la falla en el archivo de logs
            self._logs.registrar_error(exc, contexto="registrar_servicio")
            return None
        else:
            # Almacenar el servicio en la lista interna
            self._servicios.append(servicio)
            self._logs.registrar_evento(f"Servicio registrado: {servicio.describir_servicio()}")
            return servicio

    def buscar_cliente(self, cliente_id: str) -> Cliente:
        """Busca un cliente por ID en la lista interna o lanza EntidadNoEncontradaError."""
        for cliente in self._clientes:
            if cliente.id == cliente_id:
                return cliente
        raise EntidadNoEncontradaError(f"No se encontró el cliente con ID '{cliente_id}'.")

    def buscar_servicio(self, servicio_id: str) -> Servicio:
        """Busca un servicio por ID en la lista interna o lanza EntidadNoEncontradaError."""
        for servicio in self._servicios:
            if servicio.id == servicio_id:
                return servicio
        raise EntidadNoEncontradaError(f"No se encontró el servicio con ID '{servicio_id}'.")

    def buscar_reserva(self, reserva_id: str) -> Reserva:
        """Busca una reserva por ID en la lista interna o lanza EntidadNoEncontradaError."""
        for reserva in self._reservas:
            if reserva.id == reserva_id:
                return reserva
        raise EntidadNoEncontradaError(f"No se encontró la reserva con ID '{reserva_id}'.")

    def crear_reserva(
        self,
        reserva_id: str,
        cliente_id: str,
        servicio_id: str,
        duracion_horas: float,
    ) -> Optional[Reserva]:
        """Crea una reserva buscando cliente y servicio, manejando errores de negocio."""
        try:
            # Validar que el ID de reserva no esté duplicado
            if any(r.id == reserva_id for r in self._reservas):
                raise DatosInvalidosError(f"Ya existe una reserva con ID '{reserva_id}'.")
            # Localizar cliente y servicio en las listas internas
            cliente = self.buscar_cliente(cliente_id)
            servicio = self.buscar_servicio(servicio_id)
            # Instanciar la reserva (ejecuta validaciones de cliente activo y servicio disponible)
            reserva = Reserva(reserva_id, cliente, servicio, duracion_horas)
        except SoftwareFJError as exc:
            # Registrar cualquier excepción de dominio en el archivo de logs
            self._logs.registrar_error(exc, contexto="crear_reserva")
            return None
        else:
            # Guardar la reserva en la lista interna si no hubo errores
            self._reservas.append(reserva)
            self._logs.registrar_evento(f"Reserva creada: {reserva.obtener_resumen()}")
            return reserva

    def confirmar_reserva(self, reserva_id: str) -> bool:
        """Confirma una reserva existente manejando errores de estado o disponibilidad."""
        try:
            reserva = self.buscar_reserva(reserva_id)
            reserva.confirmar()
        except SoftwareFJError as exc:
            self._logs.registrar_error(exc, contexto="confirmar_reserva")
            return False
        else:
            self._logs.registrar_evento(f"Reserva confirmada: {reserva.obtener_resumen()}")
            return True

    def cancelar_reserva(self, reserva_id: str, motivo: str = "Solicitud del cliente") -> bool:
        """Cancela una reserva existente registrando el evento o el error en logs."""
        try:
            reserva = self.buscar_reserva(reserva_id)
            reserva.cancelar(motivo=motivo)
        except SoftwareFJError as exc:
            self._logs.registrar_error(exc, contexto="cancelar_reserva")
            return False
        else:
            self._logs.registrar_evento(
                f"Reserva cancelada ({motivo}): {reserva.obtener_resumen()}"
            )
            return True

    def procesar_reserva(
        self,
        reserva_id: str,
        incluir_iva: bool = True,
        porcentaje_descuento: float = 0.0,
        recargo_adicional: Optional[float] = None,
    ) -> Optional[float]:
        """Procesa una reserva confirmada y retorna el monto total calculado."""
        try:
            reserva = self.buscar_reserva(reserva_id)
            total = reserva.procesar(
                incluir_iva=incluir_iva,
                porcentaje_descuento=porcentaje_descuento,
                recargo_adicional=recargo_adicional,
            )
        except SoftwareFJError as exc:
            self._logs.registrar_error(exc, contexto="procesar_reserva")
            return None
        else:
            self._logs.registrar_evento(
                f"Reserva procesada exitosamente: {reserva.obtener_resumen()}"
            )
            return total
        finally:
            # Registrar cierre del proceso de facturación/procesamiento
            self._logs.registrar_evento(f"Intento de procesamiento concluido para '{reserva_id}'.")
