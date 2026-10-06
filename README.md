# Imagen Perfecta — Sistema Académico de Gestión

Sistema web académico para **Imagen Perfecta**, un negocio ubicado en el Centro de Medellín, Antioquia, dedicado a la impresión fotográfica y productos relacionados (fotografías, impresiones, marcos y portafolios).

El proyecto adapta un conjunto de ejercicios académicos de algoritmia y estructuras de datos al contexto real de un negocio de fotografía, demostrando de forma funcional y medible los conceptos fundamentales de ciencias de la computación.

---

## 1. Contexto de Imagen Perfecta

* **Ubicación:** Centro de Medellín, Antioquia.
* **Actividad:** Impresión de fotografías e imágenes, enmarcado y encuadernación de portafolios.
* **Tipos de Clientes:** Fotógrafo Profesional, Aficionado y Nuevo Cliente.
* **Productos:** Fotografías, Impresiones, Marcos, Portafolios.
* **Zonas de Entrega:** Centro, Laureles, Belén, El Poblado, Robledo, Envigado.

---

## 2. Tecnologías Utilizadas

### Backend
* **Python 3.12**
* **FastAPI:** Framework moderno de alto rendimiento para APIs REST.
* **Pydantic v2:** Validación estricta de esquemas, tipos y restricciones.
* **SQLAlchemy 2.0:** ORM para conexión con base de datos.
* **SQLite:** Base de datos relacional ligera embebida (archivo `imagen_perfecta.db`).
* **Pytest & HTTPX:** Suite de pruebas automatizadas y cliente de pruebas HTTP.
* **NumPy:** Soporte para cálculos numéricos.

### Frontend
* **React 19 + TypeScript**
* **Vite 6 / 8:** Bundler ultrarrápido para desarrollo y producción.
* **Tailwind CSS v4:** Estilos modernos, responsivos y modo oscuro.
* **Iconografía SVG nativa:** Componentes SVG vectoriales optimizados.

---

## 3. Arquitectura del Sistema

Frontend y backend están completamente desacoplados:

```
imagen-perfecta/
│
├── frontend/                     # Aplicación React + Vite + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/           # Sidebar, Header, Iconos SVG
│   │   ├── pages/                # Dashboard, Clientes, Pedidos, Producción, Estructuras, Algoritmos, Rutas
│   │   ├── services/api.ts       # Consumo exclusivo de API HTTP (sin algoritmos en frontend)
│   │   ├── types/index.ts        # Interfaces y tipos TypeScript
│   │   ├── App.tsx               # Orquestador y navegación
│   │   └── main.tsx              # Entrada de la app
│   ├── package.json
│   └── README.md
│
├── backend/                      # API REST FastAPI + SQLite
│   ├── app/
│   │   ├── api/                  # Endpoints REST (clientes, pedidos, algoritmos, estructuras, rutas)
│   │   ├── algorithms/           # Búsquedas, O(n²), Big O, Gauss, progresión, regresión, Dijkstra
│   │   ├── database/             # Conexión SQLite y semilla inicial (10 clientes, 30 pedidos)
│   │   ├── models/               # Modelos SQLAlchemy (Cliente, Pedido)
│   │   ├── schemas/              # Schemas Pydantic con validación
│   │   ├── services/             # Lógica CRUD y estructuras (Lista enlazada, Pila, Cola, Heap)
│   │   └── main.py               # Instancia de FastAPI, CORS y lifespan
│   ├── tests/
│   │   └── test_api.py           # 41 pruebas unitarias y de integración con Pytest
│   ├── requirements.txt
│   └── README.md
│
├── README.md
└── .gitignore
```

> **Regla de Oro Académica:** Ningún algoritmo académico está implementado en React. El frontend solo consume la API REST mediante HTTP y presenta los resultados.

---

## 4. Instalación y Ejecución

### Prerrequisitos
* Python 3.10+ (probado con Python 3.12)
* Node.js 18+ (probado con Node.js v24 LTS) y npm

### Ejecución del Backend

1. Ingresar a la carpeta `backend`:
   ```bash
   cd backend
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Iniciar el servidor FastAPI con recarga automática:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   * La API estará disponible en: `http://localhost:8000`
   * Documentación Swagger interactiva: `http://localhost:8000/docs`

### Ejecución del Frontend

1. Ingresar a la carpeta `frontend`:
   ```bash
   cd frontend
   ```

2. Instalar dependencias:
   ```bash
   npm install
   ```

