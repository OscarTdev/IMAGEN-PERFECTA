"""Configuración central (concepto PDF: parámetros configurables).

Ventana deslizante POR TURNO (segundos, configurable):
- Mañana  05:00:01 - 12:00:00  -> ventana 10 s
- Tarde   12:00:01 - 20:00:00  -> ventana 6 s
- Noche   20:00:01 - 05:00:00  -> ventana 3 s
Umbral: 3 transacciones (configurable).
"""
import os
from datetime import datetime

UMBRAL_TRANSACCIONES: int = int(os.getenv("IP_UMBRAL_TX", "3"))

# Llave secreta para HMAC (PDF: b"mi_llave_privada_123"). No hardcodear en prod.
LLAVE_SECRETA: bytes = os.getenv("IP_LLAVE_SECRETA", "mi_llave_privada_123").encode("utf-8")

# Hash autorizado que se le ENTREGA al profesor: funciona como credencial.
# El profesor envia sus transacciones (datos arbitrarios) con este mismo hash
# en el campo "hash" y el sistema las acepta y evalua por ventanas.
# Cualquier hash distinto se rechaza (PDF pag. 18: no coincide -> rechazar).
HASH_AUTORIZADO: str = os.getenv(
    "IP_HASH_AUTORIZADO",
    "d94fa63f732e8d6b2dc28d408949d19f13b7568335969879d6bbde3777178756",
)

# Ventana en SEGUNDOS por turno (esto es lo configurable del PDF, no son ventas).
VENTANAS_TURNO = {
    "manana": int(os.getenv("IP_VENTANA_MANANA", "10")),
    "tarde": int(os.getenv("IP_VENTANA_TARDE", "6")),
    "noche": int(os.getenv("IP_VENTANA_NOCHE", "3")),
}

# Compatibilidad: valor por defecto si algo pide ventana única.
VENTANA_SEGUNDOS: int = int(os.getenv("IP_VENTANA_SEGUNDOS", str(VENTANAS_TURNO["noche"])))


def turno_de_fecha(fecha: datetime) -> str:
    """Turno exacto con límites del PDF (incluye segundos)."""
    t = fecha.time()
    h, m, s = t.hour, t.minute, t.second + t.microsecond / 1e6
    seg = h * 3600 + m * 60 + s
    man_ini = 5 * 3600 + 1          # 05:00:01
    man_fin = 12 * 3600             # 12:00:00
    tar_ini = 12 * 3600 + 1         # 12:00:01
    tar_fin = 20 * 3600             # 20:00:00
    if man_ini <= seg <= man_fin:
        return "manana"
    if tar_ini <= seg <= tar_fin:
        return "tarde"
    return "noche"  # 20:00:01 - 05:00:00


def turno_de_hora(hora: int) -> str:
    """Compat: aproximación solo por hora."""
    if 5 < hora <= 12 or hora == 5:
        return "manana" if hora <= 12 else "tarde"
    if 12 < hora <= 20:
        return "tarde"
    return "noche"


def ventana_por_turno(fecha: datetime) -> int:
    return VENTANAS_TURNO[turno_de_fecha(fecha)]


def get_config() -> dict:
    return {
        "ventana_segundos": VENTANA_SEGUNDOS,
        "umbral_transacciones": UMBRAL_TRANSACCIONES,
        "ventanas_turno": dict(VENTANAS_TURNO),
    }


def set_config(ventana_segundos: int | None = None, umbral: int | None = None,
               limites: dict | None = None, ventanas_turno: dict | None = None) -> dict:
    global VENTANA_SEGUNDOS, UMBRAL_TRANSACCIONES
    data = ventanas_turno or limites  # acepta ambos nombres desde el frontend
    if data:
        for k in ("manana", "tarde", "noche"):
            if k in data and int(data[k]) > 0:
                VENTANAS_TURNO[k] = int(data[k])
    if ventana_segundos is not None and ventana_segundos > 0:
        VENTANA_SEGUNDOS = ventana_segundos
        VENTANAS_TURNO["noche"] = ventana_segundos
    if umbral is not None and umbral > 1:
        UMBRAL_TRANSACCIONES = umbral
    return get_config()
