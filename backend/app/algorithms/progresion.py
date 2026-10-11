import math

def calcular_progresion(a1: int = 2, d: int = 2, objetivos: list[int] = None) -> dict:
    """Calcula una progresión aritmética para un modelo de metas."""
    if objetivos is None:
        objetivos = [42, 72, 120]
        
    max_objetivo = max(objetivos) if objetivos else 0
    
    secuencia = []
    n = 1
    an = a1
    
    while an <= max_objetivo or n <= 1:
        an = a1 + (n - 1) * d
        secuencia.append(an)
        n += 1
        
    resultados_objetivos = []
    for obj in objetivos:
        n_estimado = max(1, math.ceil((obj - a1) / d) + 1)
        termino_alcanzado = a1 + (n_estimado - 1) * d
        resultados_objetivos.append({
            "valor": obj,
            "semana": n_estimado,
            "termino_alcanzado": termino_alcanzado
        })
        
    return {
        "primer_termino": a1,
        "diferencia": d,
        "formula": "aₙ = a₁ + (n-1)d",
        "objetivos": resultados_objetivos,
        "secuencia": secuencia
    }
