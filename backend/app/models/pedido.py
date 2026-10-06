from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_txn = Column(Integer, nullable=True, index=True)  # idTxn externo del profesor
    codigo = Column(String(10), unique=True, index=True, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    fecha_txn = Column(DateTime, default=datetime.utcnow, index=True)
    productos = Column(String(500), nullable=False)
    cantidad_total = Column(Integer, CheckConstraint("cantidad_total > 0"), nullable=False)
    valor = Column(Float, default=0, nullable=False)
    metodo_pago = Column(String(30), default="Efectivo", nullable=False)
    ip = Column(String(45), nullable=True)
    estado = Column(String(20), default="Solicitado", nullable=False)
    hash = Column(String(128), nullable=True)
    prioridad = Column(String(10), default="Normal", nullable=False)
    direccion_entrega = Column(String(200), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="pedidos")
