"""
Módulo con las implementaciones especializadas de Servicio para Software FJ.

Incluye:
- ReservaSala: gestión de salas de reuniones o capacitación.
- AlquilerEquipo: préstamo de equipos tecnológicos.
- AsesoriaEspecializada: consultorías técnicas con especialistas.
"""

from src.exceptions import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ParametroFaltanteError,
)
from .servicio import Servicio


class ReservaSala(Servicio):
    """Servicio especializado para la reserva de salas de trabajo o capacitación."""

    # Recargo fijo por uso de equipo audiovisual (proyector/sonido)
    RECARGO_AUDIOVISUAL = 25000.0

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        incluye_proyector: bool = False,
        disponible: bool = True,
    ) -> None:
        # Guardar atributos específicos antes de validar en super().__init__ si aplica
        self.capacidad_personas = capacidad_personas
        self.incluye_proyector = incluye_proyector
        # Inicializar la clase padre Servicio
        super().__init__(servicio_id, nombre, tarifa_base, disponible)
        # Validar parámetros especializados de la sala
        self.validar_parametros()

    @property
    def capacidad_personas(self) -> int:
        """Retorna el aforo máximo de la sala."""
        return self._capacidad_personas

    @capacidad_personas.setter
    def capacidad_personas(self, valor: int) -> None:
        """Valida que la capacidad sea un entero positivo."""
        if valor is None:
            raise ParametroFaltanteError("La capacidad de la sala es obligatoria.")
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise DatosInvalidosError("La capacidad de la sala debe ser un entero mayor a cero.")
        self._capacidad_personas = valor

    @property
    def incluye_proyector(self) -> bool:
        """Indica si la sala cuenta con proyector y sistema audiovisual."""
        return self._incluye_proyector

    @incluye_proyector.setter
    def incluye_proyector(self, valor: bool) -> None:
        """Valida que incluye_proyector sea booleano."""
        if not isinstance(valor, bool):
            raise DatosInvalidosError("El indicador 'incluye_proyector' debe ser booleano.")
        self._incluye_proyector = valor

    def validar_parametros(self) -> bool:
        """Valida los parámetros específicos de ReservaSala."""
        # Verificar que el aforo no exceda un límite físico razonable
        if self._capacidad_personas > 500:
            raise DatosInvalidosError("La capacidad máxima permitida para una sala es 500 personas.")
        return True

    def calcular_costo(self, duracion_horas: float) -> float:
        """Calcula el costo de la sala, sumando recargo audiovisual si aplica."""
        # Validar la duración ingresada
        horas = self.validar_duracion(duracion_horas)
        # Calcular tarifa proporcional al tiempo reservado
        costo = self.tarifa_base * horas
        # Sumar recargo único si la sala incluye proyector
        if self._incluye_proyector:
            costo += self.RECARGO_AUDIOVISUAL
        # Aplicar descuento automático del 10% para reservas de jornada completa (>= 8 horas)
        if horas >= 8:
            costo *= 0.90
        return round(costo, 2)

    def describir_servicio(self) -> str:
        """Retorna la descripción polimórfica de la sala."""
        equipo = "con proyector" if self._incluye_proyector else "sin proyector"
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"ReservaSala [{self.id}] '{self.nombre}' | Cap: {self._capacidad_personas} pers. | "
            f"{equipo} | Tarifa: ${self.tarifa_base:,.2f}/h | {estado}"
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado para el alquiler de equipos de cómputo o laboratorio."""

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        tarifa_base: float,
        categoria_equipo: str,
        cantidad_unidades: int = 1,
        deposito_seguridad: float = 0.0,
        disponible: bool = True,
    ) -> None:
        # Asignar y validar atributos propios del alquiler
        self.categoria_equipo = categoria_equipo
        self.cantidad_unidades = cantidad_unidades
        self.deposito_seguridad = deposito_seguridad
        # Inicializar clase base Servicio
        super().__init__(servicio_id, nombre, tarifa_base, disponible)
        # Ejecutar validación especializada
        self.validar_parametros()

    @property
    def categoria_equipo(self) -> str:
        """Retorna la categoría del equipo (ej. Portátil, Servidor, Red)."""
        return self._categoria_equipo

    @categoria_equipo.setter
    def categoria_equipo(self, valor: str) -> None:
        """Valida que la categoría del equipo no esté vacía."""
        self._categoria_equipo = self.validar_texto_no_vacio(valor, "categoría de equipo")

    @property
    def cantidad_unidades(self) -> int:
        """Retorna la cantidad de unidades incluidas en el alquiler."""
        return self._cantidad_unidades

    @cantidad_unidades.setter
    def cantidad_unidades(self, valor: int) -> None:
        """Valida que la cantidad de unidades sea un entero positivo."""
        if valor is None:
            raise ParametroFaltanteError("La cantidad de unidades es obligatoria.")
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise DatosInvalidosError("La cantidad de unidades debe ser un entero positivo.")
        self._cantidad_unidades = valor

    @property
    def deposito_seguridad(self) -> float:
        """Retorna el depósito reembolsable por el equipo."""
        return self._deposito_seguridad

    @deposito_seguridad.setter
    def deposito_seguridad(self, valor: float) -> None:
        """Valida que el depósito de seguridad no sea negativo."""
        try:
            dep = float(valor)
        except (TypeError, ValueError) as exc:
            raise DatosInvalidosError("El depósito de seguridad debe ser numérico.") from exc
        if dep < 0:
            raise CalculoInconsistenteError("El depósito de seguridad no puede ser negativo.")
        self._deposito_seguridad = round(dep, 2)

    def validar_parametros(self) -> bool:
        """Valida las reglas específicas del alquiler de equipos."""
        # Limitar cantidad máxima por solicitud individual
        if self._cantidad_unidades > 50:
            raise DatosInvalidosError("No se pueden alquilar más de 50 unidades en un solo servicio.")
        return True

    def calcular_costo(self, duracion_horas: float) -> float:
        """Calcula el costo multiplicando tarifa por horas, unidades y sumando depósito."""
        # Validar duración en horas
        horas = self.validar_duracion(duracion_horas)
        # Calcular costo total incluyendo unidades y depósito
        costo = (self.tarifa_base * horas * self._cantidad_unidades) + self._deposito_seguridad
        return round(costo, 2)

    def describir_servicio(self) -> str:
        """Retorna la descripción polimórfica del alquiler de equipos."""
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"AlquilerEquipo [{self.id}] '{self.nombre}' | Cat: {self._categoria_equipo} | "
            f"Unidades: {self._cantidad_unidades} | Depósito: ${self._deposito_seguridad:,.2f} | "
            f"Tarifa: ${self.tarifa_base:,.2f}/h | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para consultoría y asesoría técnica profesional."""

    # Modalidades permitidas para prestar la asesoría
    MODALIDADES_VALIDAS = ("virtual", "presencial")

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        consultor: str,
        modalidad: str = "virtual",
        disponible: bool = True,
    ) -> None:
        # Validar y almacenar propiedades de la asesoría
        self.especialidad = especialidad
        self.consultor = consultor
        self.modalidad = modalidad
        # Inicializar clase base Servicio
        super().__init__(servicio_id, nombre, tarifa_base, disponible)
        # Validar parámetros especializados
        self.validar_parametros()

    @property
    def especialidad(self) -> str:
        """Retorna el área de especialidad técnica."""
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor: str) -> None:
        """Valida que la especialidad no esté vacía."""
        self._especialidad = self.validar_texto_no_vacio(valor, "especialidad")

    @property
    def consultor(self) -> str:
        """Retorna el nombre del consultor asignado."""
        return self._consultor

    @consultor.setter
    def consultor(self, valor: str) -> None:
        """Valida el nombre del consultor."""
        self._consultor = self.validar_texto_no_vacio(valor, "consultor")

    @property
    def modalidad(self) -> str:
        """Retorna la modalidad de la asesoría (virtual o presencial)."""
        return self._modalidad

    @modalidad.setter
    def modalidad(self, valor: str) -> None:
        """Valida que la modalidad pertenezca a las opciones permitidas."""
        limpio = self.validar_texto_no_vacio(valor, "modalidad").lower()
        if limpio not in self.MODALIDADES_VALIDAS:
            raise DatosInvalidosError(
                f"Modalidad '{valor}' inválida. Use 'virtual' o 'presencial'."
            )
        self._modalidad = limpio

    def validar_parametros(self) -> bool:
        """Valida la coherencia de los parámetros de asesoría."""
        # Confirmar que modalidad y consultor estén definidos correctamente
        if self._modalidad not in self.MODALIDADES_VALIDAS:
            raise DatosInvalidosError("La modalidad de asesoría no es válida.")
        return True

    def calcular_costo(self, duracion_horas: float) -> float:
        """Calcula el costo de la asesoría aplicando recargo del 15% si es presencial."""
        # Validar duración solicitada
        horas = self.validar_duracion(duracion_horas)
        # Calcular costo base por horas
        costo = self.tarifa_base * horas
        # Aplicar recargo por desplazamiento cuando la asesoría es presencial
        if self._modalidad == "presencial":
            costo *= 1.15
        return round(costo, 2)

    def describir_servicio(self) -> str:
        """Retorna la descripción polimórfica de la asesoría especializada."""
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"AsesoriaEspecializada [{self.id}] '{self.nombre}' | Área: {self._especialidad} | "
            f"Consultor: {self._consultor} | Modalidad: {self._modalidad} | "
            f"Tarifa: ${self.tarifa_base:,.2f}/h | {estado}"
        )
