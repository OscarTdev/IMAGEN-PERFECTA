from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine, Base, SessionLocal, SQLALCHEMY_DATABASE_URL
from app.api import clientes, pedidos, transacciones, seguridad, estructuras, rutas, algoritmos
from app import models  # noqa: F401 - registra Cliente, Pedido, Anomalia
from app.models.models import Usuario, Transaccion  # noqa: F401 - contrato profesor
from app.database.seed import seed_database



def _migrar_columnas():
    """Agrega id_txn si la DB externa es de una versión anterior."""
    try:
        from sqlalchemy import text
        with engine.connect() as c:
            cols = [r[1] for r in c.execute(text("PRAGMA table_info(pedidos)")).fetchall()]
            if "id_txn" not in cols:
                c.execute(text("ALTER TABLE pedidos ADD COLUMN id_txn INTEGER"))
                c.commit()
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializar la base de datos y datos de prueba al arrancar."""
    Base.metadata.create_all(bind=engine)
    _migrar_columnas()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Imagen Perfecta API",
    description="Sistema académico de gestión — Imagen Perfecta, Centro de Medellín",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(clientes.router)
app.include_router(pedidos.router)
app.include_router(transacciones.router)
app.include_router(seguridad.router)
app.include_router(estructuras.router)
app.include_router(rutas.router)
app.include_router(algoritmos.router)



@app.get("/")
def root():
    """Endpoint raíz con información de la API."""
    return {
        "nombre": "Imagen Perfecta API",
        "descripcion": "Sistema académico de gestión para impresión de fotografías",
        "version": "1.0.0",
        "ubicacion": "Centro de Medellín, Antioquia",
        "endpoints": {
            "clientes": "/api/clientes",
            "pedidos": "/api/pedidos",
            "anomalias": "/api/anomalias",
            "dashboard": "/api/dashboard",
            "config": "/api/config",
            "algoritmos": "/api/algoritmos",
            "estructuras": "/api/estructuras",
            "rutas": "/api/rutas",
            "docs": "/docs",
            "db_url": SQLALCHEMY_DATABASE_URL,
        },
    }
