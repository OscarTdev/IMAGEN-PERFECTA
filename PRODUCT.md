# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Personal operativo de Imagen Perfecta (negocio de impresión fotográfica, Centro de Medellín) que gestiona clientes, pedidos, producción y entregas reales. Confirmado por entrevista: el uso principal es la operación del negocio, no solo la demostración en clase.

Audiencias secundarias confirmadas por el repositorio: docente y estudiantes de Programación Avanzada que evalúan y demuestran conceptos de ciencias de computación sobre datos del negocio (búsquedas, Big-O, recursión, regresión, Dijkstra, estructuras). El rediseño monocromo eliminó el interruptor académico y las pestañas Estructuras/Algoritmos del frontend por decisión del usuario; los algoritmos viven solo en el backend (verificables por HTTP, Swagger y las 41 pruebas), y Producción consume las estructuras del negocio (lista de flujo, cola FIFO del turno, heap de prioridades) porque son la operación misma del taller.

## Product Purpose

Registrar y dar seguimiento a clientes, pedidos, producción y entregas de fotografía/impresión en Medellín, con verificación de transacciones con hash de formato exacto del profesor.

Éxito significa: el personal puede operar el negocio (clientes, pedidos `IP-XXXX`, estados, producción, rutas de entrega, transacciones verificadas) y la evaluación académica puede comprobar el comportamiento funcional y medible de los conceptos implementados.

## Positioning

Un sistema de gestión anclado a un negocio fotográfico real de Medellín (zonas de entrega, tipos de cliente y productos propios) que además ejecuta la algoritmia y las estructuras en el backend de forma verificable: HMAC-SHA256 canónico para transacciones, ventana deslizante por turno configurable y endpoints académicos consumidos solo por HTTP. Un producto vecino de gestión genérica no podría copiar truthfully ese anclaje local más el contrato de verificación del profesor.

## Operating Context

Flujos confirmados en código:

- Navegación principal del frontend: Dashboard, Clientes, Pedidos, Producción (`imagen-perfecta/frontend/src/App.tsx`, `imagen-perfecta/frontend/src/pages/`).
- Backend FastAPI con lifespan que crea esquema, migra `id_txn` si falta y siembra datos (`imagen-perfecta/backend/app/main.py`).
- Transacciones formato profesor: recepción unitaria y por lote (máx. 1000), orden por fecha, validación de hash más ventana (`imagen-perfecta/backend/app/api/transacciones.py`, `imagen-perfecta/backend/app/services/transaccion_service.py` referenciado).
- Documentación y material académico en `docs/` (`ProgramacionAvanzada.pdf`, `ppt.pdf`, `Técnicas de resolución.pdf`) y vector de prueba en `pruebas_profesor.json` (raíz).
- Datos semilla: 10 clientes ficticios y 30 pedidos `IP-0001`–`IP-0030`; conjuntos temporales escalables para análisis de complejidad (según `imagen-perfecta/README.md`).
- Zonas de entrega: Centro, Laureles, Belén, El Poblado, Robledo, Envigado. Sede principal: Centro de Medellín.
- Tipos de cliente: Fotógrafo Profesional, Aficionado, Nuevo Cliente. Productos: Fotografías, Impresiones, Marcos, Portafolios.
- Flujo de producción modelado como lista enlazada: Impresión → Acabado → Enmarcado → Empaque → Despachado → NULL (según README; verificar contra `app/services` antes de afirmar implementación actual).
- Decisiones abiertas: si las superficies académicas del frontend se reconectan o permanecen ocultas tras el interruptor; objetivo de despliegue; necesidad de autenticación o multiusuario (no confirmados en código).

## Capabilities and Constraints

Capacidades confirmadas (no expandir sin evidencia):

