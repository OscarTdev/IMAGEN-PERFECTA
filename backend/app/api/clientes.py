from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.cliente import ClienteResponse, ClienteCreate, ClienteUpdate, ClientePatch
from app.services import cliente_service

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

@router.get("", response_model=List[ClienteResponse])
def listar(db: Session = Depends(get_db)):
    return cliente_service.get_clientes(db)

@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear(cliente: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.create_cliente(db, cliente)

@router.get("/{id}", response_model=ClienteResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    c = cliente_service.get_cliente(db, id)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    return c

@router.put("/{id}", response_model=ClienteResponse)
def reemplazar(id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    """PUT: reemplazo completo del cliente."""
    c = cliente_service.put_cliente(db, id, data)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    return c

@router.patch("/{id}", response_model=ClienteResponse)
def parcial(id: int, data: ClientePatch, db: Session = Depends(get_db)):
    """PATCH: actualización parcial."""
    c = cliente_service.patch_cliente(db, id, data)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    return c

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id: int, db: Session = Depends(get_db)):
    if not cliente_service.delete_cliente(db, id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    return None
