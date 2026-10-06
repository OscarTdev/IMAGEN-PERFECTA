"""Endpoints de estructuras de datos de Imagen Perfecta.

Expone la lista enlazada (flujo de producción), la pila LIFO (historial),
la cola FIFO (turno de producción) y el heap de prioridad (pedidos urgentes)
implementadas en app/services/estructuras.py.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.estructuras import (
    cola_produccion,
    heap_prioridad,
    lista_produccion,
    pila_historial,
)

router = APIRouter(prefix="/api/estructuras", tags=["Estructuras de Datos"])

PRIORIDADES = {"Urgente": 1, "Alta": 2, "Normal": 3}


class EtapaRequest(BaseModel):
    etapa: str


class PilaRequest(BaseModel):
    accion: str
    detalle: str = "Acción del sistema"


class ColaRequest(BaseModel):
    codigo: str
    cliente: str
    productos: str = ""


class HeapRequest(BaseModel):
    codigo: str
    cliente: str
    prioridad: str = "Normal"


# ─── Lista Enlazada: flujo de producción ────────────────────────────


@router.get("/lista-enlazada")
def obtener_lista():
    """Recorre la lista enlazada del flujo de producción."""
    return lista_produccion.to_dict()


@router.post("/lista-enlazada/agregar")
def agregar_etapa(req: EtapaRequest):
    """Agrega una etapa al final del flujo de producción."""
    etapa = req.etapa.strip()
    if not etapa:
        raise HTTPException(status_code=400, detail="La etapa no puede estar vacía.")
    lista_produccion.agregar(etapa)
    return lista_produccion.to_dict()


# ─── Pila LIFO: historial de acciones ────────────────────────────────


@router.get("/pila")
def obtener_pila():
    """Muestra la pila del historial de acciones recientes."""
    return pila_historial.to_dict()


@router.post("/pila/push")
def push_pila(req: PilaRequest):
    """Apila una acción en el historial (queda en la cima)."""
    if not req.accion.strip():
        raise HTTPException(status_code=400, detail="La acción no puede estar vacía.")
    pila_historial.push(
        {
            "accion": req.accion.strip(),
            "detalle": req.detalle,
            "timestamp": datetime.now().isoformat(),
        }
    )
    return pila_historial.to_dict()


@router.post("/pila/pop")
def pop_pila():
    """Extrae la acción en la cima de la pila."""
    eliminado = pila_historial.pop()
    if eliminado is None:
        raise HTTPException(status_code=400, detail="La pila está vacía.")
    return {"eliminado": eliminado, "pila": pila_historial.to_dict()}


# ─── Cola FIFO: turno de producción ─────────────────────────────────


@router.get("/cola")
def obtener_cola():
    """Muestra la cola FIFO del turno de producción."""
    return cola_produccion.to_dict()


@router.post("/cola/enqueue")
def enqueue_cola(req: ColaRequest):
    """Agrega un pedido al final de la cola (llegada)."""
    if not req.codigo.strip():
        raise HTTPException(status_code=400, detail="El código no puede estar vacío.")
    cola_produccion.enqueue(
        {
            "codigo": req.codigo.strip(),
            "cliente": req.cliente.strip(),
            "productos": req.productos,
            "fecha": datetime.now().isoformat(),
        }
    )
    return cola_produccion.to_dict()


@router.post("/cola/dequeue")
def dequeue_cola():
    """Atiende el primer pedido de la cola (primero en llegar)."""
    atendido = cola_produccion.dequeue()
    if atendido is None:
        raise HTTPException(status_code=400, detail="La cola está vacía.")
    return {"atendido": atendido, "cola": cola_produccion.to_dict()}


# ─── Heap: cola de prioridad ─────────────────────────────────────────


@router.get("/heap")
def obtener_heap():
    """Muestra el heap de pedidos por prioridad (1 Urgente, 2 Alta, 3 Normal)."""
    return heap_prioridad.to_dict()


@router.post("/heap/insertar")
def insertar_heap(req: HeapRequest):
    """Inserta un pedido en la cola de prioridad."""
    prioridad = req.prioridad.strip().capitalize()
    if prioridad not in PRIORIDADES:
        raise HTTPException(
            status_code=400,
            detail="Prioridad inválida. Usa Urgente, Alta o Normal.",
        )
    heap_prioridad.insertar(
        {"codigo": req.codigo.strip(), "cliente": req.cliente.strip()},
        PRIORIDADES[prioridad],
    )
    return heap_prioridad.to_dict()


@router.post("/heap/extraer")
def extraer_heap():
    """Atiende el pedido con mayor prioridad (menor número)."""
    atendido = heap_prioridad.extraer()
    if atendido is None:
        raise HTTPException(status_code=400, detail="El heap está vacío.")
    return {"atendido": atendido, "heap": heap_prioridad.to_dict()}
