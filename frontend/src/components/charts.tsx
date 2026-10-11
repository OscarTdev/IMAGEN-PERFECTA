/* Gráficas SVG propias del mundo monocromo (ficha de impresión).
   Sin dependencias. El color rojo #b91c1c es el único acento funcional
   (riesgo), igual que el punto del monitoreo en vivo.

   Requisitos cubiertos (uno a uno, PDF Appresso → Imagen Perfecta):
     D15 Tendencias · A1  Evolución temporal (picos, periodos)   → SerieDiariaChart
     A6  Distribución por hora (intensidad anomalías × horas)   → HeatmapHoras
     D2  Casos más recurrentes · D3 Múltiples transacciones      → BarrasDistribucion (por tipo)
     A2  Anomalías por nivel                                    → BarrasDistribucion (por nivel)
     A5  Métodos de pago                                         → BarrasDistribucion (por método)
     A3  Línea de tiempo de una anomalía                         → TimelineVentana
     A4  Visualización de la ventana deslizante                  → StripEnVivo */
import React from 'react';
import type { PuntoDiario, TxnProfeRow, TxnVentana } from '../types';

const hhmmss = (ms: number) => new Date(ms).toLocaleTimeString('es-CO', { hour12: false });

/* ── REQUISITOS D15 + A1: Evolución temporal de 14 días (transacciones vs
   anomalías): tendencias, picos repentinos y periodos de actividad ── */
export const SerieDiariaChart: React.FC<{ data: PuntoDiario[] }> = ({ data }) => {
  const W = 640;
  const H = 240;
  const padL = 40;
  const padR = 16;
  const padT = 24;
  const padB = 30;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;
  const n = data.length;
  if (!n) return null;

  const rawMax = Math.max(...data.map((d) => Math.max(d.transacciones, d.anomalias)), 0);
  const maxY = Math.max(4, Math.ceil((rawMax * 1.15) / 2) * 2);
  const x = (i: number) => padL + (n > 1 ? (i * innerW) / (n - 1) : innerW / 2);
  const y = (v: number) => padT + (1 - v / maxY) * innerH;

  const ptsTxn = data.map((d, i) => `${x(i)},${y(d.transacciones)}`).join(' ');
  const areaTxn = `${padL},${y(0)} ${ptsTxn} ${x(n - 1)},${y(0)}`;
  const iPico = data.reduce((best, d, i) => (d.anomalias > data[best].anomalias ? i : best), 0);
  const pico = data[iPico]?.anomalias ?? 0;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-label="Evolución diaria de transacciones y anomalías">
      {[0, maxY / 2, maxY].map((t) => (
        <g key={t}>
          <line
            x1={padL}
            x2={W - padR}
            y1={y(t)}
            y2={y(t)}
            className="stroke-hairline dark:stroke-[#2a2a26]"
            strokeWidth={t === 0 ? 1.2 : 0.6}
          />
          <text x={padL - 8} y={y(t) + 3} textAnchor="end" fontSize={9} className="fill-silver-2 dark:fill-[#8d8c85] font-data">
            {t}
          </text>
        </g>
      ))}

      {/* Transacciones: área tenue + línea de tinta */}
      <polygon points={areaTxn} className="fill-ink dark:fill-[#f2f1ec]" opacity={0.05} />
      <polyline points={ptsTxn} fill="none" className="stroke-ink dark:stroke-[#f2f1ec]" strokeWidth={1.8} />

      {/* Anomalías: línea de riesgo punteada */}
      <polyline
        points={data.map((d, i) => `${x(i)},${y(d.anomalias)}`).join(' ')}
        fill="none"
        stroke="#b91c1c"
        strokeWidth={1.6}
        strokeDasharray="4 3"
      />
      {data.map((d, i) => (
        <circle key={d.fecha} cx={x(i)} cy={y(d.anomalias)} r={2.6} fill="#b91c1c">
          <title>{`${d.fecha} · ${d.transacciones} transacciones · ${d.anomalias} anomalías`}</title>
        </circle>
      ))}

      {/* REQUISITO A1: marcación del pico repentino del periodo */}
      {pico > 0 && (
        <g>
          <circle cx={x(iPico)} cy={y(pico)} r={4.5} fill="none" stroke="#b91c1c" strokeWidth={1} />
          <text
            x={x(iPico)}
            y={Math.max(10, y(pico) - 9)}
            textAnchor="middle"
            fill="#b91c1c"
            fontSize={9}
            className="font-data"
          >
            pico {pico}
          </text>
        </g>
      )}

      {/* Días (eje X, cada 2 días) */}
      {data.map((d, i) =>
        i % 2 === 0 ? (
          <text key={`x-${d.fecha}`} x={x(i)} y={H - 10} textAnchor="middle" fontSize={9} className="fill-silver-2 dark:fill-[#8d8c85] font-data">
            {d.fecha.slice(8, 10)}
          </text>
        ) : null
      )}
    </svg>
  );
};

