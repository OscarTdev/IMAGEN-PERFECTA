from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine, Base, SessionLocal, SQLALCHEMY_DATABASE_URL
from app.api import clientes, pedidos, transacciones, seguridad, estructuras, rutas, algoritmos
from app import models  # noqa: F401 - registra Cliente, Pedido, Anomalia
from app.models.models import Usuario, Transaccion  # noqa: F401 - contrato profesor
from app.database.seed import seed_database



def _migrar_columnas():
    """Agrega columnas si la DB es de una versión anterior (SQLite o MySQL)."""
    from sqlalchemy import text

    def columnas(tabla: str) -> set:
        with engine.connect() as c:
            if engine.dialect.name == "sqlite":
                rows = c.execute(text(f"PRAGMA table_info({tabla})")).fetchall()
                return {r[1] for r in rows}
            rows = c.execute(
                text("SELECT column_name FROM information_schema.columns "
                     "WHERE table_schema = DATABASE() AND table_name = :t"),
                {"t": tabla},
            ).fetchall()
            return {r[0] for r in rows}

    def agregar_si_falta(tabla: str, columna: str, ddl_tipo: str):
        try:
            if columna not in columnas(tabla):
                with engine.begin() as c:
                    c.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {columna} {ddl_tipo}"))
        except Exception:
            pass

    agregar_si_falta("pedidos", "id_txn", "INTEGER")
    # REQUISITO A3: fechas_ventana persiste la línea de tiempo de la anomalía
    agregar_si_falta("anomalias", "fechas_ventana", "TEXT")


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
