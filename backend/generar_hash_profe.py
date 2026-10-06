"""Genera hash formato EXACTO del profesor.
Uso: python generar_hash_profe.py
"""
import sys, json
sys.path.insert(0, ".")
from app.core.hash_utils import generar_hash
from app.core import config as cfg
from app.services.transaccion_service import payload_profe

datos = payload_profe(10001, "aa@aa.com", "2026-09-23T10:30:01.120", 50000, "Tarjeta")
h = generar_hash(datos, cfg.LLAVE_SECRETA)
print("HASH:", h)
print()
print(json.dumps({"idTxn": 10001, "user": "aa@aa.com",
                  "date": "2026-09-23T10:30:01.120", "value": 50000,
                  "paymentMethod": "Tarjeta", "hash": h}, indent=2))
