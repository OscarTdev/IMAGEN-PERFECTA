# Imagen Perfecta — Frontend Web

Interfaz académica para el sistema **Imagen Perfecta**, desarrollada con **React 19**, **TypeScript**, **Vite** y **Tailwind CSS**.

## Principio de Diseño Académico

> **El frontend NO implementa algoritmos de lógica de negocio.**
> Únicamente consume la API REST del backend mediante HTTP (`fetch`), valida entradas y renderiza los resultados.

## Módulos de la Interfaz

* **Dashboard:** Pedidos registrados, en proceso, entregados, pendientes y acceso rápido a análisis.
* **Clientes:** Directorio de clientes (Fotógrafos, Aficionados, Nuevos clientes) y formulario de registro.
* **Pedidos:** Tabla con búsqueda, filtros, creación de pedidos y cambio de estado de producción.
* **Producción:** Visualización interactiva de Cola FIFO, Min-Heap de prioridad y flujo de Lista Enlazada.
* **Estructuras:** Laboratorio interactivo para Lista Enlazada, Pila LIFO, Cola FIFO y Heap.
* **Algoritmos:** Búsqueda lineal vs binaria, tabla Big O, sumatorias Gauss, progresión aritmética, recursividad y regresión lineal.
* **Rutas:** Cálculo de la ruta más corta con Dijkstra en Medellín y estimación configurable de combustible.

## Instalación y Ejecución

```bash
# 1. Instalar dependencias
npm install

# 2. Iniciar servidor de desarrollo
npm run dev

# 3. Compilar para producción
npm run build
```

El cliente web corre en `http://localhost:5173`.
