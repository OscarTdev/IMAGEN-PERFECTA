import React, { useEffect, useState } from 'react';
import { Alert, Skeleton, Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { ArrowRight } from '../components/Icons';
import { getPedidos, getDashboardSeg } from '../services/api';
import type { Pedido, DashboardSeguridad } from '../types';
import type { TabType } from '../components/Sidebar';

interface DashboardProps {
  onNavigate: (tab: TabType) => void;
}

const ESTADO_COLOR: Record<string, string> = {
  Solicitado: 'default',
  'En proceso': 'processing',
  Listo: 'warning',
  Entregado: 'success',
};

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [seg, setSeg] = useState<DashboardSeguridad | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getPedidos(), getDashboardSeg()])
      .then(([pedidosData, segData]) => {
        setPedidos(pedidosData);
        setSeg(segData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      });
  }, []);

  const total = pedidos.length;
  const enProceso = pedidos.filter((p) => p.estado === 'En proceso').length;
  const entregados = pedidos.filter((p) => p.estado === 'Entregado').length;
  const pendientes = pedidos.filter(
    (p) => p.estado === 'Solicitado' || p.estado === 'Listo'
  ).length;
  const anomaliasAbiertas = seg?.anomalias.abiertas ?? 0;

  const recientes = [...pedidos]
    .sort((a, b) => +new Date(b.fecha) - +new Date(a.fecha))
    .slice(0, 8);

  const columns: ColumnsType<Pedido> = [
    {
      title: 'Código',
      dataIndex: 'codigo',
      key: 'codigo',
      render: (c: string) => <span className="font-data font-bold text-[12px]">{c}</span>,
    },
    { title: 'Productos', dataIndex: 'productos', key: 'productos', ellipsis: true },
    {
      title: 'Estado',
      dataIndex: 'estado',
      key: 'estado',
      render: (e: string) => <Tag color={ESTADO_COLOR[e]}>{e}</Tag>,
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
    },
  ];

  const acciones: { label: string; tab: TabType; nota: string }[] = [
    { label: 'Registrar y atender pedidos', tab: 'pedidos', nota: 'Código IP-XXXX, prioridad y estados' },
    { label: 'Planear entregas del día', tab: 'rutas', nota: 'Dijkstra por zonas y combustible' },
    { label: 'Vigilar transacciones', tab: 'transacciones', nota: `${anomaliasAbiertas} anomalías abiertas` },
    { label: 'Ver producción', tab: 'produccion', nota: 'Turno FIFO y cola prioritaria' },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-10">
      {/* Banda de especificaciones del día */}
      <section className="grid grid-cols-2 md:grid-cols-5 border border-hairline dark:border-[#2a2a26] bg-paper dark:bg-negative-2">
        {[
          { label: 'Pedidos', value: total, nota: 'total registrados' },
          { label: 'En proceso', value: enProceso, nota: 'imprimiendo o enmarcando' },
          { label: 'Entregados', value: entregados, nota: 'completados' },
          { label: 'Pendientes', value: pendientes, nota: 'solicitados o listos' },
          { label: 'Anomalías', value: anomaliasAbiertas, nota: 'abiertas por revisar' },
        ].map((s, i) => (
          <div
            key={s.label}
            className={`px-5 py-4 ${i > 0 ? 'border-l border-hairline dark:border-[#2a2a26]' : ''} ${
              i >= 2 ? 'max-md:border-t max-md:border-hairline dark:max-md:border-[#2a2a26]' : ''
            } ${i === 2 || i === 4 ? 'max-md:border-l-0' : ''}`}
          >
            <span className="spec-label">{s.label}</span>
            <span className="spec-value">
              {loading ? '···' : s.value.toLocaleString('es-CO')}
            </span>
            <p className="text-[11px] text-silver-2 dark:text-[#8d8c85] mt-1">{s.nota}</p>
          </div>
        ))}
      </section>

      {loading && <Skeleton active paragraph={{ rows: 4}} />}

      {error && (
        <Alert
          type="error"
          showIcon
          message="No se pudo conectar con la API"
          description={`Verifica que el backend FastAPI esté corriendo en el puerto 8000. Detalle: ${error}`}
        />
      )}

      {/* Mesa de pedidos recientes */}
      {!loading && !error && (
        <section>
          <div className="flex items-baseline justify-between mb-3">
            <h3 className="text-sm font-bold text-ink dark:text-[#f2f1ec]">Pedidos recientes</h3>
            <button
              onClick={() => onNavigate('pedidos')}
              className="text-xs font-semibold text-ink dark:text-[#f2f1ec] underline underline-offset-4 decoration-hairline dark:decoration-[#3a3a35] hover:decoration-ink dark:hover:decoration-[#f2f1ec] transition-colors"
            >
              Ver todos los pedidos
            </button>
          </div>
          <div className="sheet">
            <Table<Pedido>
              rowKey="id"
              size="small"
              columns={columns}
              dataSource={recientes}
              pagination={false}
            />
          </div>
        </section>
      )}

      {/* Accesos del taller como índice de hoja técnica */}
      {!loading && !error && (
        <section>
          <h3 className="text-sm font-bold text-ink dark:text-[#f2f1ec] mb-3">Ir a</h3>
          <div className="border-t border-hairline dark:border-[#2a2a26]">
            {acciones.map((a) => (
              <button
                key={a.label}
                onClick={() => onNavigate(a.tab)}
                className="w-full group flex items-center justify-between px-1 py-3.5 border-b border-hairline dark:border-[#2a2a26] text-left hover:px-2 transition-all"
              >
                <span>
                  <span className="text-[13px] font-semibold text-ink dark:text-[#f2f1ec]">
                    {a.label}
                  </span>
                  <span className="font-data text-[11px] text-silver-2 dark:text-[#8d8c85] ml-3">
                    {a.nota}
                  </span>
                </span>
                <ArrowRight className="w-4 h-4 text-silver-2 dark:text-[#8d8c85] group-hover:text-ink dark:group-hover:text-[#f2f1ec] group-hover:translate-x-1 transition-all" />
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
