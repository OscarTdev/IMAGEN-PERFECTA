from pydantic import BaseModel
from typing import Union

class TransaccionProfe(BaseModel):
    """Formato exacto esperado por el profesor (PDF Técnicas, pag. 40).

    El hash es REQUERIDO: cada transacción llega firmada con HMAC-SHA256
    sobre su propio payload (llave del PDF: mi_llave_privada_123).
    El server valida el hash por transacción y rechaza si no coincide.
    """
    idTxn: int
    user: str
    date: str
    value: Union[int, float]
    paymentMethod: str
    hash: str
    ip: Union[str, None] = None
