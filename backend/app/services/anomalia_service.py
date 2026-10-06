from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
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
    now = datetime.utcnow()
    hoy = now.replace(hour=0, minute=0, second=0, microsecond=0)
    semana = hoy - timedelta(days=7)
    mes = hoy - timedelta(days=30)

    def count_desde(modelo, campo, fecha):
        return db.query(modelo).filter(campo >= fecha).count()

    total = db.query(Pedido).count()
    anoms = db.query(Anomalia).all()
    total_anom = len(anoms)
    pct = round(total_anom / total * 100, 2) if total else 0
    valor_sospechoso = 0.0
    for a in anoms:
        if a.pedido_id:
            p = db.query(Pedido).filter(Pedido.id == a.pedido_id).first()
            if p and p.valor:
                valor_sospechoso += float(p.valor)
    clientes_afectados = len({a.cliente_id for a in anoms if a.cliente_id})
    # Recurrentes: cliente con >= 2 anomalías (find/filter)
    conteo: dict[int, int] = {}
    for a in anoms:
        if a.cliente_id:
            conteo[a.cliente_id] = conteo.get(a.cliente_id, 0) + 1
    recurrentes = [k for k, v in conteo.items() if v >= 2]

    # Distribución por hora y método de pago
    por_hora = {str(h): 0 for h in range(24)}
    for a in anoms:
        if a.fecha_creacion:
            por_hora[str(a.fecha_creacion.hour)] += 1
    por_metodo: dict[str, int] = {}
    for p in db.query(Pedido).all():
        por_metodo[p.metodo_pago or "Otro"] = por_metodo.get(p.metodo_pago or "Otro", 0) + 1

    abiertas = sum(1 for a in anoms if a.estado_revision == "abierta")
    return {
        "pedidos": {
            "total": total,
            "hoy": count_desde(Pedido, Pedido.fecha_txn, hoy),
            "semana": count_desde(Pedido, Pedido.fecha_txn, semana),
            "mes": count_desde(Pedido, Pedido.fecha_txn, mes),
        },
        "anomalias": {
            "total": total_anom,
            "hoy": count_desde(Anomalia, Anomalia.fecha_creacion, hoy),
            "semana": count_desde(Anomalia, Anomalia.fecha_creacion, semana),
            "mes": count_desde(Anomalia, Anomalia.fecha_creacion, mes),
            "abiertas": abiertas,
            "revisadas": sum(1 for a in anoms if a.estado_revision == "revisada"),
            "descartadas": sum(1 for a in anoms if a.estado_revision == "descartada"),
            "porcentaje": pct,
        },
        "clientes_afectados": clientes_afectados,
        "clientes_recurrentes": recurrentes,
        "valor_sospechoso": valor_sospechoso,
        "promedio_por_cliente": round(total / len({p.cliente_id for p in db.query(Pedido).all()}) , 2) if total else 0,
        "por_hora": por_hora,
        "por_metodo_pago": por_metodo,
    }
