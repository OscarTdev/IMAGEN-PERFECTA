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


# ═══════════════════════════════════════════════════════════════════
# TESTS DE TRANSACCIONES, ANOMALÍAS Y DASHBOARD (PDF Appresso → Imagen Perfecta)
# Verifican uno a uno los requisitos del dashboard de seguridad:
#   D1-D15 banda día/semana/mes e indicadores,
#   A1-A6 evolución, niveles, línea de tiempo, ventana, métodos, por hora.
# ═══════════════════════════════════════════════════════════════════

from datetime import datetime  # noqa: E402

from app.core import config as cfg  # noqa: E402

HASH_OK = cfg.HASH_AUTORIZADO


def _txn(idTxn, user, date, value=50000, pago="Tarjeta", hash_=None):
    """Transacción en el formato EXACTO del profesor."""
    return {
        "idTxn": idTxn,
        "user": user,
        "date": date,
        "value": value,
        "paymentMethod": pago,
        "hash": hash_ or HASH_OK,
    }


class TestTransaccionesProfe:
    """Contrato del profesor: hash, duplicados, lote y ventana deslizante (REQUISITO D3)."""

    def test_txn_valida_normal(self):
        r = client.post("/api/transacciones", json=_txn(700001, "dash@test.co", "2026-10-05T14:30:01"))
        assert r.status_code == 200
        body = r.json()
        assert body["deteccion"] == "NORMAL"
        assert body["hash_valido"] is True
        assert body["codigo"].startswith("IP-")

    def test_hash_invalido_rechazado(self):
        r = client.post(
            "/api/transacciones",
            json=_txn(700002, "dash@test.co", "2026-10-05T14:30:02", hash_="ff" * 32),
        )
        assert r.status_code == 400
        assert "HASH_INVALIDO" in r.json()["detail"]

    def test_duplicado_rechazado(self):
        t = _txn(700003, "dup@test.co", "2026-10-05T14:31:01")
        r1 = client.post("/api/transacciones", json=t)
        assert r1.status_code == 200
        r2 = client.post("/api/transacciones", json=t)
        assert r2.status_code == 400
        assert "RECHAZADO_DUPLICADO" in r2.json()["detail"]

    def test_rafaga_genera_posible_fraude_y_linea_de_tiempo(self):
        """REQUISITOS D3 + A3: 3 tx del mismo usuario dentro de la ventana de su
        turno -> POSIBLE_FRAUDE con línea de tiempo persistida."""
        user = "rafaga@test.co"
        base = 710000
        fechas = ["2026-10-05T15:00:01", "2026-10-05T15:00:03", "2026-10-05T15:00:05"]
        detecciones = []
        for i, f in enumerate(fechas):
            r = client.post("/api/transacciones", json=_txn(base + i, user, f, value=10000 * (i + 1)))
            assert r.status_code == 200
            detecciones.append(r.json()["deteccion"])
        assert detecciones == ["NORMAL", "NORMAL", "POSIBLE_FRAUDE"]

        r = client.get("/api/anomalias", params={"tipo": "POSIBLE_FRAUDE"})
        propias = [a for a in r.json() if a["detalle"] and user in a["detalle"]]
        assert propias, "debe existir la anomalía de la ráfaga"
        a = propias[0]
        assert a["cantidad_transacciones"] == 3
        assert a["ventana_segundos"] == cfg.ventana_por_turno(datetime(2026, 10, 5, 15, 0, 5))
        # REQUISITO A3: línea de tiempo = transacciones dentro de la ventana
        assert len(a["transacciones_ventana"]) == 3
        assert [t["idTxn"] for t in a["transacciones_ventana"]] == [base, base + 1, base + 2]

    def test_lote_ordenado_con_ventana_por_usuario(self):
        """El lote se procesa ordenado cronológicamente aunque llegue desordenado."""
        lote = [
            _txn(720001, "lote@test.co", "2026-10-05T10:00:03"),
            _txn(720002, "lote@test.co", "2026-10-05T10:00:01"),
            _txn(720003, "lote@test.co", "2026-10-05T10:00:02"),
        ]
        r = client.post("/api/transacciones/lote", json=lote)
        assert r.status_code == 200
        body = r.json()
        assert body["resumen"]["TOTAL"] == 3
        assert body["resumen"]["NORMAL"] == 2
        assert body["resumen"]["POSIBLE_FRAUDE"] == 1
        assert body["detalle"][0]["deteccion"] == "NORMAL"
        assert body["detalle"][2]["deteccion"] == "POSIBLE_FRAUDE"


