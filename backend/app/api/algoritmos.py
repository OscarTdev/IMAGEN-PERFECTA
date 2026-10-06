"""Endpoints académicos: complejidad, Big O, progresiones, recursividad, regresión.

PDF ProgramacionAvanzada: casos 1-4 (búsqueda, conteo, fidelización, predicción).
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.algorithms import busquedas, matematicas

router = APIRouter(prefix="/api/algoritmos", tags=["Algoritmos"])


class BusquedaRequest(BaseModel):
    tamanio: int = Field(ge=0, le=100000, description="Tamaño del conjunto IP-0001..IP-n")
    id_buscado: str


class ComplejidadRequest(BaseModel):
    tamanios: list[int] = Field(default=[10, 100, 1000, 10000, 100000])


class MejorPeorRequest(BaseModel):
    n: int = Field(ge=1, le=100000)


class SumatoriaRequest(BaseModel):
    n: int = Field(ge=0, le=1000000)


class ProgresionRequest(BaseModel):
    a1: int = Field(default=2, ge=1, description="Primer término (productos semana 1)")
    d: int = Field(default=2, ge=1, description="Diferencia común (incremento semanal)")
    objetivos: list[int] = Field(default=[42, 72, 120])


class RecursividadRequest(BaseModel):
    productos: list[str] = Field(default_factory=list)


class RegresionRequest(BaseModel):
    datos: list[dict] | None = Field(default=None, description="[{dia, pedidos}]")
    dias_prediccion: list[int] = Field(default=[2, 5, 7])


@router.post("/busqueda-lineal")
def post_busqueda_lineal(req: BusquedaRequest):
    """Búsqueda secuencial O(n) con conteo exacto de comparaciones."""
    return busquedas.busqueda_lineal(req.tamanio, req.id_buscado)


@router.post("/busqueda-binaria")
def post_busqueda_binaria(req: BusquedaRequest):
    """Búsqueda por bisección O(log n) sobre pedidos ordenados."""
    return busquedas.busqueda_binaria(req.tamanio, req.id_buscado)


@router.post("/complejidad")
def post_complejidad(req: ComplejidadRequest):
    """Matriz comparativa O(1), O(log n), O(n), O(n²) para cada tamaño."""
    return {"resultados": busquedas.matriz_complejidad(req.tamanios)}


@router.post("/mejor-peor-caso")
def post_mejor_peor(req: MejorPeorRequest):
    """Mejor y peor caso de búsqueda lineal y binaria."""
    return busquedas.mejor_peor_caso(req.n)


@router.post("/sumatoria")
def post_sumatoria(req: SumatoriaRequest):
    """Sumatoria de Gauss S = n(n+1)/2 vs conteo iterativo."""
    return matematicas.sumatoria_gauss(req.n)


@router.post("/progresion")
def post_progresion(req: ProgresionRequest):
    """Progresión aritmética aₙ = a₁ + (n-1)d: semanas para 42/72/120 productos."""
    return matematicas.progresion_aritmetica(req.a1, req.d, req.objetivos)


@router.post("/recursividad")
def post_recursividad(req: RecursividadRequest):
    """Procesamiento recursivo de productos con caso base índice >= n."""
    return matematicas.procesar_recursivo(req.productos)


@router.post("/regresion")
def post_regresion(req: RegresionRequest):
    """Regresión lineal por mínimos cuadrados para proyectar ventas."""
    return matematicas.regresion_lineal(req.datos, req.dias_prediccion)
