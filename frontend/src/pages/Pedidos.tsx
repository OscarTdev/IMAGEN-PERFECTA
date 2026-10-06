import React, { useEffect, useMemo, useState } from 'react';
import {
  App as AntdApp,
  Button,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Table,
  Tag,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { getPedidos, createPedido, updateEstadoPedido, putPedido, getClientes } from '../services/api';
import type { Pedido, Cliente, EstadoPedido, PrioridadPedido } from '../types';
import { ErrorBlock, LoadingBlock } from '../components/ui';

const ESTADO_COLOR: Record<EstadoPedido, string> = {
  Solicitado: 'default',
  'En proceso': 'processing',
  Listo: 'warning',
  Entregado: 'success',
};

const PRIORIDAD_COLOR: Record<PrioridadPedido, string> = {
  Urgente: 'error',
  Alta: 'warning',
  Normal: 'default',
};

const COP = (v?: number) =>
  v ? v.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }) : '—';

export const Pedidos: React.FC = () => {
  const { message } = AntdApp.useApp();
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState<string>('todos');
  const [filtroPrioridad, setFiltroPrioridad] = useState<string>('todos');

  const [pedidoSeleccionado, setPedidoSeleccionado] = useState<Pedido | null>(null);
  const [mostrarModalCrear, setMostrarModalCrear] = useState(false);
  const [pedidoEditando, setPedidoEditando] = useState<Pedido | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [guardandoEdicion, setGuardandoEdicion] = useState(false);
  const [form] = Form.useForm();
  const [formEditar] = Form.useForm();

  const cargarDatos = () => {
    setLoading(true);
    setError(null);
    Promise.all([getPedidos(), getClientes()])
      .then(([pedidosData, clientesData]) => {
        setPedidos(pedidosData);
        setClientes(clientesData);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    cargarDatos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getNombreCliente = (clienteId: number) => {
    const c = clientes.find((item) => item.id === clienteId);
    return c ? c.nombre : `Cliente #${clienteId}`;
  };

  const handleCrearPedido = async (values: {
    cliente_id: number;
    productos: string;
    cantidad_total: number;
    prioridad: PrioridadPedido;
    direccion_entrega: string;
    valor?: number;
  }) => {
    setGuardando(true);
    try {
      await createPedido({
        cliente_id: Number(values.cliente_id),
        productos: values.productos,
        cantidad_total: Number(values.cantidad_total),
        prioridad: values.prioridad,
        direccion_entrega: values.direccion_entrega,
        valor: values.valor ? Number(values.valor) : undefined,
      });
      message.success('Pedido creado');
      setMostrarModalCrear(false);
      form.resetFields();
      cargarDatos();
    } catch (err) {
      message.error(`Error al crear pedido: ${err instanceof Error ? err.message : 'desconocido'}`);
    } finally {
      setGuardando(false);
    }
  };

  const handleCambiarEstado = async (id: number, nuevoEstado: EstadoPedido) => {
    try {
      const actualizado = await updateEstadoPedido(id, nuevoEstado);
      setPedidos((prev) => prev.map((p) => (p.id === id ? actualizado : p)));
      if (pedidoSeleccionado?.id === id) setPedidoSeleccionado(actualizado);
      message.success(`Pedido → ${nuevoEstado}`);
    } catch (err) {
      message.error(`Error al actualizar: ${err instanceof Error ? err.message : 'desconocido'}`);
    }
  };

  const abrirEdicion = (p: Pedido) => {
    setPedidoEditando(p);
    formEditar.setFieldsValue({
      cliente_id: p.cliente_id,
      productos: p.productos,
      cantidad_total: p.cantidad_total,
      valor: p.valor ?? 0,
      prioridad: p.prioridad,
      direccion_entrega: p.direccion_entrega,
    });
  };

  const handleEditar = async (values: {
    cliente_id: number;
    productos: string;
    cantidad_total: number;
    prioridad: PrioridadPedido;
    direccion_entrega: string;
    valor?: number;
  }) => {
    if (!pedidoEditando) return;
    setGuardandoEdicion(true);
    try {
      const actualizado = await putPedido(pedidoEditando.id, {
        cliente_id: Number(values.cliente_id),
        productos: values.productos,
        cantidad_total: Number(values.cantidad_total),
        prioridad: values.prioridad,
        direccion_entrega: values.direccion_entrega,
        valor: values.valor ? Number(values.valor) : 0,
      });
      message.success(`Pedido ${actualizado.codigo} actualizado`);
      setPedidoEditando(null);
      cargarDatos();
    } catch (err) {
      message.error(`Error al editar: ${err instanceof Error ? err.message : 'desconocido'}`);
    } finally {
      setGuardandoEdicion(false);
    }
  };

  const pedidosFiltrados = useMemo(
    () =>
      pedidos.filter((p) => {
        const matchBusqueda =
          p.codigo.toLowerCase().includes(busqueda.toLowerCase()) ||
          getNombreCliente(p.cliente_id).toLowerCase().includes(busqueda.toLowerCase()) ||
          p.id.toString() === busqueda;
        const matchEstado = filtroEstado === 'todos' || p.estado === filtroEstado;
        const matchPrioridad = filtroPrioridad === 'todos' || p.prioridad === filtroPrioridad;
        return matchBusqueda && matchEstado && matchPrioridad;
        // eslint-disable-next-line react-hooks/exhaustive-deps
      }),
    [pedidos, clientes, busqueda, filtroEstado, filtroPrioridad]
  );

  const columns: ColumnsType<Pedido> = [
    {
      title: 'Código',
      dataIndex: 'codigo',
      key: 'codigo',
      render: (c: string) => <span className="font-data font-bold text-[12px]">{c}</span>,
      sorter: (a, b) => a.codigo.localeCompare(b.codigo),
    },
    {
      title: 'Cliente',
      dataIndex: 'cliente_id',
      key: 'cliente_id',
      render: (id: number) => getNombreCliente(id),
    },
    { title: 'Productos', dataIndex: 'productos', key: 'productos', ellipsis: true },
    {
      title: 'Valor',
      dataIndex: 'valor',
      key: 'valor',
      render: (v: number | undefined) => (
        <span className="font-data text-[12px]">{COP(v)}</span>
      ),
      sorter: (a, b) => (a.valor ?? 0) - (b.valor ?? 0),
    },
    {
      title: 'Prioridad',
      dataIndex: 'prioridad',
      key: 'prioridad',
      render: (p: PrioridadPedido) => <Tag color={PRIORIDAD_COLOR[p]}>{p}</Tag>,
    },
    {
      title: 'Estado',
      dataIndex: 'estado',
      key: 'estado',
      render: (e: EstadoPedido) => <Tag color={ESTADO_COLOR[e]}>{e}</Tag>,
    },
    {
      title: 'Entrega',
      dataIndex: 'fecha',
      key: 'fecha',
      render: (f: string) => (
        <span className="font-data text-[12px] text-silver dark:text-[#8d8c85]">
          {new Date(f).toLocaleDateString('es-CO')}
        </span>
      ),
      sorter: (a, b) => +new Date(a.fecha) - +new Date(b.fecha),
    },
    {
      title: '',
      key: 'acciones',
      align: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => abrirEdicion(r)}>
            Editar
          </Button>
          <Button type="link" size="small" onClick={() => setPedidoSeleccionado(r)}>
            Ver detalle
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Banda de trabajo: buscar, filtrar, crear */}
      <div className="flex flex-col md:flex-row md:items-center gap-3 md:gap-4 border-b border-hairline dark:border-[#2a2a26] pb-4">
        <Input.Search
          placeholder="Buscar por código (IP-0001) o cliente…"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          allowClear
          className="flex-1"
        />
        <Select
          value={filtroEstado}
          onChange={setFiltroEstado}
          className="w-full md:w-44"
          options={[
            { value: 'todos', label: 'Todos los estados' },
            { value: 'Solicitado', label: 'Solicitado' },
            { value: 'En proceso', label: 'En proceso' },
            { value: 'Listo', label: 'Listo' },
            { value: 'Entregado', label: 'Entregado' },
          ]}
        />
        <Select
          value={filtroPrioridad}
          onChange={setFiltroPrioridad}
          className="w-full md:w-44"
          options={[
            { value: 'todos', label: 'Toda prioridad' },
            { value: 'Normal', label: 'Normal' },
            { value: 'Alta', label: 'Alta' },
            { value: 'Urgente', label: 'Urgente' },
          ]}
        />
        <Button type="primary" onClick={() => setMostrarModalCrear(true)} className="md:shrink-0">
          Nuevo pedido
        </Button>
      </div>

      <p className="font-data text-[11px] uppercase tracking-[0.14em] text-silver-2 dark:text-[#8d8c85]">
        {pedidosFiltrados.length.toLocaleString('es-CO')} de {pedidos.length.toLocaleString('es-CO')} pedidos mostrados
      </p>

      <div className="sheet">
        {loading ? (
          <div className="p-6">
            <LoadingBlock />
          </div>
        ) : error ? (
          <div className="p-6">
            <ErrorBlock message={error} />
          </div>
        ) : (
          <Table<Pedido>
            rowKey="id"
            size="small"
            columns={columns}
            dataSource={pedidosFiltrados}
            pagination={{ pageSize: 10, showSizeChanger: false }}
            scroll={{ x: 900 }}
          />
        )}
      </div>

      <Modal
        title={`Pedido ${pedidoSeleccionado?.codigo ?? ''}`}
        open={!!pedidoSeleccionado}
        onCancel={() => setPedidoSeleccionado(null)}
        footer={<Button onClick={() => setPedidoSeleccionado(null)}>Cerrar</Button>}
      >
        {pedidoSeleccionado && (
          <div className="w-full space-y-2.5">
            <div className="flex justify-between text-sm">
              <span className="text-silver dark:text-[#8d8c85]">Cliente:</span>
              <b>{getNombreCliente(pedidoSeleccionado.cliente_id)}</b>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-silver dark:text-[#8d8c85]">Productos:</span>
              <span className="text-right max-w-64">{pedidoSeleccionado.productos}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-silver dark:text-[#8d8c85]">Cantidad:</span>
              <b className="font-data">{pedidoSeleccionado.cantidad_total} u.</b>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-silver dark:text-[#8d8c85]">Valor:</span>
              <b className="font-data">{COP(pedidoSeleccionado.valor)}</b>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-silver dark:text-[#8d8c85]">Prioridad:</span>
              <Tag color={PRIORIDAD_COLOR[pedidoSeleccionado.prioridad]}>{pedidoSeleccionado.prioridad}</Tag>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-silver dark:text-[#8d8c85]">Dirección:</span>
              <span className="text-xs text-right max-w-60">{pedidoSeleccionado.direccion_entrega}</span>
            </div>
            {pedidoSeleccionado.hash && (
              <div className="text-xs">
                <span className="text-silver dark:text-[#8d8c85]">Hash HMAC:</span>
                <p className="font-data text-[10px] break-all mt-1 bg-paper-2 dark:bg-negative-3 p-2 border border-hairline dark:border-[#2a2a26]">
                  {pedidoSeleccionado.hash}
                </p>
              </div>
            )}
            <div className="pt-2">
              <p className="spec-label mb-2">Cambiar estado</p>
              <Space wrap>
                {(['Solicitado', 'En proceso', 'Listo', 'Entregado'] as EstadoPedido[]).map((estado) => (
                  <Button
                    key={estado}
                    type={pedidoSeleccionado.estado === estado ? 'primary' : 'default'}
                    size="small"
                    onClick={() => handleCambiarEstado(pedidoSeleccionado.id, estado)}
                  >
                    {estado}
                  </Button>
                ))}
              </Space>
            </div>
          </div>
        )}
      </Modal>

      <Modal
        title={`Editar pedido ${pedidoEditando?.codigo ?? ''}`}
        open={!!pedidoEditando}
        onCancel={() => setPedidoEditando(null)}
        footer={null}
      >
        <Form
          form={formEditar}
          layout="vertical"
          onFinish={handleEditar}
        >
          <Form.Item label="Cliente solicitante" name="cliente_id" rules={[{ required: true, message: 'Elige un cliente' }]}>
            <Select
              showSearch
              optionFilterProp="label"
              options={clientes.map((c) => ({ value: c.id, label: `${c.nombre} (${c.tipo_cliente})` }))}
            />
          </Form.Item>
          <Form.Item label="Productos solicitados" name="productos" rules={[{ required: true, message: 'Describe los productos' }]}>
            <Input placeholder="Ej. Fotografías, Marcos" />
          </Form.Item>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <Form.Item label="Cantidad total" name="cantidad_total" rules={[{ required: true }]}>
              <InputNumber min={1} className="w-full" />
            </Form.Item>
            <Form.Item label="Prioridad" name="prioridad">
              <Select options={[{ value: 'Normal' }, { value: 'Alta' }, { value: 'Urgente' }]} />
            </Form.Item>
            <Form.Item label="Valor (COP)" name="valor">
              <InputNumber<number>
                min={0}
                step={1000}
                className="w-full"
                placeholder="Ej. 50.000"
                formatter={(v) =>
                  v !== undefined && v !== null
                    ? `$ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
                    : ''
                }
                parser={(display) =>
                  Number(
                    String(display ?? '')
                      .replace(/\$\s?/g, '')
                      .replace(/\./g, '')
                  )
                }
              />
            </Form.Item>
          </div>
          <Form.Item label="Dirección de entrega" name="direccion_entrega" rules={[{ required: true, message: 'Ingresa la dirección' }]}>
            <Input placeholder="Calle 50 #40-20, Centro, Medellín" />
          </Form.Item>
          <p className="text-[11px] text-silver dark:text-[#8d8c85] -mt-2 mb-4">
            Al guardar, el backend recalcula el hash HMAC del pedido con los nuevos datos.
          </p>
          <Form.Item className="!mb-0">
            <Space className="w-full justify-end">
              <Button onClick={() => setPedidoEditando(null)}>Cancelar</Button>
              <Button type="primary" htmlType="submit" loading={guardandoEdicion}>
                Guardar cambios
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Registrar nuevo pedido"
        open={mostrarModalCrear}
        onCancel={() => setMostrarModalCrear(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ prioridad: 'Normal' as PrioridadPedido, cantidad_total: 10 }}
          onFinish={handleCrearPedido}
        >
          <Form.Item label="Cliente solicitante" name="cliente_id" rules={[{ required: true, message: 'Elige un cliente' }]}>
            <Select
              showSearch
              optionFilterProp="label"
              options={clientes.map((c) => ({ value: c.id, label: `${c.nombre} (${c.tipo_cliente})` }))}
            />
          </Form.Item>
          <Form.Item label="Productos solicitados" name="productos" rules={[{ required: true, message: 'Describe los productos' }]}>
            <Input placeholder="Ej. Fotografías, Marcos" />
          </Form.Item>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <Form.Item label="Cantidad total" name="cantidad_total" rules={[{ required: true }]}>
              <InputNumber min={1} className="w-full" />
            </Form.Item>
            <Form.Item label="Prioridad" name="prioridad">
              <Select options={[{ value: 'Normal' }, { value: 'Alta' }, { value: 'Urgente' }]} />
            </Form.Item>
            <Form.Item label="Valor (COP)" name="valor">
              <InputNumber<number>
                min={0}
                step={1000}
                className="w-full"
                placeholder="Ej. 50.000"
                formatter={(v) =>
                  v !== undefined && v !== null
                    ? `$ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
                    : ''
                }
                parser={(display) =>
                  Number(
                    String(display ?? '')
                      .replace(/\$\s?/g, '')
                      .replace(/\./g, '')
                  )
                }
              />
            </Form.Item>
          </div>
          <Form.Item label="Dirección de entrega" name="direccion_entrega" rules={[{ required: true, message: 'Ingresa la dirección' }]}>
            <Input placeholder="Calle 50 #40-20, Centro, Medellín" />
          </Form.Item>
          <Form.Item className="!mb-0">
            <Space className="w-full justify-end">
              <Button onClick={() => setMostrarModalCrear(false)}>Cancelar</Button>
              <Button type="primary" htmlType="submit" loading={guardando}>
                Crear pedido
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
