"""
Tests para el backend de Imagen Perfecta.
Cubre pedidos, algoritmos, estructuras de datos y casos límite.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.connection import Base, get_db
from app.database.seed import seed_database

# ─── Setup de la base de datos de prueba ────────────────────────────

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_imagen_perfecta.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crear tablas y semilla una sola vez para toda la sesión de tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    import os
    try:
        if os.path.exists("./test_imagen_perfecta.db"):
            os.remove("./test_imagen_perfecta.db")
    except Exception:
        pass


client = TestClient(app)


# ═══════════════════════════════════════════════════════════════════
# TESTS DE PEDIDOS
# ═══════════════════════════════════════════════════════════════════


class TestPedidos:
    """Tests para CRUD de pedidos."""

    def test_listar_pedidos(self):
        response = client.get("/api/pedidos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 30  # Seed crea 30

    def test_crear_pedido(self):
        pedido = {
            "cliente_id": 1,
            "productos": "Fotografías,Marcos",
            "cantidad_total": 5,
            "prioridad": "Alta",
            "direccion_entrega": "Calle 50 #30-10, Laureles, Medellín",
        }
        response = client.post("/api/pedidos", json=pedido)
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["estado"] == "Solicitado"
        assert data["prioridad"] == "Alta"
        assert "codigo" in data

    def test_buscar_pedido_existente(self):
        response = client.get("/api/pedidos/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_buscar_pedido_inexistente(self):
        response = client.get("/api/pedidos/99999")
        assert response.status_code == 404

    def test_cambiar_estado(self):
        response = client.put("/api/pedidos/1/estado", json={"estado": "En proceso"})
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "En proceso"

    def test_estado_invalido(self):
        response = client.put("/api/pedidos/1/estado", json={"estado": "Cancelado"})
        assert response.status_code == 422

    def test_cantidad_invalida(self):
        pedido = {
            "cliente_id": 1,
            "productos": "Marcos",
            "cantidad_total": -1,
            "prioridad": "Normal",
            "direccion_entrega": "Centro, Medellín",
        }
        response = client.post("/api/pedidos", json=pedido)
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════
# TESTS DE CLIENTES
# ═══════════════════════════════════════════════════════════════════


class TestClientes:
    """Tests para CRUD de clientes."""

    def test_listar_clientes(self):
        response = client.get("/api/clientes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 10

    def test_crear_cliente(self):
        cliente = {
            "nombre": "Test Cliente",
            "telefono": "3001112233",
            "tipo_cliente": "Fotógrafo",
        }
        response = client.post("/api/clientes", json=cliente)
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["nombre"] == "Test Cliente"

    def test_buscar_cliente_inexistente(self):
        response = client.get("/api/clientes/99999")
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# TESTS DE ALGORITMOS
# ═══════════════════════════════════════════════════════════════════


class TestBusquedaLineal:
    """Tests para búsqueda lineal O(n)."""

    def test_busqueda_exitosa(self):
        response = client.post(
            "/api/algoritmos/busqueda-lineal",
            json={"tamanio": 100, "id_buscado": "IP-0050"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["encontrado"] is True
        assert data["complejidad"] == "O(n)"
        assert data["operaciones"] == 50

    def test_busqueda_no_encontrado(self):
        response = client.post(
            "/api/algoritmos/busqueda-lineal",
            json={"tamanio": 100, "id_buscado": "IP-9999"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["encontrado"] is False
        assert data["operaciones"] == 100  # Recorrió todo

    def test_mejor_caso(self):
        response = client.post(
            "/api/algoritmos/busqueda-lineal",
            json={"tamanio": 1000, "id_buscado": "IP-0001"},
        )
        data = response.json()
        assert data["operaciones"] == 1  # Primer elemento


class TestBusquedaBinaria:
    """Tests para búsqueda binaria O(log n)."""

    def test_busqueda_exitosa(self):
        response = client.post(
            "/api/algoritmos/busqueda-binaria",
            json={"tamanio": 100, "id_buscado": "IP-0050"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["encontrado"] is True
        assert data["complejidad"] == "O(log n)"
        assert data["operaciones"] <= 7  # log2(100) ≈ 6.6

    def test_busqueda_no_encontrado(self):
        response = client.post(
            "/api/algoritmos/busqueda-binaria",
            json={"tamanio": 100, "id_buscado": "IP-9999"},
        )
        data = response.json()
        assert data["encontrado"] is False


class TestCuadratico:
    """Tests para algoritmo cuadrático O(n²)."""

    def test_complejidad(self):
        response = client.post(
            "/api/algoritmos/complejidad",
            json={"tamanios": [10, 100]},
        )
        assert response.status_code == 200
        data = response.json()
        resultados = data["resultados"]
        assert len(resultados) == 2
        # n=10: cuadrático debería tener ~45 operaciones (n*(n-1)/2)
        assert resultados[0]["cuadratico"]["operaciones"] > 0


class TestSumatoria:
    """Tests para sumatoria S = n(n+1)/2."""

    def test_sumatoria_10(self):
        response = client.post("/api/algoritmos/sumatoria", json={"n": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["sumatoria_formula"] == 55
        assert data["n"] == 10

    def test_sumatoria_100(self):
        response = client.post("/api/algoritmos/sumatoria", json={"n": 100})
        data = response.json()
        assert data["sumatoria_formula"] == 5050


class TestProgresion:
    """Tests para progresión aritmética."""

    def test_progresion_default(self):
        response = client.post(
            "/api/algoritmos/progresion",
            json={"a1": 2, "d": 2, "objetivos": [42, 72, 120]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["primer_termino"] == 2
        assert data["diferencia"] == 2
        assert len(data["objetivos"]) == 3
        # a_n = 2 + (n-1)*2 = 2n -> para 42: n=21
        assert data["objetivos"][0]["semana"] == 21


class TestRecursividad:
    """Tests para función recursiva."""

    def test_recursion_basica(self):
        response = client.post(
            "/api/algoritmos/recursividad",
            json={"productos": ["Foto", "Marco", "Portafolio"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["cantidad"] == 3
        assert data["llamadas_recursivas"] == 4  # 3 items + 1 caso base
        assert len(data["resultados"]) == 3


class TestRegresion:
    """Tests para regresión lineal."""

    def test_regresion_default(self):
        response = client.post("/api/algoritmos/regresion", json={})
        assert response.status_code == 200
        data = response.json()
        assert "pendiente" in data
        assert "intercepto" in data
        assert len(data["predicciones"]) == 3
        assert "nota" in data


# ═══════════════════════════════════════════════════════════════════
# TESTS DE ESTRUCTURAS DE DATOS
# ═══════════════════════════════════════════════════════════════════


class TestListaEnlazada:
    """Tests para lista enlazada."""

    def test_obtener_lista(self):
        response = client.get("/api/estructuras/lista-enlazada")
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "Lista Enlazada"
        assert "Impresión" in data["etapas"]
        assert "Despachado" in data["etapas"]

    def test_agregar_etapa(self):
        response = client.post(
            "/api/estructuras/lista-enlazada/agregar",
            json={"etapa": "Control de calidad"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "Control de calidad" in data["etapas"]


class TestPila:
    """Tests para pila LIFO."""

    def test_obtener_pila(self):
        response = client.get("/api/estructuras/pila")
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "Pila (LIFO)"
        assert data["tamanio"] > 0

    def test_push(self):
        response = client.post(
            "/api/estructuras/pila/push",
            json={"accion": "Test acción", "detalle": "Prueba"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tope"]["accion"] == "Test acción"

    def test_pop(self):
        # Primero push
        client.post(
            "/api/estructuras/pila/push",
            json={"accion": "Para eliminar", "detalle": "Test"},
        )
        response = client.post("/api/estructuras/pila/pop")
        assert response.status_code == 200
        data = response.json()
        assert data["eliminado"]["accion"] == "Para eliminar"


class TestCola:
    """Tests para cola FIFO."""

    def test_obtener_cola(self):
        response = client.get("/api/estructuras/cola")
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "Cola (FIFO)"

    def test_enqueue(self):
        response = client.post(
            "/api/estructuras/cola/enqueue",
            json={"codigo": "IP-TEST", "cliente": "Test", "productos": "Foto"},
        )
        assert response.status_code == 200

    def test_dequeue(self):
        response = client.post("/api/estructuras/cola/dequeue")
        assert response.status_code == 200
        data = response.json()
        assert "atendido" in data


class TestHeap:
    """Tests para heap / cola de prioridad."""

    def test_obtener_heap(self):
        response = client.get("/api/estructuras/heap")
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "Heap / Cola de Prioridad"

    def test_insertar(self):
        response = client.post(
            "/api/estructuras/heap/insertar",
            json={"codigo": "IP-HEAP", "cliente": "Test", "prioridad": "Urgente"},
        )
        assert response.status_code == 200

    def test_extraer(self):
        response = client.post("/api/estructuras/heap/extraer")
        assert response.status_code == 200
        data = response.json()
        assert "atendido" in data


# ═══════════════════════════════════════════════════════════════════
# TESTS DE RUTAS Y DIJKSTRA
# ═══════════════════════════════════════════════════════════════════


class TestDijkstra:
    """Tests para Dijkstra y cálculo de rutas."""

    def test_obtener_grafo(self):
        response = client.get("/api/rutas/grafo")
        assert response.status_code == 200
        data = response.json()
        assert "Centro" in data["nodos"]
        assert len(data["aristas"]) > 0

    def test_dijkstra_centro_envigado(self):
        response = client.post(
            "/api/rutas/dijkstra",
            json={"origen": "Centro", "destino": "Envigado"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["origen"] == "Centro"
        assert data["destino"] == "Envigado"
        assert len(data["ruta"]) >= 2
        assert data["distancia_km"] > 0

    def test_dijkstra_centro_laureles(self):
        response = client.post(
            "/api/rutas/dijkstra",
            json={"origen": "Centro", "destino": "Laureles"},
        )
        data = response.json()
        assert data["distancia_km"] == 4.2  # Directa

    def test_destino_inexistente(self):
        response = client.post(
            "/api/rutas/dijkstra",
            json={"origen": "Centro", "destino": "Sabaneta"},
        )
        assert response.status_code == 404


class TestCombustible:
    """Tests para cálculo de combustible."""

    def test_calculo_basico(self):
        response = client.post(
            "/api/rutas/combustible",
            json={"distancia_km": 12.0, "rendimiento": 12.0, "precio_litro": 14500.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["litros_estimados"] == 1.0
        assert data["costo_estimado"] == 14500.0

    def test_distancia_cero(self):
        response = client.post(
            "/api/rutas/combustible",
            json={"distancia_km": 0},
        )
        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════
# TESTS DE CASOS LÍMITE
# ═══════════════════════════════════════════════════════════════════


class TestCasosLimite:
    """Tests para casos límite."""

    def test_lista_vacia_busqueda_lineal(self):
        response = client.post(
            "/api/algoritmos/busqueda-lineal",
            json={"tamanio": 0, "id_buscado": "IP-0001"},
        )
        # Tamaño 0 no debería encontrar nada
        data = response.json()
        assert data["encontrado"] is False

    def test_id_duplicado_cliente(self):
        # Crear dos clientes con los mismos datos (debería funcionar - IDs son auto)
        cliente = {
            "nombre": "Duplicado Test",
            "telefono": "3009999999",
            "tipo_cliente": "Nuevo cliente",
        }
        r1 = client.post("/api/clientes", json=cliente)
        r2 = client.post("/api/clientes", json=cliente)
        assert r1.status_code in (200, 201)
        assert r2.status_code in (200, 201)
        assert r1.json()["id"] != r2.json()["id"]

    def test_mejor_peor_caso(self):
        response = client.post(
            "/api/algoritmos/mejor-peor-caso",
            json={"n": 100},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["lineal"]["mejor"]["operaciones"] < data["lineal"]["peor"]["operaciones"]
