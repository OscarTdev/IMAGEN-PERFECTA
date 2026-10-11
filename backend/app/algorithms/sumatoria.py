def calcular_sumatoria(n: int) -> dict:
    """Calcula la sumatoria de Gauss de forma iterativa y con fórmula."""
    sumatoria_formula = (n * (n + 1)) // 2
    
    sumatoria_iterativa = 0
    operaciones_iterativas = 0
    for i in range(1, n + 1):
        sumatoria_iterativa += i
        operaciones_iterativas += 1
        
    return {
        "n": n,
        "sumatoria_formula": sumatoria_formula,
        "sumatoria_iterativa": sumatoria_iterativa,
        "operaciones_iterativas": operaciones_iterativas,
        "formula": "S = n(n+1)/2",
        "relacion": "La sumatoria 1+2+...+n = n(n+1)/2 explica por qué un algoritmo con dos ciclos anidados realiza aproximadamente n²/2 operaciones, confirmando su complejidad O(n²)"
    }
