from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClientePatch
from app.core.logger import log_evento

def get_clientes(db: Session) -> List[Cliente]:
    return db.query(Cliente).all()

def get_cliente(db: Session, id: int) -> Optional[Cliente]:
    # Búsqueda eficiente: filtro directo + índice PK (concepto PDF find())
    return db.query(Cliente).filter(Cliente.id == id).first()

def buscar_por_email(db: Session, email: str) -> Optional[Cliente]:
    # Diccionario/objeto como índice (PDF: búsqueda eficiente)
    return db.query(Cliente).filter(Cliente.email == email).first()

def create_cliente(db: Session, data: ClienteCreate) -> Cliente:
    db_cliente = Cliente(**data.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    log_evento(f"Cliente creado id={db_cliente.id}", donde="cliente_service.create")
    return db_cliente

def put_cliente(db: Session, id: int, data: ClienteUpdate) -> Optional[Cliente]:
    """PUT: reemplazo completo."""
    c = get_cliente(db, id)
    if not c:
        return None
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c

def patch_cliente(db: Session, id: int, data: ClientePatch) -> Optional[Cliente]:
    """PATCH: actualización parcial."""
    c = get_cliente(db, id)
    if not c:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c

def delete_cliente(db: Session, id: int) -> bool:
    c = get_cliente(db, id)
    if not c:
        return False
    db.delete(c)
    db.commit()
    log_evento(f"Cliente eliminado id={id}", donde="cliente_service.delete")
    return True
