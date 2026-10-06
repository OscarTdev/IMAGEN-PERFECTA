# Imagen Perfecta — Backend API

Backend del sistema académico de gestión para **Imagen Perfecta** (Medellín, Antioquia), construido con **FastAPI**, **SQLAlchemy** y **MySQL**.

## Estructura

```
backend/
├── app/
│   ├── algorithms/       # Búsqueda lineal, binaria, Big O, Gauss, progresión, regresión, Dijkstra
│   ├── api/              # Routers FastAPI: clientes, pedidos, algoritmos, estructuras, rutas
│   ├── database/         # Conexión a MySQL y semilla inicial con 10 clientes y 30 pedidos
│   ├── models/           # Modelos relacionales SQLAlchemy (Cliente, Pedido)
│   ├── schemas/          # Modelos de validación Pydantic
│   ├── services/         # Operaciones CRUD y estructuras de datos (Lista, Pila, Cola, Heap)
│   └── main.py           # Instancia principal de FastAPI con CORS y Lifespan
├── tests/
│   └── test_api.py       # 41 pruebas unitarias y de integración
├── requirements.txt      # Dependencias del backend
└── README.md
```

## Instalación y Ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. (Opcional) Configurar variables de entorno para la DB
# Copiar .env.example a .env y ajustar:
#   DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME   (para MySQL)
#   O bien definir DATABASE_URL directamente (ej. mysql+pymysql://user:pass@host:port/db)
#   O bien definir IMAGEN_DB_PATH para usar SQLite (ruta a .db)
# Si no se define nada: se usa MySQL con credenciales por defecto (root@localhost/imagen_perfecta)

# 3. Iniciar servidor FastAPI
uvicorn app.main:app --reload --port 8000
```

* API Docs (Swagger UI): `http://localhost:8000/docs`
* API ReDoc: `http://localhost:8000/redoc`

## Ejecución de Pruebas

```bash
pytest tests/test_api.py -v
```

Todas las 41 pruebas pasan al 100%.
