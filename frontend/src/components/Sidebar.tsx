import React from 'react';
import {
  LayoutDashboard,
  Users,
  PackageCheck,
  Factory,
  Navigation,
  ApertureMark,
  ArrowLeftRight,
} from './Icons';

export type TabType =
  | 'dashboard'
  | 'clientes'
  | 'pedidos'
  | 'transacciones'
  | 'produccion'
  | 'rutas';

interface SidebarProps {
  currentTab: TabType;
  setCurrentTab: (tab: TabType) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab }) => {
  const items = [
    { id: 'dashboard' as TabType, label: 'Panel', icon: LayoutDashboard },
    { id: 'clientes' as TabType, label: 'Clientes', icon: Users },
    { id: 'pedidos' as TabType, label: 'Pedidos', icon: PackageCheck },
    { id: 'transacciones' as TabType, label: 'Transacciones', icon: ArrowLeftRight },
    { id: 'produccion' as TabType, label: 'Producción', icon: Factory },
    { id: 'rutas' as TabType, label: 'Entregas', icon: Navigation },
  ];

  const renderItem = (item: { id: TabType; label: string; icon: React.FC<{ className?: string }> }) => {
    const Icon = item.icon;
    const isActive = currentTab === item.id;
    return (
      <button
        key={item.id}
        onClick={() => setCurrentTab(item.id)}
        className={`w-full flex items-center gap-3 px-3 py-2 text-[13px] font-medium transition-colors duration-150 text-left border-l-2 ${
          isActive
            ? 'border-ink bg-ink text-paper dark:border-[#f2f1ec] dark:bg-[#f2f1ec] dark:text-negative'
            : 'border-transparent text-silver hover:text-ink hover:bg-paper-2 dark:text-[#8d8c85] dark:hover:text-[#f2f1ec] dark:hover:bg-negative-3'
        }`}
      >
        <Icon className="w-4 h-4 shrink-0" />
        <span>{item.label}</span>
      </button>
    );
  };

  return (
    <aside className="w-56 bg-paper dark:bg-negative border-r border-hairline dark:border-[#2a2a26] flex flex-col shrink-0 min-h-screen">
      {/* Marca: bloque de tinta con el nombre del taller */}
      <div className="px-5 py-6 border-b border-hairline dark:border-[#2a2a26]">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-ink text-paper dark:bg-[#f2f1ec] dark:text-negative">
            <ApertureMark className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-[15px] tracking-tight text-ink dark:text-[#f2f1ec] leading-tight">
              Imagen Perfecta
            </h1>
            <p className="font-data text-[10px] uppercase tracking-[0.14em] text-silver dark:text-[#8d8c85] mt-0.5">
              Medellín · Antioquia
            </p>
          </div>
        </div>
      </div>

      <nav className="flex-1 py-4 px-3 space-y-0.5 overflow-y-auto">
        <div className="px-3 pb-2 font-data text-[10px] uppercase tracking-[0.14em] text-silver dark:text-[#8d8c85]">
          Negocio
        </div>
        {items.map(renderItem)}
      </nav>

      <div className="p-4 border-t border-hairline dark:border-[#2a2a26]">
        <p className="font-data text-[10px] leading-relaxed text-silver dark:text-[#8d8c85] text-center">
          Impresión · Enmarcado · Portafolios
        </p>
      </div>
    </aside>
  );
};
