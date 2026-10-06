from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class AnomaliaResponse(BaseModel):
    id: int
    pedido_id: Optional[int] = None
    cliente_id: Optional[int] = None
    tipo: str
    nivel: str
    cantidad_transacciones: int
    ventana_segundos: int
    estado_revision: str
    detalle: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    model_config = {'from_attributes': True}

class AnomaliaRevision(BaseModel):
    estado_revision: Literal['abierta', 'revisada', 'descartada']
