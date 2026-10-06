import React, { useEffect, useState } from 'react';
import { message, Button } from 'antd';
import { ArrowRight, Play, CheckCircle2, Clock, Layers, Flame } from '../components/Icons';
import {
  getCola,
  dequeueCola,
  enqueueCola,
  getHeap,
  extraerHeap,
  insertarHeap,
  getListaEnlazada,
  agregarEtapaLista,
} from '../services/api';
import type { ColaData, HeapData, ListaEnlazadaData } from '../types';

export const Produccion: React.FC = () => {
  const [cola, setCola] = useState<ColaData | null>(null);
  const [heap, setHeap] = useState<HeapData | null>(null);
  const [lista, setLista] = useState<ListaEnlazadaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [mensajeAtendidoCola, setMensajeAtendidoCola] = useState<string | null>(null);
  const [mensajeAtendidoHeap, setMensajeAtendidoHeap] = useState<string | null>(null);

  const [nuevoCodigoCola, setNuevoCodigoCola] = useState('IP-0105');
  const [nuevoClienteCola, setNuevoClienteCola] = useState('Valentina Ríos');
  const [nuevosProductosCola, setNuevosProductosCola] = useState('Foto 20x30, Marco');

  const [nuevoCodigoHeap, setNuevoCodigoHeap] = useState('IP-0106');
  const [nuevoClienteHeap, setNuevoClienteHeap] = useState('Mateo Restrepo');
  const [nuevaPrioridadHeap, setNuevaPrioridadHeap] = useState<'Urgente' | 'Alta' | 'Normal'>('Urgente');

  const [nuevaEtapa, setNuevaEtapa] = useState('');

  const cargarDatos = () => {
    setLoading(true);
    setError(null);
    Promise.all([getCola(), getHeap(), getListaEnlazada()])
      .then(([colaRes, heapRes, listaRes]) => {
        setCola(colaRes);
        setHeap(heapRes);
        setLista(listaRes);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      });
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const handleDequeueCola = async () => {
    try {
      const res = await dequeueCola();
      setCola(res.cola);
      setMensajeAtendidoCola(
        `Atendido: ${res.atendido.codigo} (${res.atendido.cliente}) — ${res.atendido.productos}`
      );
    } catch (err: unknown) {
      if (err instanceof Error) message.error(err.message);
    }
  };

  const handleEnqueueCola = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await enqueueCola(nuevoCodigoCola, nuevoClienteCola, nuevosProductosCola);
      setCola(res);
      setNuevoCodigoCola(`IP-0${Math.floor(100 + Math.random() * 900)}`);
    } catch (err: unknown) {
      if (err instanceof Error) message.error(err.message);
    }
  };

  const handleExtraerHeap = async () => {
    try {
      const res = await extraerHeap();
      setHeap(res.heap);
      const ped = res.atendido as { codigo?: string; cliente?: string };
      setMensajeAtendidoHeap(
        `Atendido prioritario: ${ped.codigo || 'Pedido'} (${ped.cliente || 'Cliente'})`
      );
    } catch (err: unknown) {
      if (err instanceof Error) message.error(err.message);
    }
  };

  const handleInsertarHeap = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await insertarHeap(nuevoCodigoHeap, nuevoClienteHeap, nuevaPrioridadHeap);
      setHeap(res);
      setNuevoCodigoHeap(`IP-0${Math.floor(100 + Math.random() * 900)}`);
    } catch (err: unknown) {
      if (err instanceof Error) message.error(err.message);
    }
  };

  const handleAgregarEtapa = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nuevaEtapa.trim()) return;
    try {
      const res = await agregarEtapaLista(nuevaEtapa.trim());
      setLista(res);
      setNuevaEtapa('');
    } catch (err: unknown) {
      if (err instanceof Error) message.error(err.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-10">
      {loading ? (
        <div className="p-8 text-center text-sm text-silver dark:text-[#8d8c85]">
          Cargando producción…
        </div>
      ) : error ? (
        <div className="sheet p-6 flex flex-col items-start gap-3">
          <p className="text-sm font-bold">No se pudo cargar la producción</p>
          <p className="text-xs text-silver dark:text-[#8d8c85] max-w-[65ch]">
            Verifica que el backend FastAPI esté corriendo en el puerto 8000. Detalle: {error}
          </p>
          <Button onClick={cargarDatos}>Reintentar</Button>
        </div>
      ) : (
        <div className="space-y-10">
          {/* Flujo de fabricación: lista enlazada del taller */}
          <section className="sheet p-6 space-y-4">
            <div className="flex items-center gap-2.5">
              <Layers className="w-4 h-4" />
              <h3 className="text-sm font-bold">Flujo de fabricación</h3>
              <span className="font-data text-[11px] text-silver-2 dark:text-[#8d8c85]">
                cada etapa pasa a la siguiente hasta terminar en NULL
              </span>
            </div>

            <div className="border border-hairline dark:border-[#2a2a26] bg-paper-2 dark:bg-negative-3 p-5 overflow-x-auto">
              <div className="flex items-center gap-2 min-w-max py-1">
                {lista?.etapas.map((etapa, idx) => (
                  <React.Fragment key={idx}>
                    <div className="px-4 py-2 border border-ink dark:border-[#f2f1ec] text-center">
                      <span className="font-data text-[10px] uppercase tracking-[0.14em] text-silver-2 dark:text-[#8d8c85] block">
                        Etapa {idx + 1}
                      </span>
                      <span className="text-[13px] font-semibold">{etapa}</span>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-silver-2 dark:text-[#8d8c85] shrink-0" />
                  </React.Fragment>
                ))}
                <div className="px-3 py-2 border border-dashed border-hairline dark:border-[#3a3a35] font-data text-[11px] text-silver-2 dark:text-[#8d8c85]">
                  NULL
                </div>
              </div>
              <p className="font-data text-[11px] mt-4 bg-paper dark:bg-negative-2 p-2.5 border border-hairline dark:border-[#2a2a26] break-all">
                {lista?.estructura}
              </p>
            </div>

            <form onSubmit={handleAgregarEtapa} className="flex gap-2 max-w-md">
              <input
                type="text"
                value={nuevaEtapa}
                onChange={(e) => setNuevaEtapa(e.target.value)}
                placeholder="Nueva etapa (ej. Laminado especial)"
                className="flex-1 px-3 py-2 bg-paper dark:bg-negative-2 border border-hairline dark:border-[#2a2a26] text-[13px] placeholder:text-silver-2 dark:placeholder:text-[#8d8c85] focus:outline-none focus:border-ink dark:focus:border-[#f2f1ec]"
              />
              <button type="submit" className="px-4 py-2 bg-ink text-paper dark:bg-[#f2f1ec] dark:text-negative text-[13px] font-semibold hover:opacity-85 transition">
                Agregar etapa
              </button>
            </form>
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Cola FIFO: turno de producción */}
            <section className="sheet p-6 flex flex-col justify-between gap-5">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-hairline dark:border-[#2a2a26]">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <div>
                      <h3 className="text-[13px] font-bold uppercase tracking-wide">Turno de producción</h3>
                      <p className="text-[11px] text-silver dark:text-[#8d8c85]">
                        Primero en llegar, primero en atenderse (FIFO)
                      </p>
                    </div>
                  </div>
                  <span className="font-data text-[11px] border border-hairline dark:border-[#3a3a35] px-2 py-1">
                    En cola: {cola?.tamanio ?? 0}
                  </span>
                </div>

                {mensajeAtendidoCola && (
                  <div className="mt-3 p-2.5 border border-hairline dark:border-[#2a2a26] bg-paper-2 dark:bg-negative-3 text-[12px] flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>{mensajeAtendidoCola}</span>
                  </div>
                )}

                <div className="mt-4">
                  <span className="spec-label mb-2 block">Orden de llegada</span>
                  {cola?.items.length === 0 ? (
                    <div className="p-4 border border-dashed border-hairline dark:border-[#3a3a35] text-[12px] text-silver-2 dark:text-[#8d8c85] text-center">
                      No hay pedidos en espera.
                    </div>
                  ) : (
                    <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                      {cola?.items.map((item, idx) => (
                        <div
                          key={idx}
                          className={`p-2.5 border flex items-center justify-between text-[12px] ${
                            idx === 0
                              ? 'border-ink dark:border-[#f2f1ec] bg-paper-2 dark:bg-negative-3'
                              : 'border-hairline dark:border-[#2a2a26]'
                          }`}
                        >
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-data font-bold">{item.codigo}</span>
                              {idx === 0 && (
                                <span className="bg-ink text-paper dark:bg-[#f2f1ec] dark:text-negative font-data text-[9px] uppercase tracking-wider px-1.5 py-0.5">
                                  Próximo
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-silver dark:text-[#8d8c85] mt-0.5">
                              {item.cliente} — {item.productos}
                            </p>
                          </div>
                          <span className="font-data text-[10px] text-silver-2 dark:text-[#8d8c85]">
                            #{idx + 1}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-3 pt-4 border-t border-hairline dark:border-[#2a2a26]">
                <button
                  onClick={handleDequeueCola}
                  disabled={!cola?.items.length}
                  className="w-full py-2.5 bg-ink text-paper dark:bg-[#f2f1ec] dark:text-negative text-[13px] font-semibold hover:opacity-85 disabled:opacity-35 transition flex items-center justify-center gap-2"
                >
                  <Play className="w-3.5 h-3.5" />
                  Atender siguiente del turno
                </button>
                <form onSubmit={handleEnqueueCola} className="grid grid-cols-4 gap-2">
                  <input
                    type="text"
                    value={nuevoCodigoCola}
                    onChange={(e) => setNuevoCodigoCola(e.target.value)}
                    placeholder="Código"
                    className="px-2 py-1.5 bg-paper dark:bg-negative-2 border border-hairline dark:border-[#2a2a26] font-data text-[12px]"
                  />
                  <input
                    type="text"
                    value={nuevoClienteCola}
                    onChange={(e) => setNuevoClienteCola(e.target.value)}
                    placeholder="Cliente"
                    className="px-2 py-1.5 bg-paper dark:bg-negative-2 border border-hairline dark:border-[#2a2a26] text-[12px]"
                  />
                  <input
                    type="text"
                    value={nuevosProductosCola}
                    onChange={(e) => setNuevosProductosCola(e.target.value)}
                    placeholder="Productos"
                    className="px-2 py-1.5 bg-paper dark:bg-negative-2 border border-hairline dark:border-[#2a2a26] text-[12px]"
                  />
                  <button type="submit" className="px-2 py-1.5 border border-ink dark:border-[#f2f1ec] hover:bg-ink hover:text-paper dark:hover:bg-[#f2f1ec] dark:hover:text-negative text-[12px] font-medium transition-colors">
                    Agregar
                  </button>
                </form>
              </div>
            </section>

            {/* Heap: pedidos prioritarios */}
            <section className="sheet p-6 flex flex-col justify-between gap-5">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-hairline dark:border-[#2a2a26]">
                  <div className="flex items-center gap-2">
                    <Flame className="w-4 h-4" />
                    <div>
                      <h3 className="text-[13px] font-bold uppercase tracking-wide">Pedidos prioritarios</h3>
                      <p className="text-[11px] text-silver dark:text-[#8d8c85]">
                        Heap: 1 urgente · 2 alta · 3 normal
                      </p>
                    </div>
                  </div>
                  <span className="font-data text-[11px] border border-hairline dark:border-[#3a3a35] px-2 py-1">
                    En espera: {heap?.tamanio ?? 0}
                  </span>
                </div>

                {mensajeAtendidoHeap && (
                  <div className="mt-3 p-2.5 border border-hairline dark:border-[#2a2a26] bg-paper-2 dark:bg-negative-3 text-[12px] flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>{mensajeAtendidoHeap}</span>
                  </div>
                )}

                <div className="mt-4">
                  <span className="spec-label mb-2 block">Orden de atención</span>
                  {heap?.items.length === 0 ? (
                    <div className="p-4 border border-dashed border-hairline dark:border-[#3a3a35] text-[12px] text-silver-2 dark:text-[#8d8c85] text-center">
                      No hay pedidos prioritarios.
                    </div>
                  ) : (
                    <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                      {heap?.items.map((item, idx) => {
                        const priTexto =
                          item.prioridad === 1 ? 'Urgente' : item.prioridad === 2 ? 'Alta' : 'Normal';
                        return (
                          <div
                            key={idx}
                            className={`p-2.5 border flex items-center justify-between text-[12px] ${
                              idx === 0
                                ? 'border-ink dark:border-[#f2f1ec] bg-paper-2 dark:bg-negative-3'
                                : 'border-hairline dark:border-[#2a2a26]'
                            }`}
                          >
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-data font-bold">{item.pedido.codigo}</span>
                                <span
                                  className={`font-data text-[9px] uppercase tracking-wider px-1.5 py-0.5 ${
                                    item.prioridad === 1
                                      ? 'bg-[#b91c1c] text-white'
                                      : item.prioridad === 2
                                      ? 'bg-[#b45309] text-white'
                                      : 'border border-hairline dark:border-[#3a3a35] text-silver dark:text-[#8d8c85]'
                                  }`}
                                >
                                  {priTexto}
                                </span>
                              </div>
                              <p className="text-[11px] text-silver dark:text-[#8d8c85] mt-0.5">
                                {item.pedido.cliente}
                              </p>
                            </div>
                            {idx === 0 && (
                              <span className="bg-ink text-paper dark:bg-[#f2f1ec] dark:text-negative font-data text-[9px] uppercase tracking-wider px-1.5 py-0.5">
                                Siguiente
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-3 pt-4 border-t border-hairline dark:border-[#2a2a26]">
                <button
                  onClick={handleExtraerHeap}
                  disabled={!heap?.items.length}
                  className="w-full py-2.5 bg-ink text-paper dark:bg-[#f2f1ec] dark:text-negative text-[13px] font-semibold hover:opacity-85 disabled:opacity-35 transition flex items-center justify-center gap-2"
                >
                  <Play className="w-3.5 h-3.5" />
                  Atender pedido prioritario
                </button>
                <form onSubmit={handleInsertarHeap} className="grid grid-cols-4 gap-2">
                  <input
                    type="text"
                    value={nuevoCodigoHeap}
                    onChange={(e) => setNuevoCodigoHeap(e.target.value)}
                    placeholder="Código"
                    className="px-2 py-1.5 bg-paper dark:bg-negative-2 border border-hairline dark:border-[#2a2a26] font-data text-[12px]"
                  />
                  <input
                    type="text"
                    value={nuevoClienteHeap}
                    onChange={(e) => setNuevoClienteHeap(e.target.value)}
                    placeholder="Cliente"
                    className="px-2 py-1.5 bg-paper dark:bg-negative-2 border border-hairline dark:border-[#2a2a26] text-[12px]"
                  />
                  <select
                    value={nuevaPrioridadHeap}
                    onChange={(e) => setNuevaPrioridadHeap(e.target.value as 'Urgente' | 'Alta' | 'Normal')}
                    className="px-2 py-1.5 bg-paper dark:bg-negative-2 border border-hairline dark:border-[#2a2a26] text-[12px]"
                  >
                    <option value="Urgente">Urgente (1)</option>
                    <option value="Alta">Alta (2)</option>
                    <option value="Normal">Normal (3)</option>
                  </select>
                  <button type="submit" className="px-2 py-1.5 border border-ink dark:border-[#f2f1ec] hover:bg-ink hover:text-paper dark:hover:bg-[#f2f1ec] dark:hover:text-negative text-[12px] font-medium transition-colors">
                    Agregar
                  </button>
                </form>
              </div>
            </section>
          </div>
        </div>
      )}
    </div>
  );
};