/* ── REQUISITO A6: Distribución por hora del día — la intensidad de cada
   celda representa la cantidad de anomalías en esa hora (0-23) ── */
export const HeatmapHoras: React.FC<{ porHora: Record<string, number> }> = ({ porHora }) => {
  const W = 640;
  const m = 4;
  const gap = 3;
  const top = 6;
  const cellH = 46;
  const cw = (W - 2 * m - 23 * gap) / 24;
  const max = Math.max(1, ...Object.values(porHora));
  const horas = Array.from({ length: 24 }, (_, h) => h);

  return (
    <svg viewBox={`0 0 ${W} ${top + cellH + 22}`} className="w-full h-auto" role="img" aria-label="Anomalías por hora del día">
      {horas.map((h) => {
        const v = porHora[String(h)] ?? porHora[h] ?? 0;
        const op = v === 0 ? 0.07 : 0.15 + 0.85 * (v / max);
        return (
          <g key={h}>
            <rect
              x={m + h * (cw + gap)}
              y={top}
              width={cw}
              height={cellH}
              rx={2}
              className="fill-ink dark:fill-[#f2f1ec]"
              opacity={op}
            >
              <title>{`${String(h).padStart(2, '0')}:00 · ${v} anomalía${v === 1 ? '' : 's'}`}</title>
            </rect>
            {v > 0 && (
              <text
                x={m + h * (cw + gap) + cw / 2}
                y={top + cellH / 2 + 3}
                textAnchor="middle"
                fontSize={8.5}
                className={`font-data ${op > 0.5 ? 'fill-paper dark:fill-[#111110]' : 'fill-silver dark:fill-[#8d8c85]'}`}
              >
                {v}
              </text>
            )}
          </g>
        );
      })}
      {horas
        .filter((h) => h % 3 === 0)
        .map((h) => (
          <text
            key={`l${h}`}
            x={m + h * (cw + gap) + cw / 2}
            y={top + cellH + 16}
            textAnchor="middle"
            fontSize={8.5}
            className="fill-silver-2 dark:fill-[#8d8c85] font-data"
          >
            {String(h).padStart(2, '0')}
          </text>
        ))}
    </svg>
  );
};

/* ── Barras horizontales reutilizables ──
   D2 Casos más recurrentes (por tipo) · D3 Múltiples transacciones (tipo
   POSIBLE_FRAUDE) · A2 Anomalías por nivel · A5 Métodos de pago ── */
export const BarrasDistribucion: React.FC<{
  datos: Record<string, number>;
  accentKeys?: string[];
  emptyText?: string;
}> = ({ datos, accentKeys = [], emptyText = 'Sin datos todavía.' }) => {
  const entradas = Object.entries(datos).sort((a, b) => b[1] - a[1]);
  if (!entradas.length) return <p className="text-xs text-silver dark:text-[#8d8c85]">{emptyText}</p>;
  const max = Math.max(1, ...entradas.map(([, v]) => v));
  return (
    <ul className="space-y-2.5">
      {entradas.map(([k, v]) => (
        <li key={k} className="flex items-center gap-3">
          <span
            className="w-24 shrink-0 truncate font-data text-[10px] uppercase tracking-[0.08em] text-silver dark:text-[#8d8c85]"
            title={k}
          >
            {k}
          </span>
          <span className="flex-1 h-[6px] bg-paper-3 dark:bg-negative-3 relative overflow-hidden">
            <span
              className={`absolute inset-y-0 left-0 ${accentKeys.includes(k) ? 'bg-[#b91c1c]' : 'bg-ink dark:bg-[#f2f1ec]'}`}
              style={{ width: `${(v / max) * 100}%` }}
            />
          </span>
          <span className="w-8 text-right font-data text-[11px] font-bold">{v.toLocaleString('es-CO')}</span>
        </li>
      ))}
    </ul>
  );
};

