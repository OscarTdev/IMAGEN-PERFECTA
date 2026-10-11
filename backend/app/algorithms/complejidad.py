from app.algorithms.busqueda_lineal import buscar_pedido_lineal
from app.algorithms.busqueda_binaria import buscar_pedido_binario
from app.algorithms.cuadratico import comparar_pedidos

def generar_pedidos_prueba(n: int) -> list[dict]:
    """Genera n pedidos de prueba con códigos secuenciales."""
    return [
        {
            "id": f"id-{i}",
            "codigo": f"IP-{i:04d}",
            "estado": "pendiente" if i % 2 == 0 else "completado",
            "prioridad": "alta" if i % 3 == 0 else "normal"
        }
        for i in range(1, n + 1)
    ]

def ejecutar_pruebas_complejidad(tamanios: list[int] = None) -> dict:
    """Ejecuta pruebas de complejidad para varios tamaños de entrada."""
    if tamanios is None:
        tamanios = [10, 100, 1000, 10000, 100000]
        
    resultados = []
    
    for n in tamanios:
        pedidos = generar_pedidos_prueba(n)
        # Buscar el último elemento asegura el peor caso para la búsqueda lineal y cerca del peor para binaria
        id_buscado = f"IP-{n:04d}"
        
        # Búsqueda Lineal
        res_lineal = buscar_pedido_lineal(pedidos, id_buscado)
        
        # Búsqueda Binaria
        res_binaria = buscar_pedido_binario(pedidos, id_buscado)
        
        # Algoritmo Cuadrático (Omitir si n >= 10000 para evitar timeout)
        if n >= 10000:
            res_cuad = {
                "operaciones": "omitido por tiempo",
                "tiempo_ms": "omitido por tiempo"
            }
        else:
            res_cuadratico = comparar_pedidos(pedidos)
            res_cuad = {
                "operaciones": res_cuadratico["operaciones"],
                "tiempo_ms": res_cuadratico["tiempo_ms"]
            }
            
        resultados.append({
            "n": n,
            "busqueda_lineal": {
                "operaciones": res_lineal["operaciones"],
                "tiempo_ms": res_lineal["tiempo_ms"]
            },
            "busqueda_binaria": {
                "operaciones": res_binaria["operaciones"],
                "tiempo_ms": res_binaria["tiempo_ms"]
            },
            "cuadratico": res_cuad
        })
        
    return {"resultados": resultados}
