"""Búsquedas y complejidad (PDF ProgramacionAvanzada).

Genera conjuntos sinteticos escalables (IP-0001..IP-n) para analizar
O(n), O(log n) y O(n^2) sin sobrecargar la base de datos.
"""
import math


def generar_pedidos_sinteticos(tamanio: int) -> list[str]:
    """Conjunto temporal ordenado IP-0001..IP-n (no toca la DB)."""
    return [f"IP-{i:04d}" for i in range(1, tamanio + 1)]


def busqueda_lineal(tamanio: int, id_buscado: str) -> dict:
    """Búsqueda lineal O(n): recorre uno a uno contando operaciones.

    Mejor caso: 1 operacion (primer elemento).
    Peor caso: n operaciones (ultimo o no encontrado).
    """
    pedidos = generar_pedidos_sinteticos(tamanio)
    operaciones = 0
    posicion = -1
    for idx, codigo in enumerate(pedidos):
        operaciones += 1
        if codigo == id_buscado:
            posicion = idx
            break
    return {
        "algoritmo": "Búsqueda Lineal",
        "tamanio": tamanio,
        "id_buscado": id_buscado,
        "encontrado": posicion >= 0,
        "posicion": posicion,
        "operaciones": operaciones,
        "complejidad": "O(n)",
        "explicacion": (
            "Recorre la lista pedazo a pedazo: en el peor caso revisa los n pedidos "
            "(no encontrado o ultimo elemento) y en el mejor solo 1."
        ),
    }


def busqueda_binaria(tamanio: int, id_buscado: str) -> dict:
    """Búsqueda binaria O(log n): requiere datos ordenados (PDF pag. 18)."""
    pedidos = generar_pedidos_sinteticos(tamanio)
    operaciones = 0
    izquierda, derecha = 0, len(pedidos) - 1
    posicion = -1
    while izquierda <= derecha:
        operaciones += 1
        medio = (izquierda + derecha) // 2
        if pedidos[medio] == id_buscado:
            posicion = medio
            break
        if pedidos[medio] < id_buscado:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return {
        "algoritmo": "Búsqueda Binaria",
        "tamanio": tamanio,
        "id_buscado": id_buscado,
        "encontrado": posicion >= 0,
        "posicion": posicion,
        "operaciones": operaciones,
        "complejidad": "O(log n)",
        "maximo_teorico": math.ceil(math.log2(tamanio)) if tamanio > 1 else 1,
        "explicacion": (
            "Divide el espacio a la mitad en cada paso (requiere orden): "
            "100.000 pedidos se resuelven en <= 17 operaciones."
        ),
    }


def _conteo_lineal(n: int) -> int:
    ops = 0
    for _ in range(n):
        ops += 1
    return ops


def _conteo_cuadratico(n: int) -> int:
    """Bucles anidados estilo tabla de multiplicar (PDF pag. 19-21)."""
    ops = 0
    for i in range(1, n + 1):
        for _ in range(1, i + 1):
            ops += 1
    return ops


def matriz_complejidad(tamanios: list[int]) -> list[dict]:
    """Comparativa para n en {10, 100, 1000, 10000, 100000} (PDF pag. 32)."""
    filas = []
    for n in tamanios:
        cuad = _conteo_cuadratico(n)
        filas.append({
            "tamanio": n,
            "lineal": {"operaciones": _conteo_lineal(n), "complejidad": "O(n)"},
            "cuadratico": {"operaciones": cuad, "complejidad": "O(n²)"},
            "logaritmico": {
                "operaciones": max(1, math.ceil(math.log2(n))) if n > 1 else 1,
                "complejidad": "O(log n)",
            },
            "constante": {"operaciones": 1, "complejidad": "O(1)"},
            "suma_gauss": n * (n + 1) // 2,
        })
    return filas


def mejor_peor_caso(n: int) -> dict:
    """Mejor y peor caso de lineal y binaria sobre el mismo conjunto."""
    pedidos = generar_pedidos_sinteticos(n)
    return {
        "n": n,
        "lineal": {
            "mejor": {"caso": "IP-0001 (primer elemento)", "operaciones": 1},
            "peor": {"caso": f"IP-{n:04d} (último) / no encontrado",
                     "operaciones": n},
        },
        "binaria": {
            "mejor": {"caso": "elemento en el medio", "operaciones": 1},
            "peor": {"caso": "no encontrado",
                     "operaciones": max(1, math.ceil(math.log2(n))) if n > 1 else 1},
        },
        "conclusion": (
            "Lineal: mejor O(1), peor O(n). "
            "Binaria: mejor O(1), peor O(log n) — siempre que los datos estén ordenados."
        ),
    }
