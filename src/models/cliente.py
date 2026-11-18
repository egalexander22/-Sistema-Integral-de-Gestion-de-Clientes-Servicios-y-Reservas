"""
Módulo que define la clase Cliente con encapsulación y validaciones estrictas.

Hereda de EntidadSistema para garantizar uniformidad e identificación en el sistema.
"""

import re
from src.exceptions import DatosInvalidosError, ParametroFaltanteError
from .entidad import EntidadSistema


class Cliente(EntidadSistema):
    """Representa un cliente registrado en Software FJ con datos personales encapsulados."""

    # Expresión regular básica para validar el formato de correo electrónico
    _PATRON_CORREO = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    # Expresión regular para validar teléfonos entre 7 y 15 dígitos (opcional + inicial)
    _PATRON_TELEFONO = re.compile(r"^\+?\d{7,15}$")

    def __init__(
        self,
        cliente_id: str,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str,
        activo: bool = True,
    ) -> None:
        # Inicializar la clase base abstracta con el ID del cliente
        super().__init__(cliente_id)
        # Asignar atributos mediante setters para ejecutar todas las validaciones
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        self.activo = activo
        # Ejecutar validación integral de la instancia recién creada
        self.validar()

    @property
    def nombre(self) -> str:
        """Retorna el nombre completo del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y asigna el nombre del cliente (mínimo 3 caracteres)."""
        # Validar que sea una cadena no vacía usando el método heredado
        limpio = self.validar_texto_no_vacio(valor, "nombre")
        # Comprobar longitud mínima razonable para un nombre real
        if len(limpio) < 3:
            raise DatosInvalidosError("El nombre del cliente debe tener al menos 3 caracteres.")
        # Guardar el valor en el atributo privado
        self._nombre = limpio

    @property
    def documento(self) -> str:
        """Retorna el número de documento de identidad del cliente."""
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        """Valida y asigna el documento (alfanumérico entre 5 y 20 caracteres)."""
        # Validar texto no vacío
        limpio = self.validar_texto_no_vacio(valor, "documento")
        # Validar longitud y ausencia de caracteres especiales inválidos
        if not limpio.isalnum() or not (5 <= len(limpio) <= 20):
            raise DatosInvalidosError(
                "El documento debe ser alfanumérico y tener entre 5 y 20 caracteres."
            )
        # Almacenar documento validado
        self._documento = limpio

    @property
    def correo(self) -> str:
        """Retorna el correo electrónico del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida el formato del correo electrónico y lo normaliza en minúsculas."""
        # Validar texto no vacío
        limpio = self.validar_texto_no_vacio(valor, "correo").lower()
        # Verificar coincidencia con el patrón de correo electrónico
        if not self._PATRON_CORREO.match(limpio):
            raise DatosInvalidosError(f"El correo electrónico '{valor}' no tiene un formato válido.")
        # Guardar correo normalizado
        self._correo = limpio

    @property
    def telefono(self) -> str:
        """Retorna el número de teléfono del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida y asigna el teléfono del cliente."""
        # Validar que el teléfono haya sido suministrado
        if valor is None:
            raise ParametroFaltanteError("El campo 'telefono' es obligatorio.")
        # Limpiar espacios y guiones comunes en números telefónicos
        limpio = str(valor).strip().replace(" ", "").replace("-", "")
        # Validar contra el patrón de dígitos permitido
        if not self._PATRON_TELEFONO.match(limpio):
            raise DatosInvalidosError(
                f"El teléfono '{valor}' debe contener entre 7 y 15 dígitos numéricos."
            )
        # Guardar el teléfono validado
        self._telefono = limpio

    @property
    def activo(self) -> bool:
        """Indica si el cliente se encuentra habilitado para realizar reservas."""
        return self._activo

    @activo.setter
    def activo(self, valor: bool) -> None:
        """Valida que el estado activo sea booleano."""
        # Comprobar tipo booleano estricto
        if not isinstance(valor, bool):
            raise DatosInvalidosError("El estado 'activo' del cliente debe ser booleano (True/False).")
        # Asignar el estado booleano
        self._activo = valor

    def validar(self) -> bool:
        """Verifica que todos los atributos esenciales del cliente estén consistentes."""
        # Confirmar que los campos internos existen y cumplen sus reglas
        if not all([self._id, self._nombre, self._documento, self._correo, self._telefono]):
            raise DatosInvalidosError("El cliente posee campos obligatorios incompletos.")
        # Retornar True si todas las comprobaciones pasaron
        return True

    def obtener_resumen(self) -> str:
        """Retorna una descripción legible del cliente."""
        # Definir etiqueta textual del estado
        estado_txt = "Activo" if self._activo else "Inactivo"
        # Formatear cadena de resumen
        return (
            f"Cliente [{self._id}] {self._nombre} | Doc: {self._documento} | "
            f"Correo: {self._correo} | Tel: {self._telefono} | Estado: {estado_txt}"
        )
