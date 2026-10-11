from app.algorithms.busqueda_lineal import buscar_pedido_lineal
from app.algorithms.busqueda_binaria import buscar_pedido_binario
from app.algorithms.complejidad import generar_pedidos_prueba

def analizar_mejor_peor_caso(n: int = 1000) -> dict:
    """Analiza los tiempos y operaciones del mejor y peor caso de las búsquedas."""
    pedidos = generar_pedidos_prueba(n)
    
    # Búsqueda Lineal
    id_lineal_mejor = pedidos[0]["codigo"]  # Primer elemento
    id_lineal_peor = "IP-INEXISTENTE"     # Elemento no existente
    
    res_lineal_mejor = buscar_pedido_lineal(pedidos, id_lineal_mejor)
    res_lineal_peor = buscar_pedido_lineal(pedidos, id_lineal_peor)
    
    # Búsqueda Binaria
    medio = len(pedidos) // 2
    id_binaria_mejor = pedidos[medio]["codigo"]  # Elemento en el medio
    id_binaria_peor = "IP-INEXISTENTE"           # Elemento no existente
    
    res_binaria_mejor = buscar_pedido_binario(pedidos, id_binaria_mejor)
    res_binaria_peor = buscar_pedido_binario(pedidos, id_binaria_peor)
    
    return {
        "n": n,
        "lineal": {
            "mejor": {
                "operaciones": res_lineal_mejor["operaciones"],
                "tiempo_ms": res_lineal_mejor["tiempo_ms"]
            },
            "peor": {
                "operaciones": res_lineal_peor["operaciones"],
                "tiempo_ms": res_lineal_peor["tiempo_ms"]
            }
        },
        "binaria": {
            "mejor": {
                "operaciones": res_binaria_mejor["operaciones"],
                "tiempo_ms": res_binaria_mejor["tiempo_ms"]
            },
            "peor": {
                "operaciones": res_binaria_peor["operaciones"],
                "tiempo_ms": res_binaria_peor["tiempo_ms"]
            }
        }
    }
