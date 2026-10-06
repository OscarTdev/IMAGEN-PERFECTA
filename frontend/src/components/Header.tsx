import React from 'react';
import { Sun, Moon } from './Icons';
import type { TabType } from './Sidebar';

interface HeaderProps {
  currentTab: TabType;
  dark: boolean;
  onToggleTheme: () => void;
}

const titles: Record<TabType, { title: string; subtitle: string }> = {
  dashboard: {
    title: 'Panel del taller',
    subtitle: 'El día de Imagen Perfecta en una sola hoja: pedidos, estados y producción',
  },
  clientes: {
    title: 'Clientes',
    subtitle: 'Fotógrafos profesionales, aficionados y nuevos clientes en Medellín',
  },
  pedidos: {
    title: 'Pedidos',
    subtitle: 'Seguimiento por código IP-XXXX, cliente, prioridad y estado de producción',
  },
  produccion: {
    title: 'Producción',
    subtitle: 'Flujo de fabricación, turno FIFO y atención por prioridad',
  },
  transacciones: {
    title: 'Transacciones',
    subtitle: 'Recepción del profesor: hash, ventana deslizante por turno, anomalías y umbrales configurables',
  },
  rutas: {
    title: 'Entregas',
    subtitle: 'Ruta más corta por Medellín (Dijkstra) y costo de combustible',
  },
};

export const Header: React.FC<HeaderProps> = ({ currentTab, dark, onToggleTheme }) => {
  const { title, subtitle } = titles[currentTab];

  return (
    <header className="border-b border-hairline dark:border-[#2a2a26] px-8 py-5 flex items-end justify-between sticky top-0 z-10 bg-paper/95 dark:bg-negative/95 backdrop-blur-sm">
      <div>
        <h2 className="text-[26px] font-bold tracking-tight leading-none text-ink dark:text-[#f2f1ec]">
          {title}
        </h2>
        <p className="text-xs text-silver dark:text-[#8d8c85] mt-1.5 max-w-[65ch]">
          {subtitle}
        </p>
      </div>
      <button
        onClick={onToggleTheme}
        title={dark ? 'Invertir a positivo (papel)' : 'Invertir a negativo (tinta)'}
        aria-label={dark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
        className="flex items-center gap-2 px-3 py-2 border border-hairline dark:border-[#3a3a35] hover:border-ink dark:hover:border-[#f2f1ec] text-ink dark:text-[#f2f1ec] transition-colors"
      >
        {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        <span className="font-data text-[10px] uppercase tracking-[0.14em]">
          {dark ? 'Positivo' : 'Negativo'}
        </span>
      </button>
    </header>
  );
};
