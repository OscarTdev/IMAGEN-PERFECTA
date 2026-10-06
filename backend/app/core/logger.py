"""Logs y diagnóstico (PDF: qué ocurrió, cuándo y dónde). Fuera del código."""
import logging
import os
from datetime import datetime
from pathlib import Path

def _log_path() -> Path:
    custom = os.getenv("IMAGEN_LOG_PATH")
    if custom:
        p = Path(custom).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    d = Path.home() / ".imagen-perfecta"
    d.mkdir(parents=True, exist_ok=True)
    return d / "app.log"

LOG_PATH = _log_path()

_logger = logging.getLogger("imagen_perfecta")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    _logger.addHandler(fh)

def log_evento(que: str, donde: str = "") -> None:
    _logger.info(f"{que} | donde={donde or '?'}")

def log_error(que: str, donde: str = "") -> None:
    _logger.error(f"{que} | donde={donde or '?'}")

def dividir_seguro(a: float, b: float) -> float | None:
    """Ejemplo PDF dividir(a,b) con log en app.log."""
    try:
        return a / b
    except ZeroDivisionError:
        log_error("Error intentando dividir por cero", donde="dividir_seguro")
        return None
