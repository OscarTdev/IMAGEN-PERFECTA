from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.pedido import PedidoResponse, PedidoCreate, PedidoEstadoUpdate, PedidoPut, PedidoPatch
from app.services import pedido_service, cliente_service

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"])

@router.get("", response_model=List[PedidoResponse])
def listar(db: Session = Depends(get_db)):
    return pedido_service.get_pedidos(db)

@router.post("", status_code=status.HTTP_201_CREATED)
def crear(pedido: PedidoCreate, db: Session = Depends(get_db)):
    """POST crear pedido: valida hash + ventana deslizante + turnos."""
    if not cliente_service.get_cliente(db, pedido.cliente_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    obj, estado = pedido_service.create_pedido(db, pedido)
    data = PedidoResponse.model_validate(obj).model_dump()
    data["deteccion"] = estado
    return data

@router.get("/buscar", response_model=List[PedidoResponse])
def buscar(producto: str, db: Session = Depends(get_db)):
    """Búsqueda eficiente por producto (includes)."""
    return pedido_service.buscar_por_producto(db, producto)

@router.post("/lote")
def crear_lote(items: List[PedidoCreate], db: Session = Depends(get_db)):
    """POST lote: recibe hasta 1000 transacciones (el profe envía 500).

    Las ordena cronológicamente y aplica validación + hash + ventana + turnos.
    """
    if len(items) > 1000:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Máximo 1000 por lote")
    return pedido_service.create_lote(db, items)

@router.get("/{id}", response_model=PedidoResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    p = pedido_service.get_pedido(db, id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    return p

@router.put("/{id}", response_model=PedidoResponse)
def reemplazar(id: int, data: PedidoPut, db: Session = Depends(get_db)):
    """PUT: reemplazo completo."""
    p = pedido_service.put_pedido(db, id, data)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    return p

@router.patch("/{id}", response_model=PedidoResponse)
def parcial(id: int, data: PedidoPatch, db: Session = Depends(get_db)):
    """PATCH: actualización parcial."""
    p = pedido_service.patch_pedido(db, id, data)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    return p

@router.put("/{id}/estado", response_model=PedidoResponse)
def estado(id: int, data: PedidoEstadoUpdate, db: Session = Depends(get_db)):
    p = pedido_service.update_estado(db, id, data.estado)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    return p

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id: int, db: Session = Depends(get_db)):
    if not pedido_service.delete_pedido(db, id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    return None
