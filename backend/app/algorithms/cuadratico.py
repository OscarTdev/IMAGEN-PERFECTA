import time

def comparar_pedidos(pedidos: list[dict]) -> dict:
    """
    Algoritmo O(n^2) que compara todos los pedidos entre sí para buscar similitudes.
    """
    inicio = time.perf_counter()
    operaciones = 0
    n = len(pedidos)
    pares_encontrados = 0
    
    for i in range(n):
        for j in range(i + 1, n):
            operaciones += 1
            # Comparamos estado y prioridad
            if pedidos[i].get('estado') == pedidos[j].get('estado') and \
               pedidos[i].get('prioridad') == pedidos[j].get('prioridad'):
                pares_encontrados += 1
                
    fin = time.perf_counter()
    tiempo_ms = (fin - inicio) * 1000
    
    return {
        "n": n,
        "operaciones": operaciones,
        "tiempo_ms": tiempo_ms,
        "complejidad": "O(n²)",
        "comparaciones_detalle": "Se comparan todos los pares posibles de pedidos para buscar similitudes en estado y prioridad",
        "pares_encontrados": pares_encontrados
    }
