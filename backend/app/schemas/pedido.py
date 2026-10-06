from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import datetime

METODOS = ['Efectivo', 'Tarjeta', 'Transferencia', 'Nequi']

class PedidoBase(BaseModel):
    cliente_id: int
    productos: str
    cantidad_total: int = Field(gt=0, description="Cantidad total de productos, debe ser mayor a 0")
    prioridad: Literal['Normal', 'Alta', 'Urgente']
    direccion_entrega: str
    valor: float = Field(default=0, ge=0)
    metodo_pago: str = "Efectivo"
    ip: Optional[str] = None
    fecha_txn: Optional[datetime] = None

    @field_validator('prioridad')
    def validate_prioridad(cls, v: str) -> str:
        if v not in ['Normal', 'Alta', 'Urgente']:
            raise ValueError('prioridad inválida')
        return v

class PedidoCreate(PedidoBase):
    """POST crear. hash opcional: si se envía se verifica, si no se genera."""
    hash: Optional[str] = None

class PedidoPut(PedidoBase):
    """PUT reemplazo completo."""
    pass

class PedidoPatch(BaseModel):
    """PATCH parcial: solo lo que se requiere cambiar."""
    productos: Optional[str] = None
    cantidad_total: Optional[int] = Field(default=None, gt=0)
    prioridad: Optional[Literal['Normal', 'Alta', 'Urgente']] = None
    direccion_entrega: Optional[str] = None
    valor: Optional[float] = Field(default=None, ge=0)
    metodo_pago: Optional[str] = None
    estado: Optional[Literal['Solicitado', 'En proceso', 'Listo', 'Entregado']] = None

class PedidoResponse(PedidoBase):
    id: int
    codigo: str
    fecha: datetime
    estado: str
    hash: Optional[str] = None

    model_config = {'from_attributes': True}

class PedidoEstadoUpdate(BaseModel):
    estado: Literal['Solicitado', 'En proceso', 'Listo', 'Entregado']
