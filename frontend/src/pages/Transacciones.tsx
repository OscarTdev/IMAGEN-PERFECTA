import React, { useEffect, useRef, useState } from 'react';
import { App as AntdApp, Button, Drawer, InputNumber, Select, Space, Table, Tabs, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  getAnomalias,
  revisarAnomalia,
  getDashboardSeg,
  getAppConfig,
  setAppConfig,
  getTransacciones,
} from '../services/api';
import type { Anomalia, AppConfig, DashboardSeguridad, TxnProfeRow, TxnVentana } from '../types';
import { ErrorBlock, LoadingBlock } from '../components/ui';
import {
  BarrasDistribucion,
  HeatmapHoras,
  SerieDiariaChart,
  StripEnVivo,
  TimelineVentana,
} from '../components/charts';

/* ─────────────────────────────────────────────────────────────────────
   DASHBOARD DE SEGURIDAD (PDF Appresso → Imagen Perfecta)

   Cada requisito está etiquetado en el código para verificación uno a uno:
     D1  Banda Hoy (10) │ Esta semana (50) │ Este mes (127)
     D2  Casos más recurrentes
     D3  Múltiples transacciones
     D4  Usuarios recurrentes
     D5  Total de transacciones (día/semana/mes)
     D6  Total de anomalías (día/semana/mes)
     D7  Porcentaje de transacciones con anomalías
     D8  Usuarios afectados
     D9  Valor total de transacciones sospechosas
     D10 Promedio de transacciones por usuario
     D11 Número de anomalías nuevas
     D12 Anomalías abiertas
     D13 Anomalías revisadas
     D14 Anomalías descartadas
     D15 Tendencias
     A1  Evolución temporal (horas con más anomalías, picos, periodos)
     A2  Anomalías por nivel
     A3  Línea de tiempo de una anomalía
     A4  Visualización de la ventana deslizante
     A5  Métodos de pago
     A6  Distribución por hora (intensidad = anomalías × horas)
   ───────────────────────────────────────────────────────────────────── */

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
  // REQUISITO A3: anomalía seleccionada para abrir su línea de tiempo
  const [anomaliaSelId, setAnomaliaSelId] = useState<number | null>(null);

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

  // ─── REQUISITO A4: monitoreo en vivo de la ventana deslizante ───
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
    if (seg >= manIni && seg <= manFin) return { nombre: 'manana', ventana: ventanas.manana };
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
        const total = segData.transacciones.total;
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

  // REQUISITOS D12-D14: revisión de anomalías (abierta → revisada / descartada)
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

  // REQUISITO A3: la anomalía seleccionada (se actualiza con cada refresco en vivo)
  const anomSel = anomaliaSelId != null ? anomalias.find((a) => a.id === anomaliaSelId) ?? null : null;

  // REQUISITO D4: usuarios recurrentes con detalle
  const recurrentes = seg?.usuarios_recurrentes ?? [];

  // REQUISITO A2: niveles en orden de gravedad
  const porNivel: Record<string, number> = {};
  ['critica', 'alta', 'media', 'baja'].forEach((n) => {
    const v = seg?.anomalias.por_nivel?.[n] ?? 0;
    if (v > 0) porNivel[n] = v;
  });

  // REQUISITO A1: hora del día con más anomalías (sobre la distribución por hora)
  const entradasHora = Object.entries(seg?.por_hora ?? {});
  const picoHora = entradasHora.reduce<[string, number] | null>(
    (best, [h, v]) => (!best || v > best[1] ? [h, v] : best),
    null
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

  // REQUISITO A3: columnas de las transacciones que formaron la ventana
  const columnasVentana: ColumnsType<TxnVentana> = [
    {
      title: 'idTxn',
      dataIndex: 'idTxn',
      key: 'idTxn',
      render: (v: number | string) => <span className="font-data text-[12px] font-bold">{v}</span>,
    },
    {
      title: 'Hora',
      dataIndex: 'fecha',
      key: 'fecha',
      render: (f: string) => (
        <span className="font-data text-[12px] text-silver dark:text-[#8d8c85]">
          {new Date(f).toLocaleTimeString('es-CO')}
        </span>
      ),
    },
    {
      title: 'Valor',
      dataIndex: 'valor',
      key: 'valor',
      render: (v: number) => <span className="font-data text-[12px]">{COP(v)}</span>,
    },
    { title: 'Método', dataIndex: 'metodo_pago', key: 'metodo_pago' },
  ];

  const valorVentanaSel =
    anomSel?.transacciones_ventana?.reduce((s, t) => s + (t.valor ?? 0), 0) ?? 0;

  return (
    <div className="max-w-6xl mx-auto space-y-10">
      {/* ── REQUISITO D1: banda de información agregada
          "Hoy (10) │ Esta semana (50) │ Este mes (127)"
          (transacciones y anomalías, REQUISITOS D5 y D6) ── */}
      <section className="grid grid-cols-3 border border-hairline dark:border-[#2a2a26] bg-paper dark:bg-negative-2">
        {[
          { label: 'Hoy', txn: seg?.transacciones.hoy ?? 0, anom: seg?.anomalias.hoy ?? 0 },
          { label: 'Esta semana', txn: seg?.transacciones.semana ?? 0, anom: seg?.anomalias.semana ?? 0 },
          { label: 'Este mes', txn: seg?.transacciones.mes ?? 0, anom: seg?.anomalias.mes ?? 0 },
        ].map((d, i) => (
          <div
            key={d.label}
            className={`px-5 py-4 ${i > 0 ? 'border-l border-hairline dark:border-[#2a2a26]' : ''}`}
          >
            <span className="spec-label">{d.label}</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="spec-value">{loading ? '···' : d.txn.toLocaleString('es-CO')}</span>
              <span className="font-data text-[10px] text-silver dark:text-[#8d8c85]">transacciones</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span
                className={`text-lg font-bold font-data ${
                  d.anom > 0 ? 'text-[#b91c1c]' : 'text-ink dark:text-[#f2f1ec]'
                }`}
              >
                {loading ? '···' : d.anom.toLocaleString('es-CO')}
              </span>
              <span className="font-data text-[10px] text-silver dark:text-[#8d8c85]">anomalías</span>
            </div>
          </div>
        ))}
      </section>

      {/* ── REQUISITOS D5, D7, D8, D9, D10, D11, D12, D13, D14:
          indicadores del dashboard de seguridad ── */}
      <section className="grid grid-cols-2 md:grid-cols-5 border border-hairline dark:border-[#2a2a26] bg-paper dark:bg-negative-2">
        {[
          // REQUISITO D5: total de transacciones recibidas
          { label: 'Transacciones', value: (seg?.transacciones.total ?? 0).toLocaleString('es-CO'), nota: 'recibidas en total' },
          // REQUISITO D7: porcentaje de transacciones con anomalías
          { label: 'Con anomalía', value: `${seg?.anomalias.porcentaje ?? 0}%`, nota: 'de las transacciones' },
          // REQUISITO D9: valor total de transacciones sospechosas
          { label: 'Valor sospechoso', value: COP(seg?.valor_sospechoso ?? 0), nota: 'en transacciones con anomalía' },
          // REQUISITO D8: usuarios afectados
          { label: 'Usuarios afectados', value: (seg?.clientes_afectados ?? 0).toLocaleString('es-CO'), nota: 'con al menos una anomalía' },
          // REQUISITO D4: usuarios recurrentes (≥ 2 anomalías)
          { label: 'Recurrentes', value: recurrentes.length.toLocaleString('es-CO'), nota: 'con ≥ 2 anomalías' },
          // REQUISITO D10: promedio de transacciones por usuario
          { label: 'Promedio por usuario', value: (seg?.promedio_por_usuario ?? 0).toLocaleString('es-CO'), nota: 'transacciones / usuario' },
          // REQUISITO D11: anomalías nuevas (hoy, sin revisar)
          { label: 'Nuevas', value: (seg?.anomalias.nuevas ?? 0).toLocaleString('es-CO'), nota: 'hoy, sin revisar' },
          // REQUISITO D12: anomalías abiertas
          { label: 'Abiertas', value: (seg?.anomalias.abiertas ?? 0).toLocaleString('es-CO'), nota: 'pendientes de revisión' },
          // REQUISITO D13: anomalías revisadas
          { label: 'Revisadas', value: (seg?.anomalias.revisadas ?? 0).toLocaleString('es-CO'), nota: 'cerradas por el taller' },
          // REQUISITO D14: anomalías descartadas
          { label: 'Descartadas', value: (seg?.anomalias.descartadas ?? 0).toLocaleString('es-CO'), nota: 'falsos positivos' },
        ].map((s, i) => (
          <div
            key={s.label}
            className={`px-5 py-4 ${i > 0 ? 'md:border-l md:border-hairline dark:md:border-[#2a2a26]' : ''} ${
              i >= 5 ? 'max-md:border-t max-md:border-hairline dark:max-md:border-[#2a2a26]' : ''
            } ${i % 5 !== 0 ? 'max-md:border-l max-md:border-hairline dark:max-md:border-[#2a2a26]' : ''}`}
          >
            <span className="spec-label">{s.label}</span>
            <span className="spec-value text-xl">{loading ? '···' : s.value}</span>
            <p className="text-[11px] text-silver dark:text-[#8d8c85] mt-1">{s.nota}</p>
          </div>
        ))}
      </section>

      {loading && <LoadingBlock rows={6} />}

      {error && <ErrorBlock message={error} />}

      {!loading && !error && (
        <>
          {/* ── REQUISITOS D2, D3, A2, A5, D4: casos más recurrentes,
              anomalías por nivel, métodos de pago y usuarios recurrentes ── */}
          <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {/* REQUISITO D2 (casos más recurrentes) + D3 (múltiples transacciones):
                conteo por tipo de anomalía; POSIBLE_FRAUDE = ráfaga en la ventana */}
            <div className="sheet p-5">
              <h3 className="text-sm font-bold mb-3">Casos más recurrentes</h3>
              <BarrasDistribucion
                datos={seg?.anomalias.por_tipo ?? {}}
                accentKeys={['POSIBLE_FRAUDE']}
                emptyText="Sin anomalías registradas todavía."
              />
            </div>
            {/* REQUISITO A2: anomalías por nivel */}
            <div className="sheet p-5">
              <h3 className="text-sm font-bold mb-3">Anomalías por nivel</h3>
              <BarrasDistribucion
                datos={porNivel}
                accentKeys={['critica', 'alta']}
                emptyText="Sin anomalías registradas todavía."
              />
            </div>
            {/* REQUISITO A5: métodos de pago de las transacciones */}
            <div className="sheet p-5">
              <h3 className="text-sm font-bold mb-3">Métodos de pago</h3>
              <BarrasDistribucion datos={seg?.por_metodo_pago ?? {}} emptyText="Sin transacciones todavía." />
            </div>
            {/* REQUISITO D4: detalle de usuarios recurrentes */}
            <div className="sheet p-5">
              <h3 className="text-sm font-bold mb-3">Usuarios recurrentes</h3>
              {recurrentes.length ? (
                <ul className="divide-y divide-hairline dark:divide-[#2a2a26]">
                  {recurrentes.slice(0, 8).map((u) => (
                    <li key={u.cliente_id} className="flex items-center justify-between gap-2 py-2">
                      <span className="font-data text-[11px] truncate" title={u.email}>
                        {u.email ?? `cliente #${u.cliente_id}`}
                      </span>
                      <span className="font-data text-[11px] font-bold shrink-0">
                        {u.anomalias} <span className="text-silver dark:text-[#8d8c85]">anomalías</span>
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-silver dark:text-[#8d8c85]">
                  Nadie acumula ≥ 2 anomalías todavía.
                </p>
              )}
            </div>
          </section>

          {/* ── REQUISITOS D15 + A1: evolución temporal (tendencias, picos
              repentinos y periodos de actividad de los últimos 14 días) ── */}
          <section className="sheet p-6">
            <div className="flex flex-wrap items-baseline justify-between gap-3 mb-4">
              <h3 className="text-sm font-bold">Evolución temporal</h3>
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-2 font-data text-[10px] uppercase tracking-[0.08em] text-silver dark:text-[#8d8c85]">
                  <span className="inline-block w-6 h-[2px] bg-ink dark:bg-[#f2f1ec]" />
                  transacciones
                </span>
                <span className="flex items-center gap-2 font-data text-[10px] uppercase tracking-[0.08em] text-[#b91c1c]">
                  <span className="inline-block w-6 border-t-2 border-dashed border-[#b91c1c]" />
                  anomalías
                </span>
              </div>
            </div>
            <SerieDiariaChart data={seg?.serie_diaria ?? []} />
          </section>

          {/* ── REQUISITO A6: distribución por hora — la intensidad representa
              la cantidad de anomalías por hora (0-23) ── */}
          <section className="sheet p-6">
            <div className="flex flex-wrap items-baseline justify-between gap-3 mb-4">
              <h3 className="text-sm font-bold">Distribución por hora</h3>
              <p className="font-data text-[11px] text-silver dark:text-[#8d8c85]">
                {picoHora && picoHora[1] > 0
                  ? `Hora pico: ${String(picoHora[0]).padStart(2, '0')}:00 · ${picoHora[1]} anomalía${picoHora[1] === 1 ? '' : 's'}`
                  : 'Sin anomalías para distribuir por hora.'}
              </p>
            </div>
            <HeatmapHoras porHora={seg?.por_hora ?? {}} />
          </section>

          {/* ── REQUISITO A4: ventana deslizante configurable por turno (PDF) ── */}
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

          {/* ── REQUISITO A4: monitoreo en vivo — la ventana deslizante
              dibujada sobre las últimas transacciones recibidas ── */}
          {(() => {
            const turno = turnoActual();
            return (
              <div
                className={`sheet px-4 py-3 flex flex-col gap-3 transition-colors ${
                  enVivo ? 'border-ink dark:border-[#f2f1ec]' : ''
                }`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
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
                    {enVivo
                      ? `${nuevas} nueva${nuevas === 1 ? '' : 's'} esta sesión`
                      : 'esperando transacciones…'}
                  </span>
                </div>
                {transacciones.length ? (
                  <StripEnVivo
                    txns={transacciones.slice(0, 60)}
                    ventanaSeg={turno.ventana}
                    umbral={umbral}
                  />
                ) : (
                  <p className="font-data text-[11px] text-silver dark:text-[#8d8c85]">
                    La ventana deslizante se dibujará aquí con la primera transacción recibida.
                  </p>
                )}
              </div>
            );
          })()}

          {/* ── Registro: transacciones recibidas y anomalías ── */}
          <section>
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
                      <div className="flex flex-wrap items-center justify-end gap-3 mt-3 mb-3">
                        {/* REQUISITOS D12-D14: filtro por estado de revisión */}
                        <span className="font-data text-[11px] text-silver dark:text-[#8d8c85] mr-auto">
                          Haz clic en una anomalía para ver su línea de tiempo (ventana deslizante).
                        </span>
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
                          rowClassName={() => 'cursor-pointer'}
                          onRow={(r) => ({ onClick: () => setAnomaliaSelId(r.id) })}
                        />
                      </div>
                    </>
                  ),
                },
              ]}
            />
          </section>
        </>
      )}

      {/* ── REQUISITO A3: línea de tiempo de UNA anomalía (drawer) ── */}
      <Drawer
        title={anomSel ? `Anomalía #${anomSel.id} · ${anomSel.tipo}` : ''}
        open={!!anomSel}
        onClose={() => setAnomaliaSelId(null)}
        size={720}
      >
        {anomSel && (
          <div className="space-y-6">
            {/* Especificaciones de la anomalía */}
            <div className="grid grid-cols-2 md:grid-cols-3 border border-hairline dark:border-[#2a2a26] bg-paper dark:bg-negative-2">
              {[
                { label: 'Nivel', node: <Tag color={NIVEL_COLOR[anomSel.nivel] ?? 'default'}>{anomSel.nivel}</Tag> },
                { label: 'Revisión', node: <Tag>{anomSel.estado_revision}</Tag> },
                { label: 'Ventana', node: <span className="font-data text-sm font-bold">{anomSel.ventana_segundos}s</span> },
                { label: 'En ventana', node: <span className="font-data text-sm font-bold">{anomSel.cantidad_transacciones} tx</span> },
                { label: 'Umbral', node: <span className="font-data text-sm font-bold">{umbral}</span> },
                ...(anomSel.transacciones_ventana?.length
                  ? [{ label: 'Valor en ventana', node: <span className="font-data text-sm font-bold">{COP(valorVentanaSel)}</span> }]
                  : []),
              ].map((c, i) => (
                <div
                  key={c.label}
                  className={`px-4 py-3 ${i > 0 ? 'border-l border-hairline dark:border-[#2a2a26]' : ''}`}
                >
                  <span className="spec-label">{c.label}</span>
                  <div className="mt-1">{c.node}</div>
                </div>
              ))}
            </div>

            {anomSel.detalle && (
              <p className="font-data text-xs text-silver dark:text-[#8d8c85]">{anomSel.detalle}</p>
            )}

            {/* REQUISITO A3: la ventana deslizante con las transacciones que formaron la anomalía */}
            <div>
              <h4 className="text-sm font-bold mb-2">Línea de tiempo de la ventana deslizante</h4>
              {anomSel.transacciones_ventana?.length ? (
                <TimelineVentana
                  txs={anomSel.transacciones_ventana}
                  ventanaSeg={anomSel.ventana_segundos}
                  umbral={umbral}
                />
              ) : (
                <p className="text-xs text-silver dark:text-[#8d8c85]">
                  Esta anomalía se registró antes de la línea de tiempo persistida; el detalle
                  disponible es el texto de detección.
                </p>
              )}
            </div>

            {/* Transacciones de la ventana (REQUISITO A3, tabla de detalle) */}
            {anomSel.transacciones_ventana?.length ? (
              <div>
                <h4 className="text-sm font-bold mb-2">Transacciones en la ventana</h4>
                <Table<TxnVentana>
                  rowKey={(r) => String(r.idTxn)}
                  size="small"
                  columns={columnasVentana}
                  dataSource={anomSel.transacciones_ventana}
                  pagination={false}
                />
              </div>
            ) : null}

            {/* REQUISITOS D12-D14: acciones de revisión dentro del detalle */}
            {anomSel.estado_revision === 'abierta' && (
              <Space>
                <Button type="primary" onClick={() => handleRevisar(anomSel.id, 'revisada')}>
                  Marcar revisada
                </Button>
                <Button onClick={() => handleRevisar(anomSel.id, 'descartada')}>Descartar</Button>
              </Space>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};
