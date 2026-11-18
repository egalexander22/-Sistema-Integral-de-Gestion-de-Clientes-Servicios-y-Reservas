"""
Punto de entrada y simulación del Sistema Integral de Gestión de Clientes,
Servicios y Reservas para Software FJ (UNAD - Programación 213023 - Fase 4).

Ejecuta 12 operaciones completas (válidas e inválidas) demostrando que la
aplicación continúa operando de manera estable gracias al manejo avanzado de
excepciones y al registro en archivo de logs, sin utilizar bases de datos.
"""

from src.exceptions import SoftwareFJError
from src.models import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    ReservaSala,
)
from src.services import SistemaSoftwareFJ


def imprimir_separador(titulo: str) -> None:
    """Imprime un encabezado visual en consola para cada operación simulada."""
    print(f"\n{'=' * 70}")
    print(f" {titulo}")
    print(f"{'=' * 70}")


def ejecutar_simulacion() -> None:
    """Ejecuta la secuencia de al menos 10 operaciones completas del sistema."""
    # Inicializar el sistema sin base de datos y con archivo de logs propio
    sistema = SistemaSoftwareFJ(ruta_log="logs/sistema_fj.log")

    # ------------------------------------------------------------------
    # OPERACIÓN 1: Registro válido de clientes
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 1: Registro válido de clientes")
    try:
        c1 = Cliente("CLI-001", "Laura Gómez", "1032456789", "laura.gomez@correo.com", "3001234567")
        c2 = Cliente("CLI-002", "Carlos Mendoza", "79854123", "carlos.m@empresa.co", "+573109876543")
        c3 = Cliente("CLI-003", "Andrés Ríos", "1015443322", "andres.rios@correo.com", "3157778899", activo=False)
        sistema.registrar_cliente(c1)
        sistema.registrar_cliente(c2)
        sistema.registrar_cliente(c3)
    except SoftwareFJError as exc:
        print(f"Error controlado: {exc}")
    else:
        print(f"Clientes registrados correctamente: {len(sistema.clientes)}")

    # ------------------------------------------------------------------
    # OPERACIÓN 2: Registro inválido de cliente (correo y teléfono inválidos)
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 2: Registro inválido de cliente (datos inválidos)")
    try:
        # Intentar instanciar un cliente con correo sin dominio y teléfono corto
        cliente_malo = Cliente("CLI-004", "Ana", "123456", "correo_invalido", "123")
        sistema.registrar_cliente(cliente_malo)
    except SoftwareFJError as exc:
        # Registrar el error directamente en el gestor de logs del sistema
        sistema._logs.registrar_error(exc, contexto="simulacion_op2")
        print(f"Falla controlada (el sistema continúa activo): {exc}")

    # ------------------------------------------------------------------
    # OPERACIÓN 3: Registro de cliente con documento duplicado
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 3: Intento de registro de cliente duplicado")
    c_dup = Cliente("CLI-005", "Laura Gómez Clon", "1032456789", "otra@correo.com", "3009998877")
    resultado_dup = sistema.registrar_cliente(c_dup)
    print(f"Resultado registro duplicado: {'Éxito' if resultado_dup else 'Rechazado y registrado en logs'}")

    # ------------------------------------------------------------------
    # OPERACIÓN 4: Creación válida de los 3 tipos de servicios polimórficos
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 4: Creación correcta de servicios especializados")
    s1 = ReservaSala("SRV-001", "Sala Innovación A", 80000.0, capacidad_personas=20, incluye_proyector=True)
    s2 = AlquilerEquipo("SRV-002", "Kit Servidores Lab", 45000.0, categoria_equipo="Servidor", cantidad_unidades=2, deposito_seguridad=100000.0)
    s3 = AsesoriaEspecializada("SRV-003", "Arquitectura Cloud", 150000.0, especialidad="Cloud & DevOps", consultor="Ing. Sofía Vega", modalidad="presencial")
    s4 = ReservaSala("SRV-004", "Sala Mantenimiento", 60000.0, capacidad_personas=10, incluye_proyector=False, disponible=False)
    for srv in (s1, s2, s3, s4):
        sistema.registrar_servicio(srv)
        print(f"  -> {srv.describir_servicio()}")

    # ------------------------------------------------------------------
    # OPERACIÓN 5: Creación incorrecta de servicio (tarifa negativa y modalidad inválida)
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 5: Creación incorrecta de servicios")
    try:
        ServicioInvalido = ReservaSala("SRV-ERR1", "Sala Error", -50000.0, capacidad_personas=10)
        sistema.registrar_servicio(ServicioInvalido)
    except SoftwareFJError as exc:
        sistema._logs.registrar_error(exc, contexto="simulacion_op5_tarifa")
        print(f"Error controlado en tarifa: {exc}")

    try:
        AsesoriaInvalida = AsesoriaEspecializada("SRV-ERR2", "Asesoría Err", 120000.0, "IA", "Dr. X", modalidad="hibrida")
        sistema.registrar_servicio(AsesoriaInvalida)
    except SoftwareFJError as exc:
        sistema._logs.registrar_error(exc, contexto="simulacion_op5_modalidad")
        print(f"Error controlado en modalidad: {exc}")

    # ------------------------------------------------------------------
    # OPERACIÓN 6: Reserva exitosa completa (crear -> confirmar -> procesar)
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 6: Reserva exitosa de Sala (crear, confirmar y procesar)")
    r1 = sistema.crear_reserva("RES-001", "CLI-001", "SRV-001", duracion_horas=8)
    if r1:
        sistema.confirmar_reserva("RES-001")
        total_r1 = sistema.procesar_reserva("RES-001", incluir_iva=True, porcentaje_descuento=10.0)
        print(f"Reserva procesada: {r1.obtener_resumen()} | Total cobrado: ${total_r1:,.2f}")

    # ------------------------------------------------------------------
    # OPERACIÓN 7: Reserva exitosa de Alquiler de Equipos con recargo adicional
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 7: Reserva de Alquiler de Equipos con recargo (sobrecarga)")
    r2 = sistema.crear_reserva("RES-002", "CLI-002", "SRV-002", duracion_horas=5)
    if r2:
        sistema.confirmar_reserva("RES-002")
        total_r2 = sistema.procesar_reserva("RES-002", incluir_iva=True, recargo_adicional=30000.0)
        print(f"Reserva procesada: {r2.obtener_resumen()} | Total cobrado: ${total_r2:,.2f}")

    # ------------------------------------------------------------------
    # OPERACIÓN 8: Intento de reserva fallida por servicio no disponible
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 8: Reserva fallida (servicio no disponible)")
    r3 = sistema.crear_reserva("RES-003", "CLI-001", "SRV-004", duracion_horas=3)
    print(f"Resultado reserva SRV-004: {'Creada' if r3 else 'Bloqueada por indisponibilidad (ver log)'}")

    # ------------------------------------------------------------------
    # OPERACIÓN 9: Intento de reserva fallida por cliente inactivo
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 9: Reserva fallida (cliente inactivo)")
    r4 = sistema.crear_reserva("RES-004", "CLI-003", "SRV-003", duracion_horas=2)
    print(f"Resultado reserva CLI-003: {'Creada' if r4 else 'Bloqueada por cliente inactivo (ver log)'}")

    # ------------------------------------------------------------------
    # OPERACIÓN 10: Reserva fallida por duración inválida o cliente inexistente
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 10: Reserva fallida (duración <= 0 y cliente inexistente)")
    r5 = sistema.crear_reserva("RES-005", "CLI-001", "SRV-003", duracion_horas=-4)
    r6 = sistema.crear_reserva("RES-006", "CLI-999", "SRV-003", duracion_horas=2)
    print(f"Resultados inválidos manejados con estabilidad: r5={r5}, r6={r6}")

    # ------------------------------------------------------------------
    # OPERACIÓN 11: Cancelación válida de una reserva pendiente y error al procesarla
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 11: Cancelación válida e intento inválido de procesar cancelada")
    r7 = sistema.crear_reserva("RES-007", "CLI-002", "SRV-003", duracion_horas=4)
    if r7:
        sistema.cancelar_reserva("RES-007", motivo="Cambio de agenda del cliente")
        total_r7 = sistema.procesar_reserva("RES-007")
        print(f"Estado final RES-007: {r7.estado.value} | Procesamiento posterior: {total_r7}")

    # ------------------------------------------------------------------
    # OPERACIÓN 12: Intento inválido de cancelar una reserva ya procesada y cálculo inconsistente
    # ------------------------------------------------------------------
    imprimir_separador("OPERACIÓN 12: Operación no permitida y cálculo inconsistente (encadenamiento)")
    cancelacion_invalida = sistema.cancelar_reserva("RES-001", motivo="Intento tardío")
    print(f"¿Se permitió cancelar RES-001 ya procesada?: {cancelacion_invalida}")

    # Crear reserva y forzar un descuento > 100% para demostrar encadenamiento de excepciones
    r8 = sistema.crear_reserva("RES-008", "CLI-001", "SRV-003", duracion_horas=2)
    if r8:
        sistema.confirmar_reserva("RES-008")
        total_err = sistema.procesar_reserva("RES-008", porcentaje_descuento=150.0)
        print(f"Resultado cálculo inconsistente (descuento 150%): {total_err}")

    # ------------------------------------------------------------------
    # RESUMEN FINAL DEL SISTEMA EN MEMORIA
    # ------------------------------------------------------------------
    imprimir_separador("RESUMEN FINAL DE EJECUCIÓN (SIN BASE DE DATOS)")
    print(f"Total clientes en lista  : {len(sistema.clientes)}")
    print(f"Total servicios en lista : {len(sistema.servicios)}")
    print(f"Total reservas en lista  : {len(sistema.reservas)}")
    print("Archivo de logs generado : logs/sistema_fj.log")
    print("Ejecución finalizada sin interrupciones.")


if __name__ == "__main__":
    # Ejecutar la simulación principal garantizando captura global de imprevistos
    try:
        ejecutar_simulacion()
    except Exception as error_inesperado:
        print(f"Error crítico inesperado: {error_inesperado}")
    finally:
        print("\n[FIN DEL PROGRAMA SOFTWARE FJ]")
