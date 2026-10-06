"""Endpoints formato exacto del profesor (PDF Técnicas de resolución).

Contrato: cada transacción llega con su hash HMAC-SHA256; el server valida
hash por transacción (pag. 18: ¿Coincide? -> Aceptar/Rechazar) y aplica la
ventana deslizante por turno (10/6/3 s, umbral 3) para detectar POSIBLE_FRAUDE.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.transaccion import TransaccionProfe
from app.services import transaccion_service as ts
from app.services.transaccion_service import DuplicadoError, HashInvalidoError

router = APIRouter(prefix="/api/transacciones", tags=["Transacciones profe"])

@router.post("")
def recibir_una(t: TransaccionProfe, db: Session = Depends(get_db)):
    """Recibe {idTxn,user,date,value,paymentMethod,hash}.

    Valida el hash de ESTA transacción: no coincide -> rechazada (400).
    Coincide -> ventana deslizante -> NORMAL o POSIBLE_FRAUDE.
    """
    try:
        p, estado = ts.ingest_una(db, t)
    except HashInvalidoError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                             "Transacción rechazada: HASH_INVALIDO")
    except DuplicadoError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Transacción rechazada: RECHAZADO_DUPLICADO")
    return {"idTxn": t.idTxn, "codigo": p.codigo, "pedido_id": p.id,
            "user": t.user, "deteccion": estado, "hash_valido": True}

@router.post("/lote")
def recibir_lote(items: List[TransaccionProfe], db: Session = Depends(get_db)):
    """Lote de hasta 1000 (el profe envía 500). Ordena por date, valida todo."""
    if len(items) > 1000:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Máximo 1000 por lote")
    return ts.ingest_lote(db, items)

@router.get("")
def listar(db: Session = Depends(get_db)):
    """Log del contrato profesor: solo pedidos originados por transacciones (idTxn)."""
    from app.models.pedido import Pedido
    rows = db.query(Pedido).filter(Pedido.id_txn.isnot(None)).order_by(
        Pedido.fecha_txn.desc()).limit(100).all()
    return [{"idTxn": r.id_txn, "user": r.cliente.email if r.cliente else None,
             "date": r.fecha_txn.isoformat() if r.fecha_txn else None,
             "value": r.valor, "paymentMethod": r.metodo_pago, "hash": r.hash,
             "codigo": r.codigo} for r in rows]
