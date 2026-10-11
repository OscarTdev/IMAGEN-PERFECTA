# GuÃ­a de prueba â€” Sistema de Transacciones Imagen Perfecta

## Lo Ãºnico que necesita el profesor

**1. La URL:**
```
https://1eae-2803-1800-401e-828d-70b8-2c8-ccdd-29c.ngrok-free.app/api/transacciones
```

**2. EL hash (credencial):**
```
d94fa63f732e8d6b2dc28d408949d19f13b7568335969879d6bbde3777178756
```

Con eso funciona todo. No se necesita llave privada ni cÃ¡lculos: **el mismo hash va en el campo `"hash"` de CADA transacciÃ³n**, con los datos que el bot quiera enviar.

> âš ï¸ La URL del tÃºnel cambia si se reinicia. El hash se mantiene siempre.

## 1. Estructura de cada transacciÃ³n

**Method:** `POST` Â· **Headers:** `Content-Type: application/json`

```json
{
  "idTxn": 80001,
  "user": "profe@udea.edu.co",
  "date": "2026-10-05T14:30:01",
  "value": 75000,
  "paymentMethod": "Tarjeta",
  "hash": "d94fa63f732e8d6b2dc28d408949d19f13b7568335969879d6bbde3777178756"
}
```

Los campos `idTxn`, `user`, `date`, `value` y `paymentMethod` son **libres** â€”
el bot envÃ­a los datos que quiera. El `hash` es siempre el entregado.

**Respuesta (200):**
```json
{
  "idTxn": 80001,
  "codigo": "IP-0035",
  "pedido_id": 35,
  "user": "profe@udea.edu.co",
  "deteccion": "NORMAL",
  "hash_valido": true
}
```

## 2. Reglas que aplica el sistema

| Regla | Comportamiento |
|---|---|
| Hash entregado presente | **Aceptada** (cualquier dato) â€” se evalÃºa por ventanas |
| Hash distinto al entregado | **Rechazada** (`400 HASH_INVALIDO`) |
| idTxn repetido | **Rechazada** (`400 RECHAZADO_DUPLICADO`) |
| 3+ tx del mismo usuario dentro de la ventana de su turno | `POSIBLE_FRAUDE` (anomalÃ­a registrada) |
| Ventana por turno (configurable) | MaÃ±ana (05:00â€“12:00) = 10 s Â· Tarde (12:00â€“20:00) = 6 s Â· Noche (20:00â€“05:00) = 3 s |

**Ejemplo del PDF comprobado:** tres transacciones de `b@b.com` a 1 segundo
de distancia â†’ las dos primeras `NORMAL`, la tercera `POSIBLE_FRAUDE`.
Transacciones separadas mÃ¡s que la ventana â†’ todas `NORMAL`.
Cada usuario tiene su propia ventana (no se mezclan).

## 3. Lote (hasta 1000 transacciones)

**URL:** `https://1eae-2803-1800-401e-828d-70b8-2c8-ccdd-29c.ngrok-free.app/api/transacciones/lote`
**Method:** `POST` Â· Body: **arreglo JSON** de transacciones (cada una con el hash entregado).

```json
[
  { "idTxn": 90001, "user": "b@b.com", "date": "2026-10-05T10:00:01", "value": 50000, "paymentMethod": "Tarjeta", "hash": "d94fa63f732e8d6b2dc28d408949d19f13b7568335969879d6bbde3777178756" },
  { "idTxn": 90002, "user": "b@b.com", "date": "2026-10-05T10:00:02", "value": 30000, "paymentMethod": "Tarjeta", "hash": "d94fa63f732e8d6b2dc28d408949d19f13b7568335969879d6bbde3777178756" },
  { "idTxn": 90003, "user": "b@b.com", "date": "2026-10-05T10:00:03", "value": 20000, "paymentMethod": "Tarjeta", "hash": "d94fa63f732e8d6b2dc28d408949d19f13b7568335969879d6bbde3777178756" }
]
```

**Respuesta (resumen):**
```json
{
  "resumen": { "TOTAL": 3, "NORMAL": 2, "POSIBLE_FRAUDE": 1,
               "RECHAZADO": 0, "RECHAZADO_DUPLICADO": 0, "RECHAZADO_HASH_INVALIDO": 0 },
  "detalle": [ { "idTxn": 90001, "deteccion": "NORMAL" },
               { "idTxn": 90002, "deteccion": "NORMAL" },
               { "idTxn": 90003, "deteccion": "POSIBLE_FRAUDE" } ]
}
```

El lote se procesa **ordenado cronolÃ³gicamente** y cada usuario mantiene
**su propia ventana**.

## 4. Consultar resultados

- **Transacciones recibidas:** `GET /api/transacciones` (Ãºltimas 100)
- **AnomalÃ­as:** `GET /api/anomalias` â€” con tipo, nivel, ventana y transacciones contadas
- **EstadÃ­sticas:** `GET /api/dashboard` â€” totales dÃ­a/semana/mes, valor sospechoso, usuarios recurrentes
- **ConfiguraciÃ³n de ventanas:** `GET /api/config` Â· `PUT /api/config` (ajusta 10/6/3 y el umbral)
- **DocumentaciÃ³n interactiva:** `https://1eae-2803-1800-401e-828d-70b8-2c8-ccdd-29c.ngrok-free.app/docs`
