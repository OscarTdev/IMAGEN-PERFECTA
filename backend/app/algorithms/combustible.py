"""Cálculo de combustible para entregas de Imagen Perfecta.

Litros = Distancia (km) / Rendimiento (km/L)
Costo  = Litros × Precio por Litro (COP)
"""


def calcular_combustible(
    distancia_km: float,
    rendimiento_km_por_litro: float = 12.0,
    precio_por_litro: float = 14500.0,
) -> dict:
    """Estima litros y costo (COP) para una distancia de entrega."""
    if rendimiento_km_por_litro <= 0:
        raise ValueError("El rendimiento debe ser mayor que 0.")

    litros = distancia_km / rendimiento_km_por_litro
    costo = litros * precio_por_litro
    return {
        "distancia_km": distancia_km,
        "rendimiento_km_por_litro": rendimiento_km_por_litro,
        "litros_estimados": round(litros, 2),
        "precio_por_litro": precio_por_litro,
        "costo_estimado": round(costo),
        "nota": (
            f"Para {distancia_km} km con un rendimiento de "
            f"{rendimiento_km_por_litro} km/L se estiman {round(litros, 2)} L "
            f"a ${precio_por_litro:,.0f} COP por litro."
        ),
    }
