"""Sumatoria de Gauss, progresión aritmética, recursividad y regresión lineal.

PDF ProgramacionAvanzada: pag. 23-27 (progresiones y sumatorias),
pag. 28-29 (recursividad) y caso 3-4 (fidelización 42/72/120 y regresión).
"""


def sumatoria_gauss(n: int) -> dict:
    """S = n(n+1)/2 vs conteo iterativo de operaciones."""
    formula = n * (n + 1) // 2
    iterativo = 0
    for i in range(1, n + 1):
        iterativo += i
    return {
        "n": n,
        "sumatoria_formula": formula,
        "sumatoria_iterativa": iterativo,
        "coinciden": formula == iterativo,
        "formula": "S = n(n+1)/2",
        "explicacion": (
            "Un bucle anidado (i=1..n, j=1..i) realiza S = 1+2+...+n = n(n+1)/2 "
            "operaciones: por eso O(n²) ≈ n²/2 pasos."
        ),
    }


def progresion_aritmetica(a1: int, d: int, objetivos: list[int]) -> dict:
    """a_n = a1 + (n-1)d — semanas en que el cliente alcanza cada meta."""
    # Semana en la que a_n >= objetivo (progresión creciente)
    resultado = []
    max_sem = 200
    for objetivo in objetivos:
        semana = None
        valor_en_semana = None
        if d > 0 and a1 > 0:
            # a_n = a1 + (n-1)d >= objetivo  ->  n >= 1 + (objetivo - a1)/d
            n = max(1, 1 + (objetivo - a1) / d)
            n = math_ceil(n)
            if n <= max_sem:
                semana = n
                valor_en_semana = a1 + (n - 1) * d
        resultado.append({
            "objetivo": objetivo,
            "semana": semana,
            "valor_en_semana": valor_en_semana,
            "alcanza": semana is not None,
        })
    terminos = [a1 + (i) * d for i in range(10)]
    return {
        "primer_termino": a1,
        "diferencia": d,
        "formula": "aₙ = a₁ + (n - 1)d",
        "objetivos": resultado,
        "terminos": terminos,
        "explicacion": (
            "Cliente fotógrafo que empieza con a1 productos y suma d cada semana: "
            "la fórmula del término n dice directamente la semana en que alcanza "
            "42, 72 y 120 productos (descuentos por fidelización)."
        ),
    }


def math_ceil(x: float) -> int:
    import math
    return math.ceil(x)


def procesar_recursivo(productos: list[str]) -> dict:
    """Recorrido recursivo con caso base índice >= n (PDF pag. 28)."""
    llamadas = {"total": 0}
    resultados: list[dict] = []

    def _recorrer(idx: int):
        llamadas["total"] += 1
        if idx >= len(productos):  # CASO BASE
            return None
        # CASO RECURSIVO
        resultados.append({"indice": idx, "producto": productos[idx]})
        return _recorrer(idx + 1)

    _recorrer(0)
    return {
        "productos": productos,
        "cantidad": len(productos),
        "llamadas_recursivas": llamadas["total"],
        "resultados": resultados,
        "caso_base": "índice >= longitud de la lista",
        "explicacion": (
            "Cada llamada procesa un producto y se llama a sí misma con idx+1 "
            "hasta llegar al caso base: n+1 llamadas para n productos."
        ),
    }


def regresion_lineal(datos: list[dict] | None, dias_prediccion: list[int]) -> dict:
    """Mínimos cuadrados y = mx + b (PDF caso 4: predecir ventas 2, 5, 7 días)."""
    if not datos:
        # Serie por defecto: pedidos de los últimos 7 días del negocio
        datos = [
            {"dia": 1, "pedidos": 12}, {"dia": 2, "pedidos": 15},
            {"dia": 3, "pedidos": 14}, {"dia": 4, "pedidos": 19},
            {"dia": 5, "pedidos": 22}, {"dia": 6, "pedidos": 21},
            {"dia": 7, "pedidos": 26},
        ]
    xs = [float(d["dia"]) for d in datos]
    ys = [float(d["pedidos"]) for d in datos]
    n = len(xs)
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(x * y for x, y in zip(xs, ys))
    sum_x2 = sum(x * x for x in xs)
    denominador = n * sum_x2 - sum_x ** 2
    if denominador == 0:
        m = 0.0
        b = sum_y / n if n else 0.0
    else:
        m = (n * sum_xy - sum_x * sum_y) / denominador
        b = (sum_y - m * sum_x) / n
    predicciones = []
    for dia in dias_prediccion:
        valor = m * dia + b
        predicciones.append({
            "dia": dia,
            "pedidos_estimados": round(valor, 2),
        })
    return {
        "pendiente": round(m, 4),
        "intercepto": round(b, 4),
        "ecuacion": f"y = {round(m, 4)}x + {round(b, 4)}",
        "n_datos": n,
        "datos": datos,
        "dias_prediccion": dias_prediccion,
        "predicciones": predicciones,
        "nota": (
            "Regresión lineal por mínimos cuadrados sobre los pedidos diarios "
            "de Imagen Perfecta para proyectar la tendencia de ventas."
        ),
    }