3. Iniciar el servidor de desarrollo Vite:
   ```bash
   npm run dev
   ```
   * El cliente web estará disponible en: `http://localhost:5173`

---

## 5. Ejecución de Pruebas Automatizadas

El backend incluye una suite completa de **41 pruebas automatizadas** en `backend/tests/test_api.py`:

```bash
cd backend
pytest tests/test_api.py -v
```

Cobertura de pruebas:
* **CRUD de Pedidos:** Listado, creación con validación, búsqueda por ID, actualización de estado, errores HTTP 404 y 422.
* **CRUD de Clientes:** Listado, creación, validación de tipo de cliente.
* **Búsqueda Lineal:** Caso exitoso O(n), caso no encontrado, mejor caso (1 op), peor caso (n op).
* **Búsqueda Binaria:** Caso exitoso O(log n), peor caso (<= log₂ n op), no encontrado.
* **Algoritmo Cuadrático O(n²):** Validación de comparaciones anidadas.
* **Sumatorias:** Fórmula de Gauss `S = n(n+1)/2` vs conteo iterativo de operaciones.
* **Progresión Aritmética:** `aₙ = a₁ + (n - 1)d`, cálculo exacto de semanas para 42, 72 y 120 productos.
* **Recursividad:** Procesamiento recursivo de lista de productos, caso base y conteo de llamadas.
* **Regresión Lineal:** Mínimos cuadrados para estimación en días 2, 5 y 7.
* **Estructuras de Datos:** Operaciones push/pop en Pila LIFO, enqueue/dequeue en Cola FIFO, inserción/extracción en Min-Heap de prioridad, recorrido y adición en Lista Enlazada.
* **Dijkstra y Rutas:** Grafo de Medellín, distancia óptima, ruta nodo a nodo, nodos visitados.
* **Combustible:** Cálculo configurable de litros y costo en COP.
* **Casos Límite:** Lista vacía, clientes duplicados, destinos inexistentes.

---

## 6. Algoritmos Académicos Implementados

| Algoritmo | Complejidad | Propósito en Imagen Perfecta | Por qué se utilizó |
|---|---|---|---|
| **Búsqueda Lineal** | $O(n)$ | Búsqueda secuencial de pedidos por ID | Permite buscar en listas no ordenadas; demuestra el peor caso al recorrer $n$ elementos. |
| **Búsqueda Binaria** | $O(\log n)$ | Búsqueda por bisección en pedidos ordenados | Demuestra la eficiencia de dividir el espacio a la mitad; pasa de 100,000 operaciones a solo 17. |
| **Comparación de Pares** | $O(n^2)$ | Comparación exhaustiva de pedidos con dos bucles anidados | Demostración académica del crecimiento cuadrático y cómo se relaciona con la sumatoria. |
| **Sumatoria de Gauss** | $O(1)$ analítico / $O(n)$ iterativo | $S = \frac{n(n+1)}{2}$ | Demuestra matemáticamente por qué un bucle anidado realiza $\approx \frac{n^2}{2}$ pasos. |
| **Progresión Aritmética** | $O(1)$ | Proyección semanal de pedidos: $a_n = a_1 + (n - 1)d$ | Determina en qué semana un cliente alcanza metas de 42, 72 y 120 productos fotográficos. |
| **Recursividad** | $O(n)$ | Procesamiento recursivo de lista de productos | Ilustra el concepto de caso base (índice $\ge n$) y caso recursivo con pila de llamadas. |
| **Regresión Lineal** | $O(n)$ | Proyección de ventas por mínimos cuadrados | Proyecta la tendencia de pedidos a días futuros (2, 5 y 7 días) mediante $y = mx + b$. |
| **Dijkstra** | $O((V + E) \log V)$ | Camino más corto para entregas en Medellín | Encuentra la ruta de menor distancia física entre la sede central y los barrios de la ciudad. |

---

## 7. Estructuras de Datos Utilizadas

1. **Lista Enlazada (Linked List):**
   * *Implementación:* Manual en Python con clases `Nodo` y `ListaEnlazada`.
   * *Aplicación:* Modela el flujo secuencial de producción: `Impresión → Acabado → Enmarcado → Empaque → Despachado → NULL`.
2. **Pila (Stack) — LIFO:**
   * *Implementación:* Lista con `push`, `pop`, `peek`.
   * *Aplicación:* Historial de acciones recientes del sistema (deshacer/auditoría).
