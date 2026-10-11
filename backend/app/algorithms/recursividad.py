def procesar_productos_recursivamente(productos: list[str], indice: int = 0) -> dict:
    """Procesa una lista de productos utilizando recursividad."""
    resultados_locales = []
    llamadas_recursivas = [0]
    
    def recursar(idx: int):
        llamadas_recursivas[0] += 1
        # Caso base
        if idx >= len(productos):
            return
            
        # Caso recursivo
        resultados_locales.append({
            "paso": idx + 1,
            "producto": productos[idx],
            "indice": idx
        })
        recursar(idx + 1)
        
    recursar(indice)
    
    return {
        "productos": productos,
        "cantidad": len(productos),
        "llamadas_recursivas": llamadas_recursivas[0],
        "resultados": resultados_locales,
        "caso_base": "Cuando el índice alcanza el tamaño de la lista (índice >= n)",
        "caso_recursivo": "Procesar el producto actual y llamar con índice + 1"
    }