/* ── REQUISITO A3: Línea de tiempo de UNA anomalía — la ventana deslizante
   con las transacciones que la formaron (se abre desde la tabla) ── */
export const TimelineVentana: React.FC<{ txs: TxnVentana[]; ventanaSeg: number; umbral: number }> = ({
  txs,
  ventanaSeg,
  umbral,
}) => {
  const W = 640;
  const H = 196;
  const padL = 34;
  const padR = 34;
  const axisY = 136;
  const innerW = W - padL - padR;
  if (!txs.length) return null;

  const ordenados = [...txs].sort((a, b) => +new Date(a.fecha) - +new Date(b.fecha));
  const ms = ordenados.map((t) => +new Date(t.fecha));
  const tLast = ms[ms.length - 1];
  const boxStart = tLast - ventanaSeg * 1000;
  const domStart = Math.min(ms[0], boxStart);
  const margen = Math.max((tLast - domStart) * 0.16, 400);
  const D0 = domStart - margen;
  const D1 = tLast + margen;
  const X = (v: number) => padL + ((v - D0) / (D1 - D0)) * innerW;
  const boxX = X(boxStart);
  const boxW = Math.max(X(tLast) - boxX, 3);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-label="Línea de tiempo de la anomalía">
      {/* La ventana deslizante */}
      <rect x={boxX} y={34} width={boxW} height={axisY - 28} fill="#b91c1c" opacity={0.07} />
      <rect x={boxX} y={34} width={boxW} height={axisY - 28} fill="none" stroke="#b91c1c" strokeWidth={1} strokeDasharray="3 3" />
      <text x={boxX + 4} y={26} fontSize={9} fill="#b91c1c" className="font-data">
        ventana {ventanaSeg}s
      </text>
      <text x={boxX} y={58} fontSize={8.5} textAnchor="start" className="fill-silver-2 dark:fill-[#8d8c85] font-data">
        {hhmmss(boxStart)}
      </text>
      <text x={boxX + boxW} y={58} fontSize={8.5} textAnchor="end" className="fill-silver-2 dark:fill-[#8d8c85] font-data">
        {hhmmss(tLast)}
      </text>

      {/* Eje de tiempo */}
      <line x1={padL - 22} x2={W - padR + 22} y1={axisY} y2={axisY} className="stroke-hairline dark:stroke-[#2a2a26]" strokeWidth={1.2} />

      {/* Transacciones que formaron la anomalía */}
      {ordenados.map((t, i) => {
        const xi = X(ms[i]);
        const dotY = 70 + (i % 2) * 24;
        const esUltima = i === ordenados.length - 1;
        return (
          <g key={`${t.idTxn}-${i}`}>
            <line
              x1={xi}
              x2={xi}
              y1={dotY + 5}
              y2={axisY}
              className="stroke-silver dark:stroke-[#55554e]"
              strokeWidth={esUltima ? 1.2 : 0.8}
            />
            <circle
              cx={xi}
              cy={dotY}
              r={esUltima ? 5 : 4}
              className={esUltima ? '' : 'fill-ink dark:fill-[#f2f1ec]'}
              fill={esUltima ? '#b91c1c' : undefined}
            >
              <title>{`idTxn ${t.idTxn} · ${hhmmss(ms[i])} · ${t.valor.toLocaleString('es-CO')} COP`}</title>
            </circle>
            <text
              x={xi}
              y={axisY + (i % 2 === 0 ? 14 : 27)}
              textAnchor="middle"
              fontSize={8.5}
              className={`font-data ${esUltima ? '' : 'fill-silver-2 dark:fill-[#8d8c85]'}`}
              fill={esUltima ? '#b91c1c' : undefined}
            >
              {t.idTxn}
            </text>
          </g>
        );
      })}

      {/* Lectura del umbral */}
      <text x={W - padR + 4} y={axisY + 44} fontSize={8.5} textAnchor="end" className="fill-silver-2 dark:fill-[#8d8c85] font-data">
        {ordenados.length} en ventana ≥ umbral {umbral}
      </text>
    </svg>
  );
};

