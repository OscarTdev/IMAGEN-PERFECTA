// Tipos para clientes
export type TipoCliente = 'Fotógrafo' | 'Aficionado' | 'Nuevo cliente';

export interface Cliente {
  id: number;
  nombre: string;
  email?: string;
  telefono: string;
  tipo_cliente: TipoCliente;
  estado?: string;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

export interface ClienteCreate {
  nombre: string;
  email?: string;
  telefono: string;
  tipo_cliente: TipoCliente;
  estado?: string;
}

// Tipos para pedidos
export type EstadoPedido = 'Solicitado' | 'En proceso' | 'Listo' | 'Entregado';
export type PrioridadPedido = 'Normal' | 'Alta' | 'Urgente';

export interface Pedido {
  id: number;
  codigo: string;
  cliente_id: number;
  fecha: string;
  fecha_txn?: string;
  productos: string;
  cantidad_total: number;
  valor?: number;
  metodo_pago?: string;
  ip?: string;
  estado: EstadoPedido;
  prioridad: PrioridadPedido;
  direccion_entrega: string;
  hash?: string;
}

export interface PedidoCreate {
  cliente_id: number;
  productos: string;
  cantidad_total: number;
  prioridad: PrioridadPedido;
  direccion_entrega: string;
  valor?: number;
  metodo_pago?: string;
  ip?: string;
  fecha_txn?: string;
  hash?: string;
}

export interface Anomalia {
  id: number;
  pedido_id?: number;
  cliente_id?: number;
  tipo: string;
  nivel: string;
  cantidad_transacciones: number;
  ventana_segundos: number;
  estado_revision: string;
  detalle?: string;
  fecha_creacion?: string;
}

export interface DashboardSeguridad {
  pedidos: { total: number; hoy: number; semana: number; mes: number };
  anomalias: { total: number; hoy: number; semana: number; mes: number; abiertas: number; revisadas: number; descartadas: number; porcentaje: number };
  clientes_afectados: number;
  clientes_recurrentes: number[];
  valor_sospechoso: number;
  promedio_por_cliente: number;
  por_hora: Record<string, number>;
  por_metodo_pago: Record<string, number>;
}

export interface AppConfig {
  ventana_segundos: number;
  umbral_transacciones: number;
  ventanas_turno: { manana: number; tarde: number; noche: number };
}

// Transacciones en formato del profesor (GET /api/transacciones)
export interface TxnProfeRow {
  idTxn: number | string;
  user: string;
  date: string;
  value: number;
  paymentMethod: string;
  hash?: string | null;
  codigo?: string;
}

// Estructuras de Datos (Producción: flujo, cola y heap del negocio)
export interface ListaEnlazadaData {
  tipo: string;
  descripcion: string;
  etapas: string[];
  estructura: string;
}

export interface ItemCola {
  codigo: string;
  cliente: string;
  productos: string;
  fecha: string;
}

export interface ColaData {
  tipo: string;
  descripcion: string;
  items: ItemCola[];
  tamanio: number;
  proximo: ItemCola | null;
}

export interface ItemHeap {
  prioridad: number;
  pedido: {
    codigo: string;
    cliente: string;
    fecha?: string;
    productos?: string;
  };
}

export interface HeapData {
  tipo: string;
  descripcion: string;
  items: ItemHeap[];
  tamanio: number;
  proximo: Record<string, unknown> | null;
  explicacion: string;
}

// Rutas y Dijkstra
export interface AristaGrafo {
  origen: string;
  destino: string;
  distancia_km: number;
}

export interface GrafoData {
  nodos: string[];
  aristas: AristaGrafo[];
  nodo_principal?: string;
}

export interface PasoDijkstra {
  nodo_actual: string;
  distancia_acumulada: number | null;
  accion: string;
}

export interface ResultadoDijkstra {
  origen: string;
  destino: string;
  ruta: string[];
  distancia_km: number | null;
  nodos_visitados: string[];
  pasos?: PasoDijkstra[];
  nota?: string;
  explicacion?: string;
}

export interface ResultadoCombustible {
  distancia_km: number;
  rendimiento_km_por_litro: number;
  litros_estimados: number;
  precio_por_litro: number;
  costo_estimado: number;
  formula?: string;
  nota?: string;
}