3. **Cola (Queue) — FIFO:**
   * *Implementación:* `collections.deque` con `enqueue`, `dequeue`, `peek`.
   * *Aplicación:* Cola de producción estándar donde el primer pedido en llegar es el primero en ser procesado.
4. **Heap / Cola de Prioridad:**
   * *Implementación:* Módulo estándar `heapq` de Python con tuplas `(prioridad, contador, pedido)`.
   * *Aplicación:* Atención prioritaria de pedidos: `1: Urgente`, `2: Alta`, `3: Normal`.

---

## 8. Grafo de Medellín y Algoritmo de Dijkstra

El sistema modela las rutas de despacho desde la sede principal en el **Centro de Medellín**:

```
           [Robledo]
          /    |
       6.1km  4.5km
        /      |
   [Centro]--4.2km--[Laureles]
     |    \           /
   5.5km  5.8km    3.0km
     |      \       /
 [El Poblado] [Belén]
     \         /
    3.0km   6.2km
       \     /
      [Envigado]
```

* **Dijkstra:** Determina de forma exacta la secuencia de nodos y la distancia mínima acumulada.
* **Cálculo de Combustible:**
  $$\text{Litros} = \frac{\text{Distancia (km)}}{\text{Rendimiento (km/L)}}$$
  $$\text{Costo (COP)} = \text{Litros} \times \text{Precio por Litro}$$
  *(Ambos valores configurables en la interfaz gráfica)*.

---

## 9. Endpoints Principales de la API REST

### Clientes
* `GET /api/clientes` — Listar clientes registrados.
* `POST /api/clientes` — Registrar nuevo cliente.
* `GET /api/clientes/{id}` — Consultar cliente por ID.

### Pedidos
* `GET /api/pedidos` — Listar todos los pedidos.
* `POST /api/pedidos` — Crear nuevo pedido con código autogenerado `IP-XXXX`.
* `GET /api/pedidos/{id}` — Consultar pedido por ID.
* `PUT /api/pedidos/{id}/estado` — Actualizar estado (`Solicitado`, `En proceso`, `Listo`, `Entregado`).

### Algoritmos
* `POST /api/algoritmos/busqueda-lineal` — Búsqueda lineal con conteo de comparaciones.
* `POST /api/algoritmos/busqueda-binaria` — Búsqueda binaria en pedidos ordenados.
* `POST /api/algoritmos/complejidad` — Matriz comparativa para $n \in \{10, 100, 1000, 10000, 100000\}$.
* `POST /api/algoritmos/mejor-peor-caso` — Análisis de mejor y peor caso.
* `POST /api/algoritmos/sumatoria` — Cálculo de sumatoria $S = \frac{n(n+1)}{2}$.
* `POST /api/algoritmos/progresion` — Progresión aritmética $a_n = a_1 + (n - 1)d$.
* `POST /api/algoritmos/recursividad` — Recorrido recursivo de productos.
* `POST /api/algoritmos/regresion` — Regresión lineal de mínimos cuadrados para ventas.

### Estructuras de Datos
* `GET /api/estructuras/lista-enlazada` — Visualizar flujo de producción.
* `POST /api/estructuras/lista-enlazada/agregar` — Agregar etapa al flujo.
* `GET /api/estructuras/pila` / `POST /api/estructuras/pila/push` / `POST /api/estructuras/pila/pop` — Pila LIFO.
* `GET /api/estructuras/cola` / `POST /api/estructuras/cola/enqueue` / `POST /api/estructuras/cola/dequeue` — Cola FIFO.
* `GET /api/estructuras/heap` / `POST /api/estructuras/heap/insertar` / `POST /api/estructuras/heap/extraer` — Min-Heap.

### Rutas
* `GET /api/rutas/grafo` — Obtener nodos y aristas del grafo de Medellín.
* `POST /api/rutas/dijkstra` — Calcular ruta óptima más corta.
* `POST /api/rutas/combustible` — Estimar consumo y costo en COP.

---

## 10. Datos de Prueba (Seed Inicial)

La base de datos SQLite se inicializa automáticamente al arrancar con:
* **10 clientes ficticios** representativos de fotógrafos, aficionados y nuevos clientes.
* **30 pedidos de prueba** (`IP-0001` a `IP-0030`) con diferentes estados, prioridades, productos y direcciones en Medellín.
* Conjuntos temporales de prueba escalables hasta **100,000 pedidos** para análisis de complejidad computacional sin sobrecargar la base de datos.
