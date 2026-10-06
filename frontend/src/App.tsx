import React, { useEffect, useState } from 'react';
import { ConfigProvider, App as AntdApp, Layout } from 'antd';
import esES from 'antd/locale/es_ES';
import { getAntdTheme } from './theme';
import { Sidebar, type TabType } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { Clientes } from './pages/Clientes';
import { Pedidos } from './pages/Pedidos';
import { Produccion } from './pages/Produccion';
import { Transacciones } from './pages/Transacciones';
import { Entregas } from './pages/Entregas';

const THEME_KEY = 'ip-theme';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<TabType>('dashboard');
  const [dark, setDark] = useState<boolean>(() => {
    try {
      return localStorage.getItem(THEME_KEY) === 'dark';
    } catch {
      return false;
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    const primeraVez = !root.classList.contains('ip-booted');
    root.classList.add('ip-booted');
    root.classList.toggle('dark', dark);
    if (!primeraVez) {
      // Movimiento firma: la inversión se orquesta una sola vez y se retira al terminar
      root.classList.add('theme-flip');
      const t = window.setTimeout(() => root.classList.remove('theme-flip'), 340);
      try {
        localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light');
      } catch {
        /* almacenamiento no disponible */
      }
      return () => window.clearTimeout(t);
    }
    try {
      localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light');
    } catch {
      /* almacenamiento no disponible */
    }
  }, [dark]);

  return (
    <ConfigProvider theme={getAntdTheme(dark)} locale={esES}>
      <AntdApp>
        <div className="flex min-h-screen bg-paper text-ink dark:bg-negative dark:text-[#f2f1ec] font-sans">
          <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

          <div className="flex-1 flex flex-col min-w-0">
            <Header currentTab={currentTab} dark={dark} onToggleTheme={() => setDark((d) => !d)} />

            <main className="flex-1 px-4 sm:px-8 py-8 overflow-x-hidden">
              {currentTab === 'dashboard' && <Dashboard onNavigate={setCurrentTab} />}
              {currentTab === 'clientes' && <Clientes />}
              {currentTab === 'pedidos' && <Pedidos />}
              {currentTab === 'transacciones' && <Transacciones />}
              {currentTab === 'produccion' && <Produccion />}
              {currentTab === 'rutas' && <Entregas />}
              <Layout.Footer className="text-center !bg-transparent !text-silver-2 dark:!text-[#8d8c85] text-xs pt-12">
                Imagen Perfecta · Medellín — React 19 + Ant Design · API FastAPI + MySQL
              </Layout.Footer>
            </main>
          </div>
        </div>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;
