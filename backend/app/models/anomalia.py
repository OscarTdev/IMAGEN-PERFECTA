import json
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.database.connection import Base

class Anomalia(Base):
    __tablename__ = "anomalias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    tipo = Column(String(40), nullable=False)  # POSIBLE_FRAUDE, HASH_INVALIDO, TURNO_EXCEDIDO
    nivel = Column(String(20), default="media", nullable=False)
    cantidad_transacciones = Column(Integer, default=0)
    ventana_segundos = Column(Integer, default=3)
    estado_revision = Column(String(20), default="abierta")  # abierta/revisada/descartada
    detalle = Column(String(500), nullable=True)
    # REQUISITO A3 (línea de tiempo de una anomalía): JSON con las
    # transacciones que formaron la ventana deslizante
    # [{idTxn, fecha, valor, metodo_pago}]
    fechas_ventana = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def transacciones_ventana(self) -> list:
        """REQUISITO A3: transacciones dentro de la ventana al detectar."""
        if not self.fechas_ventana:
            return []
        try:
            data = json.loads(self.fechas_ventana)
            return data if isinstance(data, list) else []
        except (ValueError, TypeError):
            return []
