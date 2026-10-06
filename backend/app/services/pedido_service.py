"""Lógica pedidos + conceptos PDF: descomposición, hash, ventana, divide y vencerás."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.pedido import Pedido
from app.models.anomalia import Anomalia
from app.schemas.pedido import PedidoCreate
from app.core import config as cfg
from app.core.hash_utils import generar_hash, verificar_hash
from app.core import detector
from app.core.logger import log_evento, log_error, dividir_seguro

# Índice en memoria por código (PDF: diccionarios para búsqueda eficiente)
_indice_codigo: dict[str, int] = {}


def payload_hash(p: Pedido) -> dict:
    # Solo campos que el cliente conoce ANTES de crear (sin codigo autogenerado).
    # Así el profe puede calcular el HMAC desde fuera y el servidor lo verifica.
    return {
        "cliente_id": p.cliente_id, "productos": p.productos,
        "cantidad_total": p.cantidad_total, "valor": p.valor,
        "metodo_pago": p.metodo_pago, "fecha_txn": p.fecha_txn.isoformat() if p.fecha_txn else "",
    }


def payload_hash_legacy(p: Pedido) -> dict:
    d = payload_hash(p)
    d["codigo"] = p.codigo
    return d


def get_next_codigo(db: Session) -> str:
    last_pedido = db.query(Pedido).order_by(Pedido.id.desc()).first()
    if not last_pedido:
        return "IP-0001"
    last_number = int(last_pedido.codigo.split("-")[1])
    return f"IP-{last_number + 1:04d}"


def get_pedidos(db: Session) -> List[Pedido]:
    return db.query(Pedido).order_by(Pedido.fecha_txn.desc()).all()


def get_pedido(db: Session, id: int) -> Optional[Pedido]:
    return db.query(Pedido).filter(Pedido.id == id).first()


def get_pedido_by_codigo(db: Session, codigo: str) -> Optional[Pedido]:
    # filter() eficiente + caché dict (PDF: filter/includes/diccionarios)
    if codigo in _indice_codigo:
        return get_pedido(db, _indice_codigo[codigo])
    p = db.query(Pedido).filter(Pedido.codigo == codigo).first()
    if p:
        _indice_codigo[codigo] = p.id
    return p


def buscar_por_producto(db: Session, texto: str) -> List[Pedido]:
    """Búsqueda y filtrado eficiente: includes() equivalente en Python/SQL."""
    todos = get_pedidos(db)
    t = texto.lower()
    return [p for p in todos if t in (p.productos or "").lower()]


def calcular_total_seguro(items: list) -> float:
    """Descomposición PDF: entradas->proceso->salida con validación robusta."""
    total = 0.0
    for it in items:
        try:
            valor = float(it.get("valor", 0))
            cantidad = int(it.get("cantidad", 0))
            if valor <= 0:
                log_error(f"Valor inválido {it}", donde="calcular_total")
                continue
            if cantidad <= 0:
                log_error(f"Cantidad inválida {it}", donde="calcular_total")
                continue
            total += valor * cantidad
        except (ValueError, TypeError):
            log_error(f"Datos inválidos {it}", donde="calcular_total")
    return total


def pedido_mayor_valor_recursivo(pedidos: list) -> Optional[Pedido]:
    """Divide y vencerás recursivo: encontrar pedido de mayor valor."""
    if not pedidos:
        return None
    if len(pedidos) == 1:
        return pedidos[0]
    mid = len(pedidos) // 2
    left = pedido_mayor_valor_recursivo(pedidos[:mid])
    right = pedido_mayor_valor_recursivo(pedidos[mid:])
    lv = left.valor if left else -1
    rv = right.valor if right else -1
    return left if lv >= rv else right


def _registrar_anomalia(db: Session, pedido: Pedido, tipo: str, cantidad: int,
                        ventana: int, detalle: str, nivel: str = "alta") -> Anomalia:
    a = Anomalia(pedido_id=pedido.id, cliente_id=pedido.cliente_id, tipo=tipo,
                 nivel=nivel, cantidad_transacciones=cantidad,
                 ventana_segundos=ventana, detalle=detalle)
    db.add(a)
    db.commit()
    db.refresh(a)
    log_evento(f"Anomalía {tipo} pedido={pedido.codigo} cant={cantidad}", donde="detector")
    return a


def create_pedido(db: Session, data: PedidoCreate) -> tuple[Pedido, str]:
    """POST: valida hash, guarda, ordena cronológicamente y aplica ventana.

    Retorna (pedido, estado: NORMAL | POSIBLE_FRAUDE | HASH_INVALIDO).
    """
    fecha_txn = data.fecha_txn or datetime.utcnow()
    codigo = get_next_codigo(db)
    db_pedido = Pedido(
        codigo=codigo, cliente_id=data.cliente_id, productos=data.productos,
        cantidad_total=data.cantidad_total, estado="Solicitado",
        prioridad=data.prioridad, direccion_entrega=data.direccion_entrega,
        valor=data.valor or 0, metodo_pago=data.metodo_pago or "Efectivo",
        ip=data.ip, fecha_txn=fecha_txn, fecha=datetime.utcnow(),
    )
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    _indice_codigo[codigo] = db_pedido.id

    # 1. Validar hash si el cliente lo envió (PDF: calcular y comparar)
    datos = payload_hash(db_pedido)
    estado = "NORMAL"
    if data.hash:
        ok = verificar_hash(datos, cfg.LLAVE_SECRETA, data.hash)
        if not ok:
            # Compatibilidad: seeds viejos firmados con codigo incluido
            ok = verificar_hash(payload_hash_legacy(db_pedido), cfg.LLAVE_SECRETA, data.hash)
        if not ok:
            _registrar_anomalia(db, db_pedido, "HASH_INVALIDO", 1, 0,
                                "Hash recibido no coincide", nivel="critica")
            estado = "HASH_INVALIDO"
    # Si no se envió, se genera y guarda (autofirma servidor)
    db_pedido.hash = generar_hash(datos, cfg.LLAVE_SECRETA)
    db.commit()
    db.refresh(db_pedido)

    # 2. Ventana deslizante por cliente según turno (10/6/3 s)
    historial = [p.fecha_txn for p in db.query(Pedido).filter(
        Pedido.cliente_id == data.cliente_id, Pedido.id != db_pedido.id).order_by(Pedido.fecha_txn.asc()).all()]
    turno = cfg.turno_de_fecha(fecha_txn)
    ventana = cfg.ventana_por_turno(fecha_txn)
    res = detector.analizar(data.cliente_id, fecha_txn, ventana, historial)
    if res["cantidad_en_ventana"] >= cfg.UMBRAL_TRANSACCIONES and estado == "NORMAL":
        _registrar_anomalia(db, db_pedido, "POSIBLE_FRAUDE", res["cantidad_en_ventana"],
                            ventana, f"{res['cantidad_en_ventana']} pedidos en {ventana}s turno={turno}")
        estado = "POSIBLE_FRAUDE"

    log_evento(f"Pedido {codigo} estado={estado} turno={turno} ventana={ventana}s", donde="pedido_service.create")
    return db_pedido, estado


def update_estado(db: Session, id: int, estado: str) -> Optional[Pedido]:
    p = get_pedido(db, id)
    if not p:
        return None
    p.estado = estado
    db.commit()
    db.refresh(p)
    return p


def put_pedido(db: Session, id: int, data) -> Optional[Pedido]:
    """PUT: reemplazo completo + re-hash."""
    p = get_pedido(db, id)
    if not p:
        return None
    for k in ("cliente_id", "productos", "cantidad_total", "prioridad",
              "direccion_entrega", "valor", "metodo_pago", "ip"):
        v = getattr(data, k, None)
        if v is not None:
            setattr(p, k, v)
    p.hash = generar_hash(payload_hash(p), cfg.LLAVE_SECRETA)
    db.commit()
    db.refresh(p)
    return p


def patch_pedido(db: Session, id: int, data) -> Optional[Pedido]:
    """PATCH: solo campos enviados."""
    p = get_pedido(db, id)
    if not p:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        if v is not None and hasattr(p, k):
            setattr(p, k, v)
    p.hash = generar_hash(payload_hash(p), cfg.LLAVE_SECRETA)
    db.commit()
    db.refresh(p)
    return p


def delete_pedido(db: Session, id: int) -> bool:
    p = get_pedido(db, id)
    if not p:
        return False
    _indice_codigo.pop(p.codigo, None)
    db.delete(p)
    db.commit()
    log_evento(f"Pedido eliminado id={id}", donde="pedido_service.delete")
    return True


def promedio_por_cliente(db: Session) -> float | None:
    """Ejemplo logs PDF: evita división por cero."""
    total = db.query(Pedido).count()
    clientes = db.query(Pedido.cliente_id).distinct().count()
    return dividir_seguro(float(total), float(clientes))


def create_lote(db: Session, items: list) -> dict:
    """Lote de hasta N transacciones (ej. 500 del profesor).

    Lógica interna: orden cronológico, validación robusta por item,
    hash HMAC por item, ventana deslizante por cliente en memoria
    (sale uno/entra uno), límites por turno. Un solo commit.
    """
    import time
    from collections import deque
    t0 = time.perf_counter()

    # Orden cronológico (PDF)
    def _fecha(x):
        return x.fecha_txn or datetime.utcnow()
    ordenados = sorted(items, key=_fecha)

    # Clientes existentes (una sola consulta)
    ids = {x.cliente_id for x in ordenados}
    existentes = {c.id for c in db.query(__import__("app.models.cliente", fromlist=["Cliente"]).Cliente).filter(
        __import__("app.models.cliente", fromlist=["Cliente"]).Cliente.id.in_(ids)).all()} if ids else set()

    # Historial previo por cliente (una consulta por lote)
    from app.models.cliente import Cliente  # noqa
    ventanas: dict[int, deque] = {}
    for cid in ids:
        prev = [r[0] for r in db.query(Pedido.fecha_txn).filter(Pedido.cliente_id == cid).all()]
        ventanas[cid] = deque(sorted([f for f in prev if f]))

    # Contadores de turno del día (base + progresivo)
    base_turno = {"manana": 0, "tarde": 0, "noche": 0}
    for (f,) in db.query(Pedido.fecha_txn).all():
        try:
            base_turno[cfg.turno_de_hora(f.hour)] += 1
        except Exception:
            pass

    # Siguiente código (un solo cálculo)
    last = db.query(Pedido).order_by(Pedido.id.desc()).first()
    seq = int(last.codigo.split("-")[1]) + 1 if last else 1

    detalle = []
    anomalias_pend: list[Anomalia] = []
    cont = {"NORMAL": 0, "POSIBLE_FRAUDE": 0, "HASH_INVALIDO": 0, "RECHAZADO": 0}

    for idx, data in enumerate(ordenados):
        fecha_txn = data.fecha_txn or datetime.utcnow()
        # Validación interna robusta (descomposición PDF)
        try:
            valor = float(data.valor or 0)
            cantidad = int(data.cantidad_total)
            if valor < 0 or cantidad <= 0:
                cont["RECHAZADO"] += 1
                detalle.append({"indice": idx, "deteccion": "RECHAZADO", "motivo": "valor/cantidad inválidos"})
                log_error(f"Lote item {idx} valor/cantidad inválidos", donde="create_lote")
                continue
        except (ValueError, TypeError):
            cont["RECHAZADO"] += 1
            detalle.append({"indice": idx, "deteccion": "RECHAZADO", "motivo": "tipos inválidos"})
            continue
        if data.cliente_id not in existentes:
            cont["RECHAZADO"] += 1
            detalle.append({"indice": idx, "deteccion": "RECHAZADO", "motivo": "cliente no existe"})
            continue

        codigo = f"IP-{seq:04d}"
        seq += 1
        p = Pedido(
            codigo=codigo, cliente_id=data.cliente_id, productos=data.productos,
            cantidad_total=cantidad, estado="Solicitado",
            prioridad=data.prioridad, direccion_entrega=data.direccion_entrega,
            valor=valor, metodo_pago=data.metodo_pago or "Efectivo",
            ip=data.ip, fecha_txn=fecha_txn, fecha=datetime.utcnow(),
        )
        db.add(p)
        db.flush()  # id sin commit (rápido para 500)
        _indice_codigo[codigo] = p.id

        datos = payload_hash(p)
        estado = "NORMAL"
        if data.hash:
            ok = verificar_hash(datos, cfg.LLAVE_SECRETA, data.hash) or \
                 verificar_hash(payload_hash_legacy(p), cfg.LLAVE_SECRETA, data.hash)
            if not ok:
                estado = "HASH_INVALIDO"
        p.hash = generar_hash(datos, cfg.LLAVE_SECRETA)

        # Ventana en memoria por cliente según turno (10/6/3 s)
        turno = cfg.turno_de_fecha(fecha_txn)
        ventana = cfg.ventana_por_turno(fecha_txn)
        dq = ventanas[data.cliente_id]
        dq.append(fecha_txn)
        limite = fecha_txn - __import__("datetime").timedelta(seconds=ventana)
        while dq and dq[0] < limite:
            dq.popleft()
        cant = len(dq)
        if cant >= cfg.UMBRAL_TRANSACCIONES and estado == "NORMAL":
            estado = "POSIBLE_FRAUDE"

        if estado in ("POSIBLE_FRAUDE", "HASH_INVALIDO"):
            anomalias_pend.append(Anomalia(
                pedido_id=p.id, cliente_id=p.cliente_id, tipo=estado,
                nivel="critica" if estado == "HASH_INVALIDO" else "alta",
                cantidad_transacciones=cant, ventana_segundos=ventana,
                detalle=f"Lote idx={idx} {cant}tx/{ventana}s turno={turno}"))

        cont[estado] = cont.get(estado, 0) + 1
        detalle.append({"indice": idx, "codigo": codigo, "pedido_id": p.id,
                        "cliente_id": p.cliente_id, "deteccion": estado,
                        "en_ventana": cant})

    for a in anomalias_pend:
        db.add(a)
    db.commit()
    # Sincroniza memoria global del detector con lo procesado
    for cid, dq in ventanas.items():
        detector._ventanas[cid] = deque(dq)

    ms = round((time.perf_counter() - t0) * 1000, 2)
    log_evento(f"Lote procesado total={len(ordenados)} normales={cont.get('NORMAL',0)} "
               f"fraude={cont.get('POSIBLE_FRAUDE',0)} hash_inv={cont.get('HASH_INVALIDO',0)} "
               f"en {ms}ms", donde="create_lote")
    return {"total": len(ordenados), "resumen": cont, "tiempo_ms": ms,
            "anomalias_creadas": len(anomalias_pend), "detalle": detalle}
