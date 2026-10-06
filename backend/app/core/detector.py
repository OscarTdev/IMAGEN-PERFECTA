"""Ventana deslizante temporal por cliente (PDF Appresso -> Imagen Perfecta).

Regla: N o más pedidos del mismo cliente dentro de X segundos => POSIBLE_FRAUDE.
Eficiente: sale uno / entra uno con deque, sin reprocesar todo.
"""
from collections import defaultdict, deque
from datetime import datetime, timedelta

_ventanas: dict[int, deque] = defaultdict(deque)


def _to_dt(v) -> datetime:
    if isinstance(v, datetime):
        return v
    try:
        return datetime.fromisoformat(str(v))
    except ValueError:
        return datetime.utcnow()


def analizar(cliente_id: int, fecha_actual, ventana_segundos: int, historial_fechas: list | None = None) -> dict:
    """Agrega evento, purga fuera de ventana y cuenta. Ventanas separadas por cliente."""
    actual = _to_dt(fecha_actual)
    dq = _ventanas[cliente_id]
    base = list(historial_fechas) if historial_fechas is not None else list(dq)
    # Orden cronológico (PDF: ordenar antes de analizar)
    base = sorted((_to_dt(x) for x in base)) if base else []
    base.append(actual)
    limite = actual - timedelta(seconds=ventana_segundos)
    # Deslizar: eliminar fuera de ventana (sale uno)
    ventana = [f for f in base if f >= limite]
    _ventanas[cliente_id] = deque(ventana)
    return {
        "cliente_id": cliente_id,
        "cantidad_en_ventana": len(ventana),
        "ventana_segundos": ventana_segundos,
        "ventana": [f.isoformat() for f in ventana],
    }


def reset() -> None:
    _ventanas.clear()
