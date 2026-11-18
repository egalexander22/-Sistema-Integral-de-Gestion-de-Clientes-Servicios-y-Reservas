# Software FJ — Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto desarrollado para la **Fase 4 (Componente Práctico)** del curso **Programación (213023)** de la Universidad Nacional Abierta y a Distancia (UNAD).

## Descripción

Aplicación orientada a objetos en **Python** (sin uso de bases de datos) para la gestión de clientes, servicios (reservas de salas, alquiler de equipos y asesorías especializadas) y reservas, implementando:

- **Abstracción y Herencia**: clase abstracta `EntidadSistema` y clase abstracta `Servicio` con tres subclases especializadas (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`).
- **Polimorfismo y Sobrecarga**: sobrescritura de `calcular_costo()`, `describir_servicio()` y `validar_parametros()`, además de sobrecarga mediante parámetros opcionales en `calcular_costo_con_opciones()`.
- **Encapsulación y Validaciones**: propiedades (`@property` y setters) con validación estricta de datos personales, tarifas, duraciones y estados.
- **Manejo Avanzado de Excepciones**: jerarquía propia (`SoftwareFJError`), uso de `try/except`, `try/except/else`, `try/except/finally` y encadenamiento (`raise ... from ...`).
- **Persistencia Exclusiva en Logs**: registro de eventos y errores en `logs/sistema_fj.log` mediante `GestorLogs`.

## Estructura del Repositorio

```text
software_fj_reservas/
├── main.py                              # Simulación de 12 operaciones completas (válidas e inválidas)
├── README.md                            # Documentación del proyecto
├── .gitignore                           # Exclusiones de caché, entornos virtuales y logs locales
├── src/
│   ├── __init__.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── excepciones.py               # Excepciones personalizadas (SoftwareFJError y derivadas)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── entidad.py                   # Clase abstracta EntidadSistema
│   │   ├── cliente.py                   # Clase Cliente con encapsulación y validaciones
│   │   ├── servicio.py                  # Clase abstracta Servicio y sobrecarga de cálculo
│   │   ├── servicios_especializados.py  # ReservaSala, AlquilerEquipo, AsesoriaEspecializada
│   │   └── reserva.py                   # Clase Reserva y ciclo de estados (EstadoReserva)
│   ├── services/
│   │   ├── __init__.py
│   │   └── gestor_sistema.py            # Orquestador en memoria SistemaSoftwareFJ
│   └── utils/
│       ├── __init__.py
│       └── logger.py                    # GestorLogs para registro en logs/sistema_fj.log
└── tests/
    └── test_sistema.py                  # Pruebas unitarias con unittest
```

## Requisitos y Ejecución

Requiere **Python 3.10+** (solo utiliza la biblioteca estándar, sin dependencias externas).

```bash
# 1. Ejecutar la simulación principal (12 operaciones completas)
python3 main.py

# 2. Ejecutar las pruebas unitarias
python3 -m unittest discover -s tests -v
```

Al ejecutar `main.py`, se creará automáticamente el archivo `logs/sistema_fj.log` con la traza completa de eventos y excepciones controladas.

## Flujo Sugerido de Trabajo Colaborativo en GitHub (5 Integrantes)

