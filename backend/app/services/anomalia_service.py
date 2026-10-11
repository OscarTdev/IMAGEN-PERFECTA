"""Métricas agregadas del módulo de seguridad (dashboard del PDF Appresso → Imagen Perfecta).

Todo se mide en TIEMPO DE TRANSACCIÓN (fecha_txn): si el bot del profesor
repite historia, los cortes día/semana/mes y las horas siguen siendo ciertos.

Mapa de requisitos que satisface cada métrica:
  D1  Banda Hoy │ Esta semana │ Este mes (agregado)
  D2  Casos más recurrentes
  D3  Múltiples transacciones
  D4  Usuarios recurrentes
  D5  Total de transacciones (día/semana/mes)
  D6  Total de anomalías (día/semana/mes)
  D7  Porcentaje de transacciones con anomalías
  D8  Usuarios afectados
  D9  Valor total de transacciones sospechosas
  D10 Promedio de transacciones por usuario
  D11 Número de anomalías nuevas
  D12 Anomalías abiertas
  D13 Anomalías revisadas
  D14 Anomalías descartadas
  D15 Tendencias
  A1  Evolución temporal (horas con más anomalías, picos, periodos)
  A2  Anomalías por nivel
  A5  Métodos de pago
  A6  Distribución por hora (intensidad = anomalías × horas)
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.models.anomalia import Anomalia


def listar(db: Session, tipo: str | None = None, estado_revision: str | None = None):
    q = db.query(Anomalia).order_by(Anomalia.fecha_creacion.desc())
    if tipo:
        q = q.filter(Anomalia.tipo == tipo)
    if estado_revision:
        q = q.filter(Anomalia.estado_revision == estado_revision)
    return q.all()


def resumen_dashboard(db: Session) -> dict:
    """Información agregada que consume el dashboard del frontend (GET /api/dashboard)."""
    now = datetime.utcnow()
    hoy = now.replace(hour=0, minute=0, second=0, microsecond=0)
    semana = hoy - timedelta(days=7)
    mes = hoy - timedelta(days=30)

    # ── REQUISITO D5: Total de transacciones (día/semana/mes) ──
    # Fuente de verdad: pedidos originados por transacciones del profesor
    # (id_txn) — exactamente lo que lista GET /api/transacciones. Los 30
    # pedidos semilla del negocio NO contaminan las métricas de seguridad.
    txns = db.query(Pedido).filter(Pedido.id_txn.isnot(None)).all()
    total_txn = len(txns)
    txn_hoy = sum(1 for t in txns if t.fecha_txn and t.fecha_txn >= hoy)
    txn_semana = sum(1 for t in txns if t.fecha_txn and t.fecha_txn >= semana)
    txn_mes = sum(1 for t in txns if t.fecha_txn and t.fecha_txn >= mes)

    # ── REQUISITO D10: Promedio de transacciones por usuario ──
    # ── REQUISITO A5: Métodos de pago (distribución de las transacciones) ──
    usuarios: set[int] = set()
    por_metodo: dict[str, int] = {}
    for t in txns:
        if t.cliente_id:
            usuarios.add(t.cliente_id)
        clave = (t.metodo_pago or "Otro").strip() or "Otro"
        por_metodo[clave] = por_metodo.get(clave, 0) + 1
    promedio_por_usuario = round(total_txn / len(usuarios), 2) if usuarios else 0.0

    # ── REQUISITO D6: Total de anomalías (día/semana/mes) ──
    # El momento de una anomalía es el fecha_txn del pedido que la detonó
    # (no la hora en que el servidor la insertó), para que la replay de
    # historia del bot siga siendo cierta.
    anoms = db.query(Anomalia).all()
    total_anom = len(anoms)

    # ── REQUISITO D7: Porcentaje de transacciones con anomalías ──
    pct = round(total_anom / total_txn * 100, 2) if total_txn else 0

    pedido_ids = {a.pedido_id for a in anoms if a.pedido_id}
    pedidos = {p.id: p for p in db.query(Pedido).filter(Pedido.id.in_(pedido_ids)).all()} \
        if pedido_ids else {}

    def momento(a: Anomalia) -> datetime | None:
        p = pedidos.get(a.pedido_id) if a.pedido_id else None
        return (p.fecha_txn if p and p.fecha_txn else a.fecha_creacion)

    # ── REQUISITO D9: Valor total de transacciones sospechosas ──
    valor_sospechoso = 0.0
    for a in anoms:
        p = pedidos.get(a.pedido_id) if a.pedido_id else None
        if p and p.valor:
            valor_sospechoso += float(p.valor)

    momentos = [(a, momento(a)) for a in anoms]
    anom_hoy = sum(1 for _, m in momentos if m and m >= hoy)
    anom_semana = sum(1 for _, m in momentos if m and m >= semana)
    anom_mes = sum(1 for _, m in momentos if m and m >= mes)

    # ── REQUISITO D12: Anomalías abiertas ──
    abiertas = sum(1 for a in anoms if a.estado_revision == "abierta")
    # ── REQUISITO D13: Anomalías revisadas ──
    revisadas = sum(1 for a in anoms if a.estado_revision == "revisada")
    # ── REQUISITO D14: Anomalías descartadas ──
    descartadas = sum(1 for a in anoms if a.estado_revision == "descartada")
    # ── REQUISITO D11: Número de anomalías nuevas (detectadas hoy y sin revisar) ──
    nuevas = sum(1 for a, m in momentos
                 if a.estado_revision == "abierta" and m and m >= hoy)

    # ── REQUISITO D2: Casos más recurrentes (conteo por tipo de anomalía) ──
    # ── REQUISITO D3: Múltiples transacciones (tipo POSIBLE_FRAUDE, la ráfaga
    #    dentro de la ventana deslizante queda contada aquí) ──
    # ── REQUISITO A2: Anomalías por nivel ──
    por_tipo: dict[str, int] = {}
    por_nivel: dict[str, int] = {}
    for a in anoms:
        por_tipo[a.tipo] = por_tipo.get(a.tipo, 0) + 1
        por_nivel[a.nivel] = por_nivel.get(a.nivel, 0) + 1

    # ── REQUISITO D8: Usuarios afectados (clientes con al menos una anomalía) ──
    # ── REQUISITO D4: Usuarios recurrentes (≥ 2 anomalías, con detalle) ──
    conteo: dict[int, int] = {}
    for a in anoms:
        if a.cliente_id:
            conteo[a.cliente_id] = conteo.get(a.cliente_id, 0) + 1
    clientes_afectados = len(conteo)
    recurrentes_ids = sorted(k for k, v in conteo.items() if v >= 2)
    usuarios_recurrentes = []
    if recurrentes_ids:
        for c in db.query(Cliente).filter(Cliente.id.in_(recurrentes_ids)).all():
            usuarios_recurrentes.append(
                {"cliente_id": c.id, "email": c.email, "anomalias": conteo[c.id]}
            )
        usuarios_recurrentes.sort(key=lambda u: u["anomalias"], reverse=True)

    # ── REQUISITO A6: Distribución por hora (intensidad = anomalías × hora 0-23) ──
    # ── REQUISITO A1: Horas con más anomalías (base del heatmap y la hora pico) ──
    por_hora = {str(h): 0 for h in range(24)}
    for _, m in momentos:
        if m:
            por_hora[str(m.hour)] += 1

    # ── REQUISITO D15: Tendencias (serie de 14 días) ──
    # ── REQUISITO A1: Evolución temporal (picos repentinos y periodos de actividad) ──
    txn_por_dia: dict = {}
    for t in txns:
        if t.fecha_txn:
            txn_por_dia[t.fecha_txn.date()] = txn_por_dia.get(t.fecha_txn.date(), 0) + 1
    anom_por_dia: dict = {}
    for _, m in momentos:
        if m:
            anom_por_dia[m.date()] = anom_por_dia.get(m.date(), 0) + 1
    serie_diaria = []
    for i in range(13, -1, -1):
        dia = (hoy - timedelta(days=i)).date()
        serie_diaria.append({
            "fecha": dia.isoformat(),
            "transacciones": txn_por_dia.get(dia, 0),
            "anomalias": anom_por_dia.get(dia, 0),
        })

    return {
        # Pedidos del negocio (operación), separados de las transacciones
        "pedidos": {"total": db.query(Pedido).count()},
        # REQUISITO D1 / D5: banda Hoy │ Esta semana │ Este mes de transacciones
        "transacciones": {"total": total_txn, "hoy": txn_hoy,
                          "semana": txn_semana, "mes": txn_mes},
        # REQUISITO D1 / D6: banda Hoy │ Esta semana │ Este mes de anomalías
        "anomalias": {
            "total": total_anom, "hoy": anom_hoy, "semana": anom_semana,
            "mes": anom_mes, "nuevas": nuevas, "abiertas": abiertas,
            "revisadas": revisadas, "descartadas": descartadas,
            "porcentaje": pct, "por_tipo": por_tipo, "por_nivel": por_nivel,
        },
        "clientes_afectados": clientes_afectados,
        "clientes_recurrentes": recurrentes_ids,
        "usuarios_recurrentes": usuarios_recurrentes,
        "valor_sospechoso": valor_sospechoso,
        "promedio_por_usuario": promedio_por_usuario,
        "por_hora": por_hora,
        "por_metodo_pago": por_metodo,
        "serie_diaria": serie_diaria,
    }
