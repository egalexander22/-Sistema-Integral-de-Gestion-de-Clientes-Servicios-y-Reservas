"""Pruebas unitarias para validar POO y manejo de excepciones en Software FJ."""

import tempfile
import unittest
from pathlib import Path
from src.exceptions import (
    DatosInvalidosError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from src.models import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    EstadoReserva,
    Reserva,
    ReservaSala,
)
from src.services import SistemaSoftwareFJ


class TestSoftwareFJ(unittest.TestCase):
    """Suite de pruebas para clientes, servicios, reservas y manejo de errores."""

    def setUp(self) -> None:
        # Crear un directorio temporal para no contaminar el log principal durante tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = str(Path(self.temp_dir.name) / "test_fj.log")
        self.sistema = SistemaSoftwareFJ(ruta_log=self.log_path)

    def tearDown(self) -> None:
        # Cerrar handlers de logging antes de eliminar la carpeta temporal
        for handler in list(self.sistema._logs._logger.handlers):
            handler.close()
            self.sistema._logs._logger.removeHandler(handler)
        self.temp_dir.cleanup()

    def test_cliente_valido_e_invalido(self) -> None:
        """Verifica validaciones estrictas de correo y documento en Cliente."""
        cliente = Cliente("C1", "María López", "12345678", "maria@correo.com", "3001112233")
        self.assertEqual(cliente.correo, "maria@correo.com")
        with self.assertRaises(DatosInvalidosError):
            Cliente("C2", "Ma", "123", "sin_arroba", "12")

    def test_polimorfismo_y_sobrecarga_servicios(self) -> None:
        """Verifica cálculo polimórfico y sobrecarga con IVA, descuento y recargo."""
        sala = ReservaSala("S1", "Sala Norte", 50000.0, 10, incluye_proyector=True)
        # 2 horas * 50000 + 25000 proyector = 125000
        self.assertEqual(sala.calcular_costo(2), 125000.0)
        # Con 10% descuento y 19% IVA: (125000 * 0.9) * 1.19 = 133875.0
        self.assertEqual(
            sala.calcular_costo_con_opciones(2, incluir_iva=True, porcentaje_descuento=10.0),
            133875.0,
        )

        equipo = AlquilerEquipo("S2", "Laptop Pro", 20000.0, "Cómputo", cantidad_unidades=3, deposito_seguridad=50000.0)
        self.assertEqual(equipo.calcular_costo(2), 170000.0)

        asesoria = AsesoriaEspecializada("S3", "Seguridad", 100000.0, "Ciberseguridad", "Ing. Juan", modalidad="presencial")
        self.assertEqual(asesoria.calcular_costo(2), 230000.0)

    def test_ciclo_reserva_y_excepciones(self) -> None:
        """Verifica confirmación, procesamiento, encadenamiento y bloqueos de estado."""
        cli = Cliente("C1", "Pedro Pérez", "98765432", "pedro@correo.com", "3112223344")
        sala = ReservaSala("S1", "Sala Sur", 40000.0, 8)
        self.sistema.registrar_cliente(cli)
        self.sistema.registrar_servicio(sala)

        reserva = self.sistema.crear_reserva("R1", "C1", "S1", 3)
        self.assertIsNotNone(reserva)
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)

        self.assertTrue(self.sistema.confirmar_reserva("R1"))
        self.assertEqual(reserva.estado, EstadoReserva.CONFIRMADA)

        total = self.sistema.procesar_reserva("R1", incluir_iva=False)
        self.assertEqual(total, 120000.0)
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)

        # No se puede cancelar una reserva ya procesada
        self.assertFalse(self.sistema.cancelar_reserva("R1"))

    def test_encadenamiento_y_servicio_no_disponible(self) -> None:
        """Verifica ServicioNoDisponibleError y encadenamiento en ReservaInvalidaError."""
        cli = Cliente("C1", "Elena Torres", "55667788", "elena@correo.com", "3204445566")
        sala_indisp = ReservaSala("S9", "Sala Cerrada", 50000.0, 5, disponible=False)
        with self.assertRaises(ServicioNoDisponibleError):
            Reserva("R9", cli, sala_indisp, 2)

        sala_ok = ReservaSala("S10", "Sala OK", 50000.0, 5, disponible=True)
        res = Reserva("R10", cli, sala_ok, 2)
        with self.assertRaises(ReservaInvalidaError) as ctx:
            res.calcular_total(porcentaje_descuento=200.0)
        self.assertIsNotNone(ctx.exception.__cause__)

        with self.assertRaises(EntidadNoEncontradaError):
            self.sistema.buscar_cliente("NO_EXISTE")

        res.cancelar()
        with self.assertRaises(OperacionNoPermitidaError):
            res.confirmar()


if __name__ == "__main__":
    unittest.main()
