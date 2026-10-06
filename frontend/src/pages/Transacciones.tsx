import React, { useEffect, useRef, useState } from 'react';
import { App as AntdApp, Button, InputNumber, Select, Space, Table, Tabs, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  getAnomalias,
  revisarAnomalia,
  getDashboardSeg,
  getAppConfig,
  setAppConfig,
  getTransacciones,
} from '../services/api';
import type { Anomalia, DashboardSeguridad, AppConfig, TxnProfeRow } from '../types';
import { ErrorBlock, LoadingBlock } from '../components/ui';

const COP = (v: number) =>
  v.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });

const NIVEL_COLOR: Record<string, string> = {
  critica: 'error',
  alta: 'warning',
  media: 'default',
  baja: 'default',
};

export const Transacciones: React.FC = () => {
  const { message, notification } = AntdApp.useApp();
  const [transacciones, setTransacciones] = useState<TxnProfeRow[]>([]);
  const [anomalias, setAnomalias] = useState<Anomalia[]>([]);
  const [seg, setSeg] = useState<DashboardSeguridad | null>(null);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtroEstado, setFiltroEstado] = useState<string>('todas');
  const [guardandoConfig, setGuardandoConfig] = useState(false);
  const [ventanas, setVentanas] = useState({ manana: 10, tarde: 6, noche: 3 });
  const [umbral, setUmbral] = useState(3);

  const cargar = () => {
    setLoading(true);
    setError(null);
    Promise.all([getTransacciones(), getAnomalias(), getDashboardSeg(), getAppConfig()])
      .then(([txns, anomaliasData, segData, configData]) => {
        setTransacciones(txns);
        setAnomalias(anomaliasData);
        setSeg(segData);
        setConfig(configData);
        setVentanas(configData.ventanas_turno);
        setUmbral(configData.umbral_transacciones);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    cargar();
  }, []);

  // ─── Monitoreo en vivo: la ventana deslizante visible mientras llegan registros ───
  const [enVivo, setEnVivo] = useState(false);
  const [nuevas, setNuevas] = useState(0);
  const prevTotal = useRef<number | null>(null);
  const enVivoRef = useRef(false);
  const establesRef = useRef(0);
  const basePedidos = useRef(0);
  const baseAnomalias = useRef(0);

  const turnoActual = () => {
    const ahora = new Date();
    const seg = ahora.getHours() * 3600 + ahora.getMinutes() * 60 + ahora.getSeconds();
    const manIni = 5 * 3600 + 1;
    const manFin = 12 * 3600;
    const tarIni = 12 * 3600 + 1;
    const tarFin = 20 * 3600;
    if (seg >= manIni && seg <= manFin) return { nombre: 'mañana', ventana: ventanas.manana };
    if (seg >= tarIni && seg <= tarFin) return { nombre: 'tarde', ventana: ventanas.tarde };
    return { nombre: 'noche', ventana: ventanas.noche };
  };

  useEffect(() => {
    const tick = window.setInterval(async () => {
      try {
        const [txns, segData, anomData] = await Promise.all([
          getTransacciones(),
          getDashboardSeg(),
          getAnomalias(),
        ]);
        setTransacciones(txns);
        setSeg(segData);
        setAnomalias(anomData);
        const total = segData.pedidos.total;
        const anomTotal = segData.anomalias.total;
        if (prevTotal.current !== null) {
          if (total > prevTotal.current) {
            if (!enVivoRef.current) {
              enVivoRef.current = true;
              basePedidos.current = prevTotal.current;
              baseAnomalias.current = anomTotal;
            }
            establesRef.current = 0;
            setEnVivo(true);
            setNuevas(total - basePedidos.current);
          } else if (enVivoRef.current) {
            establesRef.current += 1;
            if (establesRef.current >= 2) {
              enVivoRef.current = false;
              setEnVivo(false);
              const procesadas = total - basePedidos.current;
              const anomalasNuevas = anomTotal - baseAnomalias.current;
              notification.success({
                message: 'Carga de transacciones completada',
                description: `${procesadas} transacciones procesadas en vivo · ${anomalasNuevas} anomalía${anomalasNuevas === 1 ? '' : 's'} detectada${anomalasNuevas === 1 ? '' : 's'} por la ventana deslizante.`,
                placement: 'bottomRight',
                duration: 8,
              });
            }
          }
        }
        prevTotal.current = total;
      } catch {
        /* el siguiente tick reintenta */
      }
    }, 2500);
    return () => window.clearInterval(tick);
  }, [notification]);

  const handleRevisar = async (id: number, estado: string) => {
    try {
      await revisarAnomalia(id, estado);
      message.success(`Anomalía #${id} → ${estado}`);
      cargar();
    } catch (err) {
      message.error(`Error al revisar: ${err instanceof Error ? err.message : 'desconocido'}`);
    }
  };

  const handleGuardarConfig = async () => {
    setGuardandoConfig(true);
    try {
      const actualizada = await setAppConfig({
        ventana_segundos: ventanas.noche,
        umbral_transacciones: umbral,
        ventanas_turno: ventanas,
      });
      setConfig(actualizada);
      message.success('Configuración de ventana deslizante actualizada');
    } catch (err) {
      message.error(`Error al guardar: ${err instanceof Error ? err.message : 'desconocido'}`);
    } finally {
      setGuardandoConfig(false);
    }
  };

  const anomaliasFiltradas = anomalias.filter(
    (a) => filtroEstado === 'todas' || a.estado_revision === filtroEstado
  );

  const columnasTxn: ColumnsType<TxnProfeRow> = [
    {
      title: 'idTxn',
      dataIndex: 'idTxn',
      key: 'idTxn',
      render: (v: number | string) => <span className="font-data font-bold text-[12px]">{v}</span>,
    },
    {
      title: 'Usuario',
      dataIndex: 'user',
      key: 'user',
      render: (u: string) => <span className="font-data text-[12px]">{u}</span>,
    },
    {
      title: 'Fecha',
      dataIndex: 'date',
      key: 'date',
      render: (d: string) => (
        <span className="font-data text-[12px] text-silver dark:text-[#8d8c85]">
          {new Date(d).toLocaleString('es-CO')}
        </span>
      ),
      sorter: (a, b) => +new Date(a.date) - +new Date(b.date),
      defaultSortOrder: 'descend',
    },
    {
      title: 'Valor',
      dataIndex: 'value',
      key: 'value',
      render: (v: number) => <span className="font-data text-[12px]">{COP(v)}</span>,
      sorter: (a, b) => a.value - b.value,
    },
    { title: 'Pago', dataIndex: 'paymentMethod', key: 'paymentMethod' },
    {
      title: 'Pedido',
      dataIndex: 'codigo',
      key: 'codigo',
      render: (c?: string) => (
        <span className="font-data text-[12px] font-bold">{c ?? '—'}</span>
      ),
    },
    {
      title: 'Hash',
      dataIndex: 'hash',
      key: 'hash',
      ellipsis: true,
      render: (h?: string | null) => (
        <span
          className="font-data text-[11px] text-silver dark:text-[#8d8c85]"
          title={h ?? undefined}
        >
          {h ? `${h.slice(0, 12)}…` : '—'}
        </span>
      ),
    },
  ];

  const columnasAnomalia: ColumnsType<Anomalia> = [
    {
      title: '#',
      dataIndex: 'id',
      key: 'id',
      width: 60,
      render: (id: number) => (
        <span className="font-data text-[12px] text-silver dark:text-[#8d8c85]">{id}</span>
      ),
    },
    {
      title: 'Tipo',
      dataIndex: 'tipo',
      key: 'tipo',
      render: (t: string) => <span className="font-data text-[12px] font-bold">{t}</span>,
    },
    {
      title: 'Nivel',
      dataIndex: 'nivel',
      key: 'nivel',
      render: (n: string) => <Tag color={NIVEL_COLOR[n] ?? 'default'}>{n}</Tag>,
    },
    {
      title: 'Ventana',
      dataIndex: 'ventana_segundos',
      key: 'ventana_segundos',
      render: (v: number, r: Anomalia) => (
        <span className="font-data text-[12px] text-silver dark:text-[#8d8c85]">
          {v}s{r.cantidad_transacciones ? ` · ${r.cantidad_transacciones} tx` : ''}
        </span>
      ),
    },
    {
      title: 'Detalle',
      dataIndex: 'detalle',
      key: 'detalle',
      ellipsis: true,
    },
    {
      title: 'Revisión',
      dataIndex: 'estado_revision',
      key: 'estado_revision',
      render: (e: string) => <Tag>{e}</Tag>,
    },
    {
      title: '',
      key: 'acciones',
      align: 'right',
      render: (_, r) => (
        <Space size="small">
          {r.estado_revision === 'abierta' && (
            <>
              <Button type="link" size="small" onClick={() => handleRevisar(r.id, 'revisada')}>
                Revisada
              </Button>
              <Button type="link" size="small" onClick={() => handleRevisar(r.id, 'descartada')}>
                Descartar
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-10">
      {/* Especificaciones del detector */}
      <section className="grid grid-cols-2 md:grid-cols-4 border border-hairline dark:border-[#2a2a26] bg-paper dark:bg-negative-2">
        {[
          { label: 'Transacciones', value: (seg?.pedidos.total ?? 0).toLocaleString('es-CO'), nota: 'pedidos procesados' },
          { label: 'Anomalías', value: (seg?.anomalias.abiertas ?? 0).toLocaleString('es-CO'), nota: 'abiertas por revisar' },
          { label: 'Con anomalía', value: `${seg?.anomalias.porcentaje ?? 0}%`, nota: 'de los pedidos' },
          { label: 'Valor sospechoso', value: COP(seg?.valor_sospechoso ?? 0), nota: `${seg?.clientes_afectados ?? 0} clientes afectados` },
        ].map((s, i) => (
          <div
            key={s.label}
            className={`px-5 py-4 ${i > 0 ? 'md:border-l md:border-hairline dark:md:border-[#2a2a26]' : ''} ${
              i >= 2 ? 'max-md:border-t max-md:border-hairline dark:max-md:border-[#2a2a26]' : ''
            } ${i === 2 ? 'max-md:border-l-0' : ''}`}
          >
            <span className="spec-label">{s.label}</span>
            <span className="spec-value text-xl">{loading ? '···' : s.value}</span>
            <p className="text-[11px] text-silver dark:text-[#8d8c85] mt-1">{s.nota}</p>
          </div>
        ))}
      </section>

      {/* Ventana deslizante configurable por turno (PDF) */}
      <section className="sheet p-6">
        <h3 className="text-sm font-bold mb-1">Ventana deslizante por turno</h3>
        <p className="text-xs text-silver dark:text-[#8d8c85] mb-4 max-w-[70ch]">
          El detector marca POSIBLE_FRAUDE cuando un mismo cliente acumula {umbral} o más
          transacciones dentro de la ventana de su turno, y HASH_INVALIDO cuando el hash HMAC
          recibido no coincide con el calculado. Valores en segundos, configurables sin reescribir código.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl">
          <div>
            <span className="spec-label">Mañana (05:00–12:00)</span>
            <InputNumber
              min={1}
              value={ventanas.manana}
              onChange={(v) => setVentanas((x) => ({ ...x, manana: v ?? 1 }))}
              className="w-full mt-1"
            />
          </div>
          <div>
            <span className="spec-label">Tarde (12:00–20:00)</span>
            <InputNumber
              min={1}
              value={ventanas.tarde}
              onChange={(v) => setVentanas((x) => ({ ...x, tarde: v ?? 1 }))}
              className="w-full mt-1"
            />
          </div>
          <div>
            <span className="spec-label">Noche (20:00–05:00)</span>
            <InputNumber
              min={1}
              value={ventanas.noche}
              onChange={(v) => setVentanas((x) => ({ ...x, noche: v ?? 1 }))}
              className="w-full mt-1"
            />
          </div>
          <div>
            <span className="spec-label">Umbral (transacciones)</span>
            <InputNumber
              min={2}
              value={umbral}
              onChange={(v) => setUmbral(v ?? 2)}
              className="w-full mt-1"
            />
          </div>
        </div>
        <Button
          type="primary"
          className="mt-4"
          loading={guardandoConfig}
          onClick={handleGuardarConfig}
          disabled={
            !!config &&
            JSON.stringify(config.ventanas_turno) === JSON.stringify(ventanas) &&
            config.umbral_transacciones === umbral
          }
        >
          Guardar configuración
        </Button>
      </section>

      {/* Monitoreo en vivo: la ventana deslizante visible mientras llegan registros */}
      {(() => {
        const turno = turnoActual();
        return (
          <div
            className={`sheet px-4 py-3 flex flex-wrap items-center justify-between gap-2 transition-colors ${
              enVivo ? 'border-ink dark:border-[#f2f1ec]' : ''
            }`}
          >
            <div className="flex items-center gap-3">
              <span
                className={`w-2 h-2 rounded-full ${
                  enVivo ? 'bg-[#b91c1c] animate-pulse' : 'bg-hairline dark:bg-[#3a3a35]'
                }`}
              />
              <span className="text-[13px] font-semibold">
                {enVivo ? 'Recibiendo transacciones en vivo…' : 'Monitoreo en vivo activo'}
              </span>
              <span className="font-data text-[11px] text-silver dark:text-[#8d8c85]">
                turno {turno.nombre} · ventana {turno.ventana}s · umbral {umbral}
              </span>
            </div>
            <span className="font-data text-[11px] text-silver dark:text-[#8d8c85]">
              {enVivo ? `${nuevas} nueva${nuevas === 1 ? '' : 's'} esta sesión` : 'esperando transacciones…'}
            </span>
          </div>
        );
      })()}

      {/* Registro: transacciones recibidas y anomalías */}
      <section>
        {loading ? (
          <LoadingBlock rows={6} />
        ) : error ? (
          <ErrorBlock message={error} />
        ) : (
          <Tabs
            items={[
              {
                key: 'transacciones',
                label: `Transacciones recibidas (${transacciones.length})`,
                children: (
                  <div className="sheet mt-3">
                    <Table<TxnProfeRow>
                      rowKey={(r) => r.codigo ?? `txn-${r.idTxn}`}
                      size="small"
                      columns={columnasTxn}
                      dataSource={transacciones}
                      pagination={{ pageSize: 10, showSizeChanger: false }}
                      scroll={{ x: 860 }}
                      locale={{
                        emptyText:
                          'Sin transacciones del profesor todavía. Envía POST /api/transacciones o /api/transacciones/lote.',
                      }}
                    />
                  </div>
                ),
              },
              {
                key: 'anomalias',
                label: `Anomalías (${anomaliasFiltradas.length.toLocaleString('es-CO')})`,
                children: (
                  <>
                    <div className="flex items-center justify-end mt-3 mb-3">
                      <Select
                        value={filtroEstado}
                        onChange={setFiltroEstado}
                        className="w-40"
                        options={[
                          { value: 'todas', label: 'Todas' },
                          { value: 'abierta', label: 'Abiertas' },
                          { value: 'revisada', label: 'Revisadas' },
                          { value: 'descartada', label: 'Descartadas' },
                        ]}
                      />
                    </div>
                    <div className="sheet">
                      <Table<Anomalia>
                        rowKey="id"
                        size="small"
                        columns={columnasAnomalia}
                        dataSource={anomaliasFiltradas.slice(0, 200)}
                        pagination={{ pageSize: 10, showSizeChanger: false }}
                        scroll={{ x: 800 }}
                        locale={{ emptyText: 'No hay anomalías registradas.' }}
                      />
                    </div>
                  </>
                ),
              },
            ]}
          />
        )}
      </section>
    </div>
  );
};
