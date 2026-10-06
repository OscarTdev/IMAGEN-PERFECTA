"""Hash de transacción estilo PDF: HMAC-SHA256 canónico."""
import hashlib
import hmac
import json


def canon(datos: dict) -> str:
    """Serialización canónica (sort_keys + separadores compactos)."""
    return json.dumps(datos, sort_keys=True, separators=(",", ":"), default=str)


def generar_hash(datos: dict, llave: bytes) -> str:
    return hmac.new(llave, canon(datos).encode("utf-8"), hashlib.sha256).hexdigest()


def verificar_hash(datos: dict, llave: bytes, recibido: str) -> bool:
    if not recibido:
        return False
    esperado = generar_hash(datos, llave)
    return hmac.compare_digest(esperado, recibido.lower().strip())
