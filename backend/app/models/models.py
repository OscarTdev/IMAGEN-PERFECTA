"""Modelos del contrato del profesor (PDF Técnicas de resolución, pag. 45).

usuarios + transacciones comparten la Base de datos del negocio (MySQL):
el resto de tablas (clientes, pedidos, anomalias) vive en app/models/.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    estado = Column(String(20), default="activo", nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transacciones = relationship("Transaccion", back_populates="usuario")


class Transaccion(Base):
    """Log de transacciones del profesor: {idTxn, user, date, value, paymentMethod, hash}."""
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_txn = Column(String(100), unique=True, index=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    valor = Column(Numeric(12, 2), nullable=False, default=0)
    fecha_txn = Column(DateTime, index=True, nullable=False)
    estado = Column(String(30), default="NORMAL", nullable=False)
    hash = Column(String(128), nullable=True)
    metodo_pago = Column(String(50), nullable=True)
    ip = Column(String(45), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="transacciones")