- Clientes: `GET /api/clientes`, `POST /api/clientes`, `GET /api/clientes/{id}`.
- Pedidos: `GET /api/pedidos`, `POST /api/pedidos` (código autogenerado `IP-XXXX`), `GET /api/pedidos/{id}`, `PUT /api/pedidos/{id}/estado` con estados `Solicitado`, `En proceso`, `Listo`, `Entregado`.
- Transacciones profesor: `POST /api/transacciones` (`{idTxn,user,date,value,paymentMethod,hash}`), `POST /api/transacciones/lote`, `GET /api/transacciones`; rechazo con 400 (`RECHAZADO`, `RECHAZADO_DUPLICADO`) y 413 sobre 1000 por lote.
- Integridad: HMAC-SHA256 sobre serialización canónica (`sort_keys`, separadores compactos) con llave configurable (`IP_LLAVE_SECRETA`, defecto `mi_llave_privada_123`); comparación con `hmac.compare_digest` (`imagen-perfecta/backend/app/core/hash_utils.py`, `config.py`).
- Detección por ventana deslizante por turno configurable: mañana 05:00:01–12:00:00 → 10 s; tarde 12:00:01–20:00:00 → 6 s; noche 20:00:01–05:00:00 → 3 s; umbral 3 transacciones (`IP_UMBRAL_TX`, `IP_VENTANA_MANANA/TARDE/NOCHE`) (`imagen-perfecta/backend/app/core/config.py`).
- Superficies académicas documentadas en README (algoritmos, estructuras, rutas/Dijkstra, combustible) expuestas bajo `/api/algoritmos`, `/api/estructuras`, `/api/rutas`, `/api/dashboard`, `/api/config`, `/api/anomalias` según `main.py` y README; el cableado actual de routers en `main.py` incluye `clientes`, `pedidos`, `transacciones`, `seguridad` — verificar routers de algoritmos/estructuras/rutas en `app/api/` antes de afirmar rutas activas.
- Frontend: React 19 + TypeScript + Vite, Tailwind CSS v4, Ant Design 6 con locale `es-ES`, modo oscuro/claro persistido (`ip-theme`), interruptor académico persistido (`ip-academic`) (`imagen-perfecta/frontend/package.json`, `src/App.tsx`, `src/theme.ts`).
- Persistencia: MySQL mediante SQLAlchemy 2.0 y Pydantic v2; CORS abierto (`allow_origins=["*"]`).
- Pruebas: suite `pytest` en `imagen-perfecta/backend/tests/test_api.py` (README declara 41 pruebas).

Restricciones duras:

- Regla académica: ningún algoritmo académico en React; el frontend solo consume la API por HTTP y presenta resultados.
- No romper el formato exacto del profesor (`payload_profe`, script `imagen-perfecta/backend/generar_hash_profe.py`, `pruebas_profesor.json`).
- Llave secreta por entorno en producción; no hardcodear.
- Terminología preservada: `IP-XXXX`, `idTxn`, turnos `manana/tarde/noche`, prioridades `1: Urgente, 2: Alta, 3: Normal`, estados y zonas arriba indicados.
- Inconsistencia resuelta: backend configurado para MySQL (ver `app/database/connection.py`), el pie del frontend ya menciona "API FastAPI + MySQL" y el README también indica MySQL.

## Brand Commitments

Nombre existente: Imagen Perfecta, Centro de Medellín, Antioquia. Voz e interfaz en español. Referencias explícitas del usuario preservadas como vinculantes: ninguna dirección estética adicional fue dada en init, por lo que no se registra mundo visual, paleta, tipografía ni componentes.

## Evidence on Hand

- `imagen-perfecta/README.md`: contexto del negocio, arquitectura, endpoints, algoritmos, estructuras, grafo de Medellín, seed y comandos (`uvicorn app.main:app --reload --port 8000`, `npm run dev`, `pytest tests/test_api.py -v`).
- `pruebas_profesor.json` (raíz): 6 transacciones de prueba (`idTxn` 10001–10006) con hashes `GENERAR_LUEGO` y un `HASH_MALO_A_PROPOSITO` intencional.
- `imagen-perfecta/backend/generar_hash_profe.py`: generador de hash de formato exacto.
- `imagen-perfecta/backend/app/main.py`, `app/api/transacciones.py`, `app/core/hash_utils.py`, `app/core/config.py`: contrato real de transacciones y configuración.
- `imagen-perfecta/frontend/src/App.tsx`, `src/pages/`, `package.json`: navegación real y stack frontend.
- `docs/`: `ProgramacionAvanzada.pdf`, `ppt.pdf`, `Técnicas de resolución.pdf` (contenido no transcrito; no citar hechos de ellos sin leerlos).
- Ausencias que el trabajo futuro no debe fabricar: sin testimonios, clientes reales, benchmarks, precios, licencias ni afirmaciones de despliegue confirmadas.

## Product Principles

1. La operación del negocio manda: cada capacidad debe servir al registro y seguimiento real de clientes, pedidos, producción y entregas.
2. El backend demuestra, el frontend presenta: la lógica académica y de verificación vive en la API y es comprobable por HTTP y pruebas.
3. El contrato del profesor es inviolable: formato, hash canónico y ventanas por turno se preservan exactamente.
4. Nada inventado como evidencia: seed, documentos y vectores de prueba se citan con ruta; lo ausente se declara ausente.
5. Configurable por entorno, no por código rígido: llave, ventanas y umbrales cambian sin reescribir la lógica.
