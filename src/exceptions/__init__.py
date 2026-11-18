"""Paquete de excepciones personalizadas del sistema Software FJ."""

from .excepciones import (
    SoftwareFJError,
    DatosInvalidosError,
    ParametroFaltanteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    CalculoInconsistenteError,
    EntidadNoEncontradaError,
    PersistenciaLogError,
)

__all__ = [
    "SoftwareFJError",
    "DatosInvalidosError",
    "ParametroFaltanteError",
    "OperacionNoPermitidaError",
    "ReservaInvalidaError",
    "ServicioNoDisponibleError",
    "CalculoInconsistenteError",
    "EntidadNoEncontradaError",
    "PersistenciaLogError",
]
