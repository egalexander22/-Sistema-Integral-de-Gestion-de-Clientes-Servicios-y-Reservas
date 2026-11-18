"""
Módulo que define la clase abstracta base para todas las entidades del sistema.

Aplica el principio de abstracción y encapsulación compartida entre clientes,
servicios y reservas de Software FJ.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from src.exceptions import DatosInvalidosError, ParametroFaltanteError


class EntidadSistema(ABC):
    """Clase abstracta base que representa cualquier entidad gestionable del sistema."""

    def __init__(self, entidad_id: str) -> None:
        # Validar que el identificador no sea nulo ni cadena vacía
        if entidad_id is None or not isinstance(entidad_id, str) or not entidad_id.strip():
            # Lanzar ParametroFaltanteError si no se proporcionó un ID válido
            raise ParametroFaltanteError("El identificador de la entidad es obligatorio.")
        # Almacenar el ID limpio de espacios en un atributo protegido
        self._id: str = entidad_id.strip()
        # Registrar la fecha y hora exacta de creación de la entidad en memoria
        self._fecha_registro: datetime = datetime.now()

    @property
    def id(self) -> str:
        """Retorna el identificador único de la entidad (solo lectura)."""
        # Devolver el atributo encapsulado _id
        return self._id

    @property
    def fecha_registro(self) -> datetime:
        """Retorna la fecha y hora en que se instanció la entidad."""
        # Devolver la marca de tiempo protegida
        return self._fecha_registro

    @staticmethod
    def validar_texto_no_vacio(valor: str, nombre_campo: str) -> str:
        """Utilidad común para validar que un campo de texto sea válido y no vacío."""
        # Verificar si el parámetro fue omitido por completo
        if valor is None:
            raise ParametroFaltanteError(f"El campo '{nombre_campo}' es obligatorio.")
        # Verificar que el tipo de dato sea cadena de texto
        if not isinstance(valor, str):
            raise DatosInvalidosError(f"El campo '{nombre_campo}' debe ser una cadena de texto.")
        # Eliminar espacios sobrantes al inicio y al final
        texto_limpio = valor.strip()
        # Comprobar que el texto resultante tenga al menos un carácter
        if not texto_limpio:
            raise DatosInvalidosError(f"El campo '{nombre_campo}' no puede estar vacío.")
        # Retornar el texto validado
        return texto_limpio

    @abstractmethod
    def validar(self) -> bool:
        """Valida la consistencia interna de la entidad según sus reglas de negocio."""
        # Método abstracto que debe ser implementado obligatoriamente por cada subclase
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Retorna una representación resumida y legible de la entidad."""
        # Método abstracto para describir polimórficamente cada entidad
        pass

    def __str__(self) -> str:
        """Devuelve la representación en texto delegando en obtener_resumen()."""
        # Reutilizar la implementación polimórfica de cada subclase
        return self.obtener_resumen()
