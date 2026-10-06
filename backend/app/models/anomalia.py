from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database.connection import Base

class Anomalia(Base):
    __tablename__ = "anomalias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    tipo = Column(String(40), nullable=False)  # MULTIPLES_PEDIDOS, HASH_INVALIDO, TURNO_EXCEDIDO
    nivel = Column(String(20), default="media", nullable=False)
    cantidad_transacciones = Column(Integer, default=0)
    ventana_segundos = Column(Integer, default=3)
    estado_revision = Column(String(20), default="abierta")  # abierta/revisada/descartada
    detalle = Column(String(500), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
