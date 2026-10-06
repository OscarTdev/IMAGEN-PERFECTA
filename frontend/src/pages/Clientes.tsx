import React, { useEffect, useMemo, useState } from 'react';
import { App as AntdApp, Button, Form, Input, Select, Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { getClientes, createCliente } from '../services/api';
import type { Cliente, TipoCliente } from '../types';
import { ErrorBlock, LoadingBlock } from '../components/ui';

export const Clientes: React.FC = () => {
  const { message } = AntdApp.useApp();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [filtro, setFiltro] = useState('');
  const [form] = Form.useForm();

  const cargarClientes = () => {
    setLoading(true);
    setError(null);
    getClientes()
      .then((data) => {
        setClientes(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    cargarClientes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCrear = async (values: { nombre: string; telefono: string; tipo_cliente: TipoCliente }) => {
    setGuardando(true);
    try {
      await createCliente({
        nombre: values.nombre.trim(),
        telefono: values.telefono.trim(),
        tipo_cliente: values.tipo_cliente,
      });
      message.success('Cliente registrado');
      form.resetFields();
      cargarClientes();
    } catch (err) {
      message.error(`Error al crear cliente: ${err instanceof Error ? err.message : 'desconocido'}`);
    } finally {
      setGuardando(false);
    }
  };

  const clientesFiltrados = useMemo(
    () =>
      clientes.filter(
        (c) =>
          c.nombre.toLowerCase().includes(filtro.toLowerCase()) ||
          c.tipo_cliente.toLowerCase().includes(filtro.toLowerCase()) ||
          c.telefono.includes(filtro)
      ),
    [clientes, filtro]
  );

  const columns: ColumnsType<Cliente> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 64,
      render: (id: number) => <span className="font-data text-[12px] text-silver dark:text-[#8d8c85]">#{id}</span>,
      sorter: (a, b) => a.id - b.id,
    },
    { title: 'Nombre', dataIndex: 'nombre', key: 'nombre', sorter: (a, b) => a.nombre.localeCompare(b.nombre) },
    {
      title: 'Contacto',
      key: 'contacto',
      render: (_, r) => (
        <span className="font-data text-[12px]">
          {r.telefono}
          {r.email ? <span className="text-silver-2 dark:text-[#8d8c85]"> · {r.email}</span> : null}
        </span>
      ),
    },
    {
      title: 'Tipo',
      dataIndex: 'tipo_cliente',
      key: 'tipo_cliente',
      render: (tipo: TipoCliente) => <Tag>{tipo}</Tag>,
      filters: [
        { text: 'Fotógrafo', value: 'Fotógrafo' },
        { text: 'Aficionado', value: 'Aficionado' },
        { text: 'Nuevo cliente', value: 'Nuevo cliente' },
      ],
      onFilter: (v, r) => r.tipo_cliente === v,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Ficha de registro */}
        <section className="sheet h-fit p-5">
          <h3 className="text-sm font-bold mb-4">Registrar cliente</h3>
          <Form
            form={form}
            layout="vertical"
            initialValues={{ tipo_cliente: 'Fotógrafo' as TipoCliente }}
            onFinish={handleCrear}
          >
            <Form.Item
              label="Nombre completo"
              name="nombre"
              rules={[{ required: true, message: 'Ingresa el nombre' }]}
            >
              <Input placeholder="Ej. Mateo Gómez" />
            </Form.Item>
            <Form.Item
              label="Teléfono"
              name="telefono"
              rules={[{ required: true, message: 'Ingresa el teléfono' }]}
            >
              <Input placeholder="301 234 5678" />
            </Form.Item>
            <Form.Item label="Tipo de cliente" name="tipo_cliente">
              <Select
                options={[
                  { value: 'Fotógrafo', label: 'Fotógrafo profesional' },
                  { value: 'Aficionado', label: 'Aficionado' },
                  { value: 'Nuevo cliente', label: 'Nuevo cliente' },
                ]}
              />
            </Form.Item>
            <Button type="primary" htmlType="submit" loading={guardando} block>
              Guardar cliente
            </Button>
          </Form>
        </section>

        {/* Directorio */}
        <section className="lg:col-span-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
            <h3 className="text-sm font-bold">
              Directorio ({clientesFiltrados.length.toLocaleString('es-CO')})
            </h3>
            <div className="flex gap-2">
              <Input.Search
                placeholder="Nombre, tipo o teléfono…"
                value={filtro}
                onChange={(e) => setFiltro(e.target.value)}
                allowClear
                className="w-full sm:w-60"
              />
              <Button onClick={cargarClientes}>Actualizar</Button>
            </div>
          </div>
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
              <Table<Cliente>
                rowKey="id"
                size="small"
                columns={columns}
                dataSource={clientesFiltrados}
                pagination={{ pageSize: 10, showSizeChanger: false }}
                locale={{ emptyText: 'No se encontraron clientes coincidentes.' }}
              />
            )}
          </div>
        </section>
      </div>
    </div>
  );
};
