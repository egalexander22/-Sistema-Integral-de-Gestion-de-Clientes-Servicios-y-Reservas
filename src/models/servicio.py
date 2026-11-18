"""
Módulo que define la clase abstracta Servicio.

Representa la base polimórfica para los distintos servicios de Software FJ
(reservas de salas, alquiler de equipos y asesorías especializadas), incluyendo
sobrecarga idiomática de métodos para el cálculo de costos.
"""

from abc import abstractmethod
from typing import Optional
from src.exceptions import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ParametroFaltanteError,
)
from .entidad import EntidadSistema


class Servicio(EntidadSistema):
    """Clase abstracta que modela un servicio ofrecido por Software FJ."""

    # Constante con la tasa estándar de IVA en Colombia (19%)
    IVA_ESTANDAR = 0.19

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        # Inicializar la clase abstracta EntidadSistema con el ID del servicio
        super().__init__(servicio_id)
        # Asignar atributos mediante propiedades para garantizar validación
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        """Retorna el nombre comercial del servicio."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y asigna el nombre del servicio."""
        # Verificar texto no vacío usando utilidad heredada
        self._nombre = self.validar_texto_no_vacio(valor, "nombre del servicio")

    @property
    def tarifa_base(self) -> float:
        """Retorna la tarifa base por hora del servicio."""
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        """Valida que la tarifa base sea un número positivo."""
        # Verificar si la tarifa fue omitida
        if valor is None:
            raise ParametroFaltanteError("La 'tarifa_base' del servicio es obligatoria.")
        # Intentar convertir a flotante y validar positividad
        try:
            tarifa_num = float(valor)
        except (TypeError, ValueError) as exc:
            # Encadenar error de conversión hacia DatosInvalidosError
            raise DatosInvalidosError("La tarifa base debe ser un valor numérico.") from exc
        # Rechazar tarifas menores o iguales a cero
        if tarifa_num <= 0:
            raise DatosInvalidosError("La tarifa base del servicio debe ser mayor a cero.")
        # Almacenar tarifa redondeada a dos decimales
        self._tarifa_base = round(tarifa_num, 2)

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está disponible actualmente."""
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        """Valida y actualiza el estado de disponibilidad del servicio."""
        # Exigir tipo booleano explícito
        if not isinstance(valor, bool):
            raise DatosInvalidosError("La disponibilidad del servicio debe ser booleana.")
        # Guardar estado de disponibilidad
        self._disponible = valor

    def validar_duracion(self, duracion_horas: float) -> float:
        """Valida que la duración solicitada en horas sea numérica y positiva."""
        # Comprobar ausencia del parámetro
        if duracion_horas is None:
            raise ParametroFaltanteError("La duración en horas es obligatoria.")
        # Convertir a flotante validando tipo
        try:
            horas = float(duracion_horas)
        except (TypeError, ValueError) as exc:
            raise DatosInvalidosError("La duración debe ser un número válido de horas.") from exc
        # Validar que la duración sea estrictamente mayor a cero
        if horas <= 0:
            raise DatosInvalidosError("La duración de la reserva debe ser mayor a 0 horas.")
        # Retornar la duración validada
        return horas

    def calcular_costo_con_opciones(
        self,
        duracion_horas: float,
        incluir_iva: bool = False,
        porcentaje_descuento: float = 0.0,
        recargo_adicional: Optional[float] = None,
    ) -> float:
        """
        Método sobrecargado mediante parámetros opcionales para calcular costos.

        Permite invocar el cálculo en múltiples variantes:
        1. Solo duración: costo base.
        2. Con impuestos (incluir_iva=True).
        3. Con descuento porcentual (0.0 a 100.0).
        4. Con recargo adicional opcional (ej. soporte o envío).
        """
        # Validar la duración utilizando el método auxiliar
        horas = self.validar_duracion(duracion_horas)
        # Calcular el costo base delegando en el método polimórfico de la subclase
        subtotal = self.calcular_costo(horas)

        # Validar rango permitido para el porcentaje de descuento
        if porcentaje_descuento < 0 or porcentaje_descuento > 100:
            raise CalculoInconsistenteError(
                f"El descuento ({porcentaje_descuento}%) debe estar entre 0% y 100%."
            )

        # Aplicar descuento sobre el subtotal
        valor_descuento = subtotal * (porcentaje_descuento / 100.0)
        total = subtotal - valor_descuento

        # Sumar recargo adicional si fue especificado
        if recargo_adicional is not None:
            if recargo_adicional < 0:
                raise CalculoInconsistenteError("El recargo adicional no puede ser negativo.")
            total += float(recargo_adicional)

        # Aplicar IVA estándar si el usuario lo solicita
        if incluir_iva:
            total *= 1 + self.IVA_ESTANDAR

        # Verificar consistencia final del monto calculado
        if total < 0:
            raise CalculoInconsistenteError("El costo total calculado no puede ser negativo.")

        # Retornar el valor final redondeado a dos decimales
        return round(total, 2)

    @abstractmethod
    def calcular_costo(self, duracion_horas: float) -> float:
        """Calcula el costo específico del servicio según su lógica especializada."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna una descripción detallada y especializada del servicio."""
        pass

    @abstractmethod
    def validar_parametros(self) -> bool:
        """Valida los parámetros particulares de cada tipo de servicio."""
        pass

    def validar(self) -> bool:
        """Implementa el contrato de EntidadSistema validando parámetros específicos."""
        # Delegar en la validación especializada de cada subclase
        return self.validar_parametros()

    def obtener_resumen(self) -> str:
        """Retorna el resumen general delegando en describir_servicio()."""
        # Reutilizar la descripción polimórfica de cada subclase
        return self.describir_servicio()
