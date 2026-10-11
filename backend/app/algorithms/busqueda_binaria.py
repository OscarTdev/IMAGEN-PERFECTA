import time

def buscar_pedido_binario(pedidos: list[dict], id_pedido: str) -> dict:
    """
    Realiza una búsqueda binaria asumiendo que los pedidos están ordenados por código.
    """
    inicio = time.perf_counter()
    operaciones = 0
    encontrado = False
    pedido_encontrado = None
    
    izq = 0
    der = len(pedidos) - 1
    
    while izq <= der:
        operaciones += 1
        medio = (izq + der) // 2
        codigo_medio = pedidos[medio].get('codigo', pedidos[medio].get('id', ''))
        
        if codigo_medio == id_pedido:
            encontrado = True
            pedido_encontrado = pedidos[medio]
            break
        elif codigo_medio < id_pedido:
            izq = medio + 1
        else:
            der = medio - 1
            
    fin = time.perf_counter()
    tiempo_ms = (fin - inicio) * 1000
    
    return {
        "encontrado": encontrado,
        "pedido": pedido_encontrado,
        "operaciones": operaciones,
        "tiempo_ms": tiempo_ms,
        "complejidad": "O(log n)",
        "tamanio_entrada": len(pedidos),
        "id_buscado": id_pedido,
        "mejor_caso": "1 operación (elemento en el medio)",
        "peor_caso": "log₂(n) operaciones"
    }