class TestDashboardSeguridad:
    """REQUISITOS D1-D15 y A1-A6: métricas agregadas del dashboard."""

    def test_dashboard_campos_agregados(self):
        r = client.get("/api/dashboard")
        assert r.status_code == 200
        d = r.json()

        # REQUISITOS D1 / D5: transacciones total + día/semana/mes
        for k in ("total", "hoy", "semana", "mes"):
            assert k in d["transacciones"]
        # REQUISITOS D1 / D6: anomalías total + día/semana/mes
        for k in ("total", "hoy", "semana", "mes"):
            assert k in d["anomalias"]
        # REQUISITOS D7, D11, D12, D13, D14
        for k in ("porcentaje", "nuevas", "abiertas", "revisadas", "descartadas"):
            assert k in d["anomalias"]
        # REQUISITOS D2 / D3 / A2: casos recurrentes por tipo y por nivel
        assert isinstance(d["anomalias"]["por_tipo"], dict)
        assert isinstance(d["anomalias"]["por_nivel"], dict)
        assert d["anomalias"]["por_tipo"].get("POSIBLE_FRAUDE", 0) >= 2
        # REQUISITOS D4 / D8: usuarios recurrentes y afectados
        assert isinstance(d["usuarios_recurrentes"], list)
        assert d["clientes_afectados"] >= 1
        # REQUISITOS D9 / D10: valor sospechoso y promedio por usuario
        assert d["valor_sospechoso"] > 0
        assert d["promedio_por_usuario"] > 0
        # REQUISITO A5: métodos de pago de las transacciones
        assert "Tarjeta" in d["por_metodo_pago"]
        # REQUISITO A6: distribución por hora con las 24 horas
        assert len(d["por_hora"]) == 24
        # REQUISITOS D15 / A1: serie diaria de 14 días (tendencias y picos)
        assert len(d["serie_diaria"]) == 14
        assert all({"fecha", "transacciones", "anomalias"} <= set(p) for p in d["serie_diaria"])

    def test_dashboard_solo_cuenta_transacciones_reales(self):
        """REQUISITO D5: los 30 pedidos semilla NO cuentan como transacciones."""
        d = client.get("/api/dashboard").json()
        assert d["pedidos"]["total"] >= 30
        assert d["transacciones"]["total"] >= 1
        assert d["transacciones"]["total"] < d["pedidos"]["total"]

    def test_revisar_anomalia(self):
        """REQUISITOS D12 → D13/D14: ciclo de revisión reflejado en el dashboard."""
        r = client.get("/api/anomalias", params={"estado_revision": "abierta"})
        abiertas = r.json()
        assert abiertas, "debe haber anomalías abiertas de las ráfagas"
        a = abiertas[0]
        r2 = client.patch(f"/api/anomalias/{a['id']}", json={"estado_revision": "revisada"})
        assert r2.status_code == 200
        assert r2.json()["estado_revision"] == "revisada"
        d = client.get("/api/dashboard").json()
        assert d["anomalias"]["revisadas"] >= 1

    def test_revisar_anomalia_inexistente(self):
        r = client.patch("/api/anomalias/999999", json={"estado_revision": "revisada"})
        assert r.status_code == 404

    def test_listar_anomalias_por_estado(self):
        """REQUISITOS D12-D14: filtro por estado de revisión."""
        r = client.get("/api/anomalias", params={"estado_revision": "revisada"})
        assert r.status_code == 200
        assert all(a["estado_revision"] == "revisada" for a in r.json())
