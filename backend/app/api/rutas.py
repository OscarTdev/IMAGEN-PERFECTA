from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.algorithms.dijkstra import dijkstra, obtener_grafo, grafo
from app.algorithms.combustible import calcular_combustible

router = APIRouter(prefix="/api/rutas", tags=["rutas"])

# --- Models ---

class DijkstraRequest(BaseModel):
    origen: str = "Centro"
    destino: str

class CombustibleRequest(BaseModel):
    distancia_km: float
    rendimiento: float = 12.0
    precio_litro: float = 14500.0

# --- Endpoints ---

@router.get("/grafo")
def get_grafo():
    """Retorna la estructura del grafo de zonas."""
    return obtener_grafo()

@router.post("/dijkstra")
def post_dijkstra(req: DijkstraRequest):
    """Calcula la ruta más corta entre origen y destino usando Dijkstra."""
    if req.origen not in grafo:
        raise HTTPException(status_code=404, detail=f"Nodo origen '{req.origen}' no encontrado en el grafo.")
    if req.destino not in grafo:
        raise HTTPException(status_code=404, detail=f"Nodo destino '{req.destino}' no encontrado en el grafo.")
        
    return dijkstra(grafo, req.origen, req.destino)

@router.post("/combustible")
def post_combustible(req: CombustibleRequest):
    """Calcula el costo del combustible para una distancia dada."""
    if req.distancia_km <= 0:
        raise HTTPException(status_code=400, detail="La distancia debe ser mayor a 0.")
        
    return calcular_combustible(
        distancia_km=req.distancia_km,
        rendimiento_km_por_litro=req.rendimiento,
        precio_por_litro=req.precio_litro
    )
