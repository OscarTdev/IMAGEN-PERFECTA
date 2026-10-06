"""Ingesta de transacciones en formato EXACTO del profesor (PDF Técnicas pag. 40-41).

Flujo: recibir -> verificar hash -> identificar usuario/cliente -> registrar
transacción + pedido IP-XXXX -> ventana deslizante por turno -> anomalías.
"""
import hmac
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.models.anomalia import Anomalia
from app.models.models import Usuario, Transaccion
from app.core import config as cfg
from app.core.hash_utils import generar_hash, verificar_hash
from app.core import detector
from app.core.logger import log_evento, log_error
from app.services import pedido_service


def payload_profe(idTxn, user, date, value, paymentMethod) -> dict:
    """Serialización para el HMAC: exactamente los campos que envía el profesor."""
    return {
        "idTxn": idTxn,
        "user": user,
        "date": date,
        "value": value,
        "paymentMethod": paymentMethod,
    }


def _parse_fecha(date_str: str) -> datetime:
    try:
        return datetime.fromisoformat(str(date_str))
    except ValueError:
        return datetime.utcnow()


def _obtener_cliente(db: Session, email: str) -> Cliente:
    """Identifica el cliente del negocio por email; lo crea si no existe."""
    c = db.query(Cliente).filter(Cliente.email == email).first()
    if c:
        return c
    c = Cliente(
        nombre=email.split("@")[0].replace(".", " ").title(),
        email=email,
        telefono="3000000000",
        tipo_cliente="Nuevo cliente",
        estado="activo",
    )
    db.add(c)
    db.flush()
    return c


def _obtener_usuario(db: Session, email: str) -> Usuario:
    """Identifica el usuario del contrato profesor (tabla usuarios)."""
    u = db.query(Usuario).filter(Usuario.email == email).first()
    if u:
        return u
    u = Usuario(nombre=email.split("@")[0], email=email, estado="activo")
    db.add(u)
    db.flush()
    return u


def ingest_una(db: Session, t) -> Tuple[Pedido, str]:
    """Procesa una transacción del profesor.

    Contrato del PDF (pag. 18): calcular hash -> ¿coincide? -> Aceptar/Rechazar.
    Retorna (pedido, estado) con estado en: NORMAL | POSIBLE_FRAUDE.
    Rechaza con HashInvalidoError si el hash no coincide con el payload.
    """
    datos = payload_profe(t.idTxn, t.user, t.date, t.value, t.paymentMethod)
    fecha_txn = _parse_fecha(t.date)

    # 1. VALIDAR EL HASH de ESTA transacción (PDF pag. 18: ¿coincide? -> Aceptar/Rechazar)
    #    Dos vias de aceptacion:
    #    a) Credencial: el hash autorizado que se le entrego al profesor (el mismo
    #       para todas sus transacciones, con los datos que su bot quiera).
    #    b) Firma HMAC del payload con la llave privada (via del dueño del sistema).
    hash_recibido = (t.hash or "").strip().lower()
    hash_credencial = hmac.compare_digest(hash_recibido, cfg.HASH_AUTORIZADO.strip().lower())
    hash_firma = verificar_hash(datos, cfg.LLAVE_SECRETA, t.hash)
    if not (hash_credencial or hash_firma):
        log_error(f"Hash invalido para idTxn={t.idTxn}", donde="ingest_una")
        raise HashInvalidoError(str(t.idTxn))

    # 2. DUPLICADOS por idTxn
    existente = db.query(Transaccion).filter(Transaccion.id_txn == str(t.idTxn)).first()
    if existente:
        log_error(f"idTxn duplicado {t.idTxn}", donde="ingest_una")
        raise DuplicadoError(str(t.idTxn))

    # 3. IDENTIFICAR usuario y cliente
    usuario = _obtener_usuario(db, t.user)
    cliente = _obtener_cliente(db, t.user)

    # 4. CREAR PEDIDO del negocio con código IP-XXXX autogenerado
    codigo = pedido_service.get_next_codigo(db)
    pedido = Pedido(
        codigo=codigo,
        cliente_id=cliente.id,
        productos="Fotografías",
        cantidad_total=1,
        valor=float(t.value),
        metodo_pago=t.paymentMethod or "Desconocido",
        estado="Solicitado",
        prioridad="Normal",
        direccion_entrega="Centro, Medellín",
        ip=t.ip,
        fecha_txn=fecha_txn,
        fecha=datetime.utcnow(),
    )
    db.add(pedido)
    db.flush()

    # 5. REGISTRAR TRANSACCIÓN (tabla del profesor)
    txn = Transaccion(
        id_txn=str(t.idTxn),
        usuario_id=usuario.id,
        pedido_id=pedido.id,
        valor=float(t.value),
        fecha_txn=fecha_txn,
        estado="NORMAL",
        hash=t.hash,
        metodo_pago=t.paymentMethod,
        ip=t.ip,
    )
    db.add(txn)
    db.flush()

    # Autofirma del servidor sobre el payload del negocio
    pedido.hash = generar_hash(pedido_service.payload_hash(pedido), cfg.LLAVE_SECRETA)
    pedido.id_txn = int(t.idTxn) if str(t.idTxn).isdigit() else None

    # 6. VENTANA DESLIZANTE por turno (10/6/3 s) sobre pedidos del cliente
    turno = cfg.turno_de_fecha(fecha_txn)
    ventana = cfg.ventana_por_turno(fecha_txn)
    historial = [p.fecha_txn for p in db.query(Pedido).filter(
        Pedido.cliente_id == cliente.id, Pedido.id != pedido.id).all()]
    res = detector.analizar(cliente.id, fecha_txn, ventana, historial)
    cantidad = res["cantidad_en_ventana"]

    # 7. EVALUACIÓN de anomalías (umbral configurable, defecto 3)
    estado = "NORMAL"
    if cantidad >= cfg.UMBRAL_TRANSACCIONES:
        estado = "POSIBLE_FRAUDE"
        db.add(Anomalia(
            pedido_id=pedido.id, cliente_id=cliente.id, tipo="POSIBLE_FRAUDE",
            nivel="alta", cantidad_transacciones=cantidad, ventana_segundos=ventana,
            detalle=f"{cantidad} pedidos de {t.user} en {ventana}s (turno {turno})",
        ))

    txn.estado = estado
    db.commit()
    db.refresh(pedido)
    log_evento(f"Txn {t.idTxn} user={t.user} estado={estado} turno={turno} ventana={ventana}s",
               donde="ingest_una")
    return pedido, estado


