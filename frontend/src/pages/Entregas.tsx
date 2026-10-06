import React, { useEffect, useState } from 'react';
import { App as AntdApp, Button, InputNumber, Select } from 'antd';
import { Fuel, Navigation } from '../components/Icons';
import { getGrafo, calcularDijkstra, calcularCombustible } from '../services/api';
import type { GrafoData, ResultadoDijkstra, ResultadoCombustible, AristaGrafo } from '../types';

/* Posiciones del grafo de Medellín (px en un lienzo de 560×340) */
const POS: Record<string, { x: number; y: number }> = {
  Centro: { x: 150, y: 170 },
  Laureles: { x: 290, y: 120 },
  Belén: { x: 300, y: 235 },
  'El Poblado': { x: 420, y: 250 },
  Robledo: { x: 150, y: 60 },
  Envigado: { x: 470, y: 170 },
};

const COP = (v: number) =>
  v.toLocaleString('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });

export const Entregas: React.FC = () => {
  const { message } = AntdApp.useApp();
  const [grafo, setGrafo] = useState<GrafoData | null>(null);
  const [origen, setOrigen] = useState('Centro');
  const [destino, setDestino] = useState('Envigado');
  const [resultado, setResultado] = useState<ResultadoDijkstra | null>(null);
  const [calculando, setCalculando] = useState(false);

  const [distancia, setDistancia] = useState(8.5);
  const [rendimiento, setRendimiento] = useState(12);
  const [precio, setPrecio] = useState(14500);
  const [combustible, setCombustible] = useState<ResultadoCombustible | null>(null);

  useEffect(() => {
    getGrafo()
      .then(setGrafo)
      .catch((err: Error) => message.error(`No se pudo cargar el grafo: ${err.message}`));
  }, [message]);

  const handleDijkstra = async () => {
    setCalculando(true);
    try {
      const res = await calcularDijkstra(origen, destino);
      setResultado(res);
      if (res.distancia_km) setDistancia(res.distancia_km);
    } catch (err) {
      message.error(`Error calculando la ruta: ${err instanceof Error ? err.message : 'desconocido'}`);
    } finally {
      setCalculando(false);
    }
  };

  const handleCombustible = async () => {
    try {
      const res = await calcularCombustible(distancia, rendimiento, precio);
      setCombustible(res);
    } catch (err) {
      message.error(`Error calculando combustible: ${err instanceof Error ? err.message : 'desconocido'}`);
    }
  };

  const enRuta = (a: string) => resultado?.ruta.includes(a) ?? false;
  const aristaEnRuta = (e: AristaGrafo) => {
    if (!resultado) return false;
    const i = resultado.ruta.indexOf(e.origen);
    return i >= 0 && resultado.ruta[i + 1] === e.destino;
  };

  return (
    <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-5 gap-8">
      {/* Grafo de zonas */}
      <section className="sheet p-6 lg:col-span-3">
        <div className="flex items-center gap-2 mb-4">
          <Navigation className="w-4 h-4" />
          <h3 className="text-sm font-bold">Zonas de entrega — Medellín</h3>
        </div>
        <div className="border border-hairline dark:border-[#2a2a26] bg-paper-2 dark:bg-negative-3 overflow-x-auto">
          <svg viewBox="0 0 560 320" className="w-full min-w-[480px]">
            {/* Aristas */}
            {grafo?.aristas.map((e, i) => {
              const p1 = POS[e.origen];
              const p2 = POS[e.destino];
              if (!p1 || !p2) return null;
              const activa = aristaEnRuta(e);
              return (
                <g key={i}>
                  <line
                    x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y}
                    stroke={activa ? 'currentColor' : '#a5a49e'}
                    strokeWidth={activa ? 3 : 1}
                    className={activa ? 'text-ink dark:text-[#f2f1ec]' : ''}
                    strokeDasharray={activa ? undefined : '4 3'}
                  />
                  <text
                    x={(p1.x + p2.x) / 2}
                    y={(p1.y + p2.y) / 2 - 6}
                    textAnchor="middle"
                    className="fill-silver-2 dark:fill-[#8d8c85]"
                    fontSize="10"
                    fontFamily="ui-monospace, Consolas, monospace"
                  >
                    {e.distancia_km} km
                  </text>
                </g>
              );
            })}
            {/* Nodos */}
            {grafo?.nodos.map((n) => {
              const p = POS[n];
              if (!p) return null;
              const activo = enRuta(n);
              return (
                <g key={n}>
                  <rect
                    x={p.x - 52} y={p.y - 16} width={104} height={32}
                    fill={activo ? 'currentColor' : 'none'}
                    stroke="currentColor"
                    strokeWidth={1.5}
                    className="text-ink dark:text-[#f2f1ec]"
                  />
                  <text
                    x={p.x} y={p.y + 4}
                    textAnchor="middle"
                    fontSize="12"
                    fontWeight="600"
                    className={
                      activo
                        ? 'fill-paper dark:fill-negative'
                        : 'fill-ink dark:fill-[#f2f1ec]'
                    }
                  >
                    {n}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Calculadora de ruta */}
        <div className="mt-5 flex flex-col sm:flex-row gap-3 items-stretch">
          <Select
            value={origen}
            onChange={setOrigen}
            className="flex-1"
            options={grafo?.nodos.map((n) => ({ value: n, label: `Origen: ${n}` }))}
          />
          <Select
            value={destino}
            onChange={setDestino}
            className="flex-1"
            options={grafo?.nodos.map((n) => ({ value: n, label: `Destino: ${n}` }))}
          />
          <Button type="primary" loading={calculando} onClick={handleDijkstra}>
            Calcular ruta
          </Button>
        </div>

        {resultado && (
          <div className="mt-4 border-t border-hairline dark:border-[#2a2a26] pt-4">
            <span className="spec-label">Ruta más corta (Dijkstra)</span>
            <p className="font-data text-[13px] font-bold mt-1">
              {resultado.ruta.join(' → ')}
              <span className="text-silver dark:text-[#8d8c85] font-normal">
                {'  ·  '}{resultado.distancia_km} km
              </span>
            </p>
            <p className="text-[11px] text-silver-2 dark:text-[#8d8c85] mt-1">
              Nodos visitados: {resultado.nodos_visitados.join(', ')}
            </p>
          </div>
        )}
      </section>

      {/* Combustible */}
      <section className="sheet p-6 lg:col-span-2 h-fit">
        <div className="flex items-center gap-2 mb-4">
          <Fuel className="w-4 h-4" />
          <h3 className="text-sm font-bold">Combustible del despacho</h3>
        </div>
        <p className="text-xs text-silver dark:text-[#8d8c85] mb-4">
          Litros = distancia ÷ rendimiento · Costo = litros × precio por litro.
          La distancia se llena con la última ruta calculada.
        </p>
        <div className="space-y-3">
          <div>
            <span className="spec-label">Distancia (km)</span>
            <InputNumber min={0.1} step={0.1} value={distancia} onChange={(v) => setDistancia(v ?? 0.1)} className="w-full mt-1" />
          </div>
          <div>
            <span className="spec-label">Rendimiento (km/L)</span>
            <InputNumber min={1} step={0.5} value={rendimiento} onChange={(v) => setRendimiento(v ?? 12)} className="w-full mt-1" />
          </div>
          <div>
            <span className="spec-label">Precio por litro (COP)</span>
            <InputNumber min={100} step={100} value={precio} onChange={(v) => setPrecio(v ?? 14500)} className="w-full mt-1" />
          </div>
          <Button className="w-full" onClick={handleCombustible}>
            Estimar consumo
          </Button>
        </div>

        {combustible && (
          <div className="mt-5 border-t border-hairline dark:border-[#2a2a26] pt-4 space-y-2">
            <div className="flex justify-between text-[13px]">
              <span className="text-silver dark:text-[#8d8c85]">Litros estimados</span>
              <b className="font-data">{combustible.litros_estimados} L</b>
            </div>
            <div className="flex justify-between text-[13px]">
              <span className="text-silver dark:text-[#8d8c85]">Costo estimado</span>
              <b className="font-data">{COP(combustible.costo_estimado)}</b>
            </div>
          </div>
        )}
      </section>
    </div>
  );
};
