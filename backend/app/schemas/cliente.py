from pydantic import BaseModel, field_validator
from typing import Literal, Optional
from datetime import datetime

class ClienteBase(BaseModel):
    nombre: str
    telefono: str
    tipo_cliente: Literal['Fotógrafo', 'Aficionado', 'Nuevo cliente']
    email: Optional[str] = None
    estado: Optional[str] = "activo"

    @field_validator('tipo_cliente')
    def validate_tipo_cliente(cls, v: str) -> str:
        valid_types = ['Fotógrafo', 'Aficionado', 'Nuevo cliente']
        if v not in valid_types:
            raise ValueError(f'tipo_cliente must be one of {valid_types}')
        return v

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    """PUT completo: exige todos los campos base."""
    nombre: str
    telefono: str
    tipo_cliente: Literal['Fotógrafo', 'Aficionado', 'Nuevo cliente']
    email: Optional[str] = None
    estado: Optional[str] = "activo"

class ClientePatch(BaseModel):
    """PATCH parcial: solo lo que se quiere cambiar."""
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    estado: Optional[str] = None
    tipo_cliente: Optional[Literal['Fotógrafo', 'Aficionado', 'Nuevo cliente']] = None

class ClienteResponse(ClienteBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = {'from_attributes': True}
