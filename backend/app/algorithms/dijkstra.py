"""Algoritmo de Dijkstra para rutas de entrega de Imagen Perfecta.

Modela el grafo de zonas de despacho desde la sede principal en el
Centro de Medellín y calcula el camino más corto entre dos zonas.
"""

import heapq

# Grafo de Medellín: zonas de entrega y distancias en km entre vecinas.
grafo: dict[str, dict[str, float]] = {
    "Centro": {"Robledo": 6.1, "Laureles": 4.2, "El Poblado": 5.5, "Belén": 5.8},
    "Robledo": {"Centro": 6.1, "Laureles": 4.5},
    "Laureles": {"Centro": 4.2, "Robledo": 4.5, "Belén": 3.0},
    "El Poblado": {"Centro": 5.5, "Envigado": 3.0},
    "Belén": {"Centro": 5.8, "Laureles": 3.0, "Envigado": 6.2},
    "Envigado": {"El Poblado": 3.0, "Belén": 6.2},
}

# Aristas como lista plana para exponer en la API (origen, destino, km).
ARISTAS: list[tuple[str, str, float]] = [
    ("Centro", "Robledo", 6.1),
    ("Centro", "Laureles", 4.2),
    ("Centro", "El Poblado", 5.5),
    ("Centro", "Belén", 5.8),
    ("Robledo", "Laureles", 4.5),
    ("Laureles", "Belén", 3.0),
    ("El Poblado", "Envigado", 3.0),
    ("Belén", "Envigado", 6.2),
]

NODO_PRINCIPAL = "Centro"


def obtener_grafo() -> dict:
    """Estructura del grafo de zonas para el frontend."""
    return {
        "nodos": list(grafo.keys()),
        "aristas": [
            {"origen": origen, "destino": destino, "distancia": distancia}
            for origen, destino, distancia in ARISTAS
        ],
        "nodo_principal": NODO_PRINCIPAL,
    }


def dijkstra(grafo: dict, origen: str, destino: str) -> dict:
    """Camino más corto entre dos nodos con registro de pasos.

    Complejidad O((V + E) log V) con cola de prioridad (heapq).
    """
    distancias = {nodo: float("inf") for nodo in grafo}
    anteriores: dict[str, str | None] = {nodo: None for nodo in grafo}
    distancias[origen] = 0.0
    cola: list[tuple[float, str]] = [(0.0, origen)]
    visitados: list[str] = []
    pasos: list[dict] = []

    while cola:
        distancia_actual, actual = heapq.heappop(cola)
        if actual in visitados:
            continue
        visitados.append(actual)
        pasos.append(
            {
                "nodo_actual": actual,
                "distancia_acumulada": round(distancia_actual, 1),
                "accion": (
                    f"Destino alcanzado: {destino}"
                    if actual == destino
                    else f"Se fija {actual} como definitivo a {round(distancia_actual, 1)} km"
                ),
            }
        )
        if actual == destino:
            break
        for vecino, peso in grafo[actual].items():
            nueva_distancia = distancia_actual + peso
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                anteriores[vecino] = actual
                heapq.heappush(cola, (nueva_distancia, vecino))
                pasos.append(
                    {
                        "nodo_actual": vecino,
                        "distancia_acumulada": round(nueva_distancia, 1),
                        "accion": f"Relajación: {actual} → {vecino} mejora a {round(nueva_distancia, 1)} km",
                    }
                )

    if distancias[destino] == float("inf"):
        raise ValueError(f"{destino} no es alcanzable desde {origen}")

    ruta: list[str] = []
    nodo: str | None = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = anteriores[nodo]
    ruta.reverse()

    distancia_final = round(distancias[destino], 1)
    return {
        "origen": origen,
        "destino": destino,
        "ruta": ruta,
        "distancia_km": distancia_final,
        "nodos_visitados": visitados,
        "pasos": pasos,
        "nota": (
            f"Ruta óptima calculada con Dijkstra: {distancia_final} km "
            f"de {origen} a {destino} pasando por {' → '.join(ruta)}."
        ),
    }
