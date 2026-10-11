def calcular_regresion(datos: list[dict] | None = None, dias_prediccion: list[int] = None) -> dict:
    """Implementa regresión lineal simple manualmente mediante mínimos cuadrados."""
    if datos is None:
        datos = [
            {"dia": 1, "pedidos": 10},
            {"dia": 2, "pedidos": 13},
            {"dia": 3, "pedidos": 15},
            {"dia": 4, "pedidos": 18},
            {"dia": 5, "pedidos": 21}
        ]
        
    if dias_prediccion is None:
        dias_prediccion = [2, 5, 7]
        
    n = len(datos)
    sum_x = sum(d["dia"] for d in datos)
    sum_y = sum(d["pedidos"] for d in datos)
    sum_xy = sum(d["dia"] * d["pedidos"] for d in datos)
    sum_x_squared = sum(d["dia"] ** 2 for d in datos)
    
    denominador = (n * sum_x_squared - sum_x ** 2)
    if denominador == 0:
        m = 0.0
        b = sum_y / n if n != 0 else 0.0
    else:
        m = (n * sum_xy - sum_x * sum_y) / denominador
        b = (sum_y - m * sum_x) / n
        
    predicciones = []
    for dia in dias_prediccion:
        estimacion = m * dia + b
        predicciones.append({
            "dia": dia,
            "estimacion": estimacion
        })
        
    return {
        "datos_historicos": datos,
        "pendiente": m,
        "intercepto": b,
        "ecuacion": f"y = {m:.2f}x + {b:.2f}",
        "predicciones": predicciones,
        "nota": "Estimación matemática basada en datos de prueba, no predicción real de ventas."
    }
