from pydantic import BaseModel
from typing import Union

class TransaccionProfe(BaseModel):
    idTxn: int
    user: str
    date: str
    value: Union[int, float]
    paymentMethod: str
    hash: str
    ip: Union[str, None] = None