class DuplicadoError(Exception):
    def __init__(self, id_txn: str):
        super().__init__(f"idTxn duplicado: {id_txn}")
        self.id_txn = id_txn


class HashInvalidoError(Exception):
    def __init__(self, id_txn: str):
        super().__init__(f"Hash invalido para idTxn: {id_txn}")
        self.id_txn = id_txn


def ingest_lote(db: Session, items: List) -> dict:
    """Lote del profesor (hasta 1000): ordena por fecha y procesa todo."""
    resumen = {"TOTAL": 0, "NORMAL": 0, "POSIBLE_FRAUDE": 0,
               "RECHAZADO": 0, "RECHAZADO_DUPLICADO": 0, "RECHAZADO_HASH_INVALIDO": 0}
    detalle = []

    # Ordenar cronológicamente (PDF pag. 37)
    items_ordenados = sorted(items, key=lambda x: _parse_fecha(x.date))

    for item in items_ordenados:
        resumen["TOTAL"] += 1
        try:
            _, estado = ingest_una(db, item)
            resumen[estado] = resumen.get(estado, 0) + 1
            detalle.append({"idTxn": item.idTxn, "user": item.user, "deteccion": estado})
        except DuplicadoError:
            resumen["RECHAZADO_DUPLICADO"] += 1
            detalle.append({"idTxn": item.idTxn, "user": item.user,
                            "deteccion": "RECHAZADO_DUPLICADO"})
        except HashInvalidoError:
            resumen["RECHAZADO_HASH_INVALIDO"] += 1
            detalle.append({"idTxn": item.idTxn, "user": item.user,
                            "deteccion": "RECHAZADO_HASH_INVALIDO"})
        except Exception as e:
            db.rollback()
            resumen["RECHAZADO"] += 1
            log_error(f"Error procesando idTxn={getattr(item, 'idTxn', '?')}: {e}",
                      donde="ingest_lote")
            detalle.append({"idTxn": getattr(item, "idTxn", None),
                            "deteccion": "RECHAZADO", "motivo": str(e)})

    return {"resumen": resumen, "detalle": detalle}
