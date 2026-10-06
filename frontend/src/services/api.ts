import type {
  Cliente,
  ClienteCreate,
  Pedido,
  PedidoCreate,
  EstadoPedido,
  Anomalia,
  DashboardSeguridad,
  AppConfig,
  TxnProfeRow,
  ListaEnlazadaData,
  ColaData,
  HeapData,
  GrafoData,
  ResultadoDijkstra,
  ResultadoCombustible,
} from '../types';

const API_BASE_URL =
  (import.meta as unknown as { env?: Record<string, string> }).env
    ?.VITE_API_URL ?? 'http://localhost:8000/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Error HTTP ${response.status}`);
  }

  return response.json();
}

// ─── Clientes ───────────────────────────────────────────────────────
export const getClientes = (): Promise<Cliente[]> => fetchJson<Cliente[]>('/clientes');
export const createCliente = (data: ClienteCreate): Promise<Cliente> =>
  fetchJson<Cliente>('/clientes', {
    method: 'POST',
    body: JSON.stringify(data),
  });

// ─── Pedidos ────────────────────────────────────────────────────────
export const getPedidos = (): Promise<Pedido[]> => fetchJson<Pedido[]>('/pedidos');
export const createPedido = (data: PedidoCreate): Promise<Pedido> =>
  fetchJson<Pedido>('/pedidos', {
    method: 'POST',
    body: JSON.stringify(data),
  });
export const updateEstadoPedido = (id: number, estado: EstadoPedido): Promise<Pedido> =>
  fetchJson<Pedido>(`/pedidos/${id}/estado`, {
    method: 'PUT',
    body: JSON.stringify({ estado }),
  });
export const putPedido = (id: number, data: PedidoCreate): Promise<Pedido> =>
  fetchJson<Pedido>(`/pedidos/${id}`, { method: 'PUT', body: JSON.stringify(data) });

// ─── Transacciones (contrato profesor) ─────────────────────────────
export const getTransacciones = (): Promise<TxnProfeRow[]> =>
  fetchJson<TxnProfeRow[]>('/transacciones');

export const getAnomalias = (filtros?: { tipo?: string; estado_revision?: string }): Promise<Anomalia[]> => {
  const q = new URLSearchParams();
  if (filtros?.tipo) q.set('tipo', filtros.tipo);
  if (filtros?.estado_revision) q.set('estado_revision', filtros.estado_revision);
  const s = q.toString();
  return fetchJson<Anomalia[]>(`/anomalias${s ? `?${s}` : ''}`);
};
export const revisarAnomalia = (id: number, estado_revision: string): Promise<Anomalia> =>
  fetchJson<Anomalia>(`/anomalias/${id}`, { method: 'PATCH', body: JSON.stringify({ estado_revision }) });
export const getDashboardSeg = (): Promise<DashboardSeguridad> => fetchJson<DashboardSeguridad>('/dashboard');
export const getAppConfig = (): Promise<AppConfig> => fetchJson<AppConfig>('/config');
export const setAppConfig = (data: Partial<AppConfig> & { ventanas_turno?: Record<string, number> }): Promise<AppConfig> =>
  fetchJson<AppConfig>('/config', { method: 'PUT', body: JSON.stringify(data) });

// ─── Estructuras del negocio (Producción: flujo, turno FIFO, prioridades) ──
export const getListaEnlazada = (): Promise<ListaEnlazadaData> =>
  fetchJson<ListaEnlazadaData>('/estructuras/lista-enlazada');

export const agregarEtapaLista = (etapa: string): Promise<ListaEnlazadaData> =>
  fetchJson<ListaEnlazadaData>('/estructuras/lista-enlazada/agregar', {
    method: 'POST',
    body: JSON.stringify({ etapa }),
  });

export const getCola = (): Promise<ColaData> => fetchJson<ColaData>('/estructuras/cola');

export const enqueueCola = (codigo: string, cliente: string, productos: string): Promise<ColaData> =>
  fetchJson<ColaData>('/estructuras/cola/enqueue', {
    method: 'POST',
    body: JSON.stringify({ codigo, cliente, productos }),
  });

export const dequeueCola = (): Promise<{ atendido: { codigo: string; cliente: string; productos: string }; cola: ColaData }> =>
  fetchJson<{ atendido: { codigo: string; cliente: string; productos: string }; cola: ColaData }>('/estructuras/cola/dequeue', {
    method: 'POST',
  });

export const getHeap = (): Promise<HeapData> => fetchJson<HeapData>('/estructuras/heap');

export const insertarHeap = (codigo: string, cliente: string, prioridad: string): Promise<HeapData> =>
  fetchJson<HeapData>('/estructuras/heap/insertar', {
    method: 'POST',
    body: JSON.stringify({ codigo, cliente, prioridad }),
  });

export const extraerHeap = (): Promise<{ atendido: Record<string, unknown>; heap: HeapData }> =>
  fetchJson<{ atendido: Record<string, unknown>; heap: HeapData }>('/estructuras/heap/extraer', {
    method: 'POST',
  });

// ─── Entregas (grafo de zonas, Dijkstra y combustible) ──────────────
export const getGrafo = (): Promise<GrafoData> => fetchJson<GrafoData>('/rutas/grafo');

export const calcularDijkstra = (origen: string, destino: string): Promise<ResultadoDijkstra> =>
  fetchJson<ResultadoDijkstra>('/rutas/dijkstra', {
    method: 'POST',
    body: JSON.stringify({ origen, destino }),
  });

export const calcularCombustible = (
  distancia_km: number,
  rendimiento: number = 12.0,
  precio_litro: number = 14500.0
): Promise<ResultadoCombustible> =>
  fetchJson<ResultadoCombustible>('/rutas/combustible', {
    method: 'POST',
    body: JSON.stringify({ distancia_km, rendimiento, precio_litro }),
  });