/* ── REQUISITO A4: Visualización de la ventana deslizante en vivo — la
   ventana (caja roja) se desliza al llegar cada transacción nueva ── */
export const StripEnVivo: React.FC<{ txns: TxnProfeRow[]; ventanaSeg: number; umbral: number }> = ({
  txns,
  ventanaSeg,
  umbral,
}) => {
  const conFecha = txns
    .map((t) => ({ ...t, ms: +new Date(t.date) }))
    .filter((t) => !Number.isNaN(t.ms))
    .sort((a, b) => b.ms - a.ms);
  if (!conFecha.length) return null;

  const VISIBLE_S = 90; // últimos 90 segundos a escala
  const nueva = conFecha[0];
  const boxStart = nueva.ms - ventanaSeg * 1000;
  const D0 = nueva.ms - VISIBLE_S * 1000;
  const D1 = nueva.ms + VISIBLE_S * 1000 * 0.06;
  const visibles = conFecha.filter((t) => t.ms >= D0).slice(0, 40);
  const enVentana = conFecha.filter((t) => t.user === nueva.user && t.ms >= boxStart).length;

  const W = 640;
  const H = 108;
  const padL = 10;
  const padR = 10;
  const axisY = 58;
  const innerW = W - padL - padR;
  const X = (ms: number) => padL + ((ms - D0) / (D1 - D0)) * innerW;
  const boxX = X(boxStart);
  const boxW = Math.max(X(nueva.ms) - boxX, 4);
  const fraude = enVentana >= umbral;

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-label="Ventana deslizante en vivo">
        {/* ventana */}
        <rect x={boxX} y={axisY - 26} width={boxW} height={44} fill="#b91c1c" opacity={fraude ? 0.12 : 0.06} />
        <rect x={boxX} y={axisY - 26} width={boxW} height={44} fill="none" stroke="#b91c1c" strokeWidth={1} strokeDasharray="3 3" />
        {/* eje */}
        <line x1={padL} x2={W - padR} y1={axisY} y2={axisY} className="stroke-hairline dark:stroke-[#2a2a26]" strokeWidth={1.2} />
        {/* transacciones: mismas usuario rellenas, otras huecas */}
        {visibles.map((t, i) => {
          const mismo = t.user === nueva.user;
          const dentro = t.ms >= boxStart;
          const xi = X(t.ms);
          return (
            <circle
              key={`${t.idTxn}-${i}`}
              cx={xi}
              cy={mismo ? axisY - 8 : axisY + 12}
              r={mismo ? 3.5 : 2.5}
              fill={mismo && dentro ? '#b91c1c' : mismo ? undefined : 'none'}
              className={mismo && !dentro ? 'fill-ink dark:fill-[#f2f1ec]' : !mismo ? 'stroke-silver dark:stroke-[#8d8c85]' : ''}
              stroke={mismo ? undefined : 'currentColor'}
            >
              <title>{`idTxn ${t.idTxn} · ${t.user} · ${hhmmss(t.ms)}`}</title>
            </circle>
          );
        })}
        {/* límites de la escala */}
        <text x={padL} y={axisY + 30} fontSize={8.5} className="fill-silver-2 dark:fill-[#8d8c85] font-data">
          {hhmmss(D0)}
        </text>
        <text x={W - padR} y={axisY + 30} textAnchor="end" fontSize={8.5} className="fill-silver-2 dark:fill-[#8d8c85] font-data">
          {hhmmss(nueva.ms)} · escala últimos {VISIBLE_S}s
        </text>
      </svg>
      <p className={`font-data text-[11px] mt-1 ${fraude ? 'text-[#b91c1c] font-bold' : 'text-silver dark:text-[#8d8c85]'}`}>
        {enVentana} transacción{enVentana === 1 ? '' : 'es'} de {nueva.user} dentro de la ventana de {ventanaSeg}s · umbral {umbral}
        {fraude ? ' → POSIBLE_FRAUDE' : ''}
      </p>
    </div>
  );
};
