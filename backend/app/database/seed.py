from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.core.hash_utils import generar_hash
from app.core import config as cfg
from datetime import datetime
import random

def seed_database(db: Session):
    if db.query(Cliente).first() is not None:
        # Migración suave: agrega columnas nuevas si faltan valores
        for c in db.query(Cliente).all():
            if not getattr(c, "estado", None):
                c.estado = "activo"
        db.commit()
        return

    clientes_data = [
        {"nombre": "Ana López", "email": "ana@imagen.co", "telefono": "3001234567", "tipo_cliente": "Fotógrafo", "estado": "activo"},
        {"nombre": "Carlos Restrepo", "email": "carlos@imagen.co", "telefono": "3109876543", "tipo_cliente": "Aficionado", "estado": "activo"},
        {"nombre": "María Gómez", "email": "maria@imagen.co", "telefono": "3154567890", "tipo_cliente": "Nuevo cliente", "estado": "activo"},
        {"nombre": "Jorge Ramírez", "email": "jorge@imagen.co", "telefono": "3201122334", "tipo_cliente": "Fotógrafo", "estado": "activo"},
        {"nombre": "Laura Pérez", "email": "laura@imagen.co", "telefono": "3015566778", "tipo_cliente": "Aficionado", "estado": "activo"},
        {"nombre": "Andrés Osorio", "email": "andres@imagen.co", "telefono": "3119988776", "tipo_cliente": "Nuevo cliente", "estado": "activo"},
        {"nombre": "Diana Castrillón", "email": "diana@imagen.co", "telefono": "3145544332", "tipo_cliente": "Fotógrafo", "estado": "activo"},
        {"nombre": "Santiago Marín", "email": "santiago@imagen.co", "telefono": "3123344556", "tipo_cliente": "Aficionado", "estado": "activo"},
        {"nombre": "Camila Jaramillo", "email": "camila@imagen.co", "telefono": "3167788990", "tipo_cliente": "Nuevo cliente", "estado": "activo"},
        {"nombre": "Esteban Salazar", "email": "esteban@imagen.co", "telefono": "3004455667", "tipo_cliente": "Fotógrafo", "estado": "activo"},
    ]

    db_clientes = []
    for data in clientes_data:
        c = Cliente(**data)
        db.add(c)
        db_clientes.append(c)
    db.commit()
    for c in db_clientes:
        db.refresh(c)

    estados = ['Solicitado', 'En proceso', 'Listo', 'Entregado']
    prioridades = ['Normal', 'Alta', 'Urgente']
    barrios = ["El Poblado", "Laureles", "Envigado", "Sabaneta", "Bello", "Centro", "Belén", "Robledo", "Manrique", "Aranjuez"]
    productos_list = ["Fotografías", "Marcos", "Impresiones", "Portafolios"]
    pagos = ["Efectivo", "Tarjeta", "Transferencia", "Nequi"]

    for i in range(1, 31):
        codigo = f"IP-{i:04d}"
        cliente = random.choice(db_clientes)
        productos = ",".join(random.sample(productos_list, random.randint(1, 3)))
        cantidad = random.randint(1, 100)
        valor = random.choice([15000, 30000, 50000, 80000, 120000])
        metodo = random.choice(pagos)
        fecha_txn = datetime.utcnow()
        pedido = Pedido(
            codigo=codigo, cliente_id=cliente.id, productos=productos,
            cantidad_total=cantidad, valor=valor, metodo_pago=metodo,
            estado=random.choice(estados), prioridad=random.choice(prioridades),
            direccion_entrega=f"Calle {random.randint(10,100)} #{random.randint(10,100)}-{random.randint(10,100)}, {random.choice(barrios)}, Medellín",
            fecha_txn=fecha_txn, fecha=fecha_txn,
        )
        db.add(pedido)
        db.flush()
        datos = {"cliente_id": cliente.id, "productos": productos,
                 "cantidad_total": cantidad, "valor": valor, "metodo_pago": metodo,
                 "fecha_txn": fecha_txn.isoformat()}
        pedido.hash = generar_hash(datos, cfg.LLAVE_SECRETA)
    db.commit()
