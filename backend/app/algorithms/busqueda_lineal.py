import time

def buscar_pedido_lineal(pedidos: list[dict], id_pedido: str) -> dict:
    """
    Realiza una búsqueda lineal de un pedido por su id/código.
    """
    inicio = time.perf_counter()
    operaciones = 0
    encontrado = False
    pedido_encontrado = None
    
    for pedido in pedidos:
        operaciones += 1
        # Comparamos tanto con 'codigo' como con 'id' por si acaso
        if pedido.get('codigo') == id_pedido or pedido.get('id') == id_pedido:
            encontrado = True
            pedido_encontrado = pedido
            break
            
    fin = time.perf_counter()
    tiempo_ms = (fin - inicio) * 1000
    
    return {
        "encontrado": encontrado,
        "pedido": pedido_encontrado,
        "operaciones": operaciones,
        "tiempo_ms": tiempo_ms,
        "complejidad": "O(n)",
        "tamanio_entrada": len(pedidos),
        "id_buscado": id_pedido,
        "mejor_caso": "1 operación (elemento al inicio)",
        "peor_caso": "n operaciones (elemento al final o no existe)"
    }
