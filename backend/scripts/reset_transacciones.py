"""Resetea las tablas del contrato del profesor antes de una demostracion.

Borra transacciones, anomalias, pedidos creados por transacciones y usuarios.
Conserva intactos los clientes y pedidos de la semilla del negocio (IP-0001..0030).

Uso:  python scripts/reset_transacciones.py   (desde la carpeta backend)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal  # noqa: E402
from app.models.pedido import Pedido  # noqa: E402
from app.models.anomalia import Anomalia  # noqa: E402
from app.models.models import Usuario, Transaccion  # noqa: E402

db = SessionLocal()
try:
    db.query(Anomalia).delete(synchronize_session=False)
    db.query(Transaccion).delete(synchronize_session=False)
    db.query(Pedido).filter(Pedido.id_txn.isnot(None)).delete(synchronize_session=False)
    db.query(Usuario).delete(synchronize_session=False)
    db.commit()
    print(f"Pedidos de la semilla: {db.query(Pedido).count()}")
    print(f"Transacciones: {db.query(Transaccion).count()} | "
          f"Anomalias: {db.query(Anomalia).count()} | "
          f"Usuarios: {db.query(Usuario).count()}")
    print("LISTO para una corrida fresca del profesor")
finally:
    db.close()
