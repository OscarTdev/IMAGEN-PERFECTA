---
name: Imagen Perfecta — Sistema de Gestión
description: La ficha de impresión como interfaz: papel, tinta, plata y el negativo estricto — el oficio de un taller fotográfico de Medellín convertido en sistema operativo.
colors:
  papel-de-imprenta: "#FAFAF8"
  papel-de-panel: "#F2F1EC"
  tinta-de-bloque: "#141412"
  plata-de-revelado: "#6B6B66"
  plata-de-anotacion: "#6C6B65"
  filete: "#DCDBD4"
  negativo-de-archivo: "#111110"
  negativo-de-panel: "#1B1B18"
  negativo-de-detalle: "#262622"
  texto-de-negativo: "#F2F1EC"
  filete-de-negativo: "#2A2A26"
  filete-de-negativo-2: "#3A3A35"
  estado-exito: "#15803D"
  estado-alerta: "#B45309"
  estado-error: "#B91C1C"
typography:
  display:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "15px–26px"
    fontWeight: 700
    letterSpacing: "-0.015em"
    lineHeight: 1.15
  body:
    fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "ui-monospace, SF Mono, Cascadia Mono, Consolas, monospace"
    fontSize: "10px"
    fontWeight: 500
    letterSpacing: "0.14em"
    lineHeight: 1.3
rounded:
  sheet: "0px"
  control: "2px"
spacing:
  page: "32px"
  sheet: "24px"
  control: "10px"
components:
  button-primary:
    backgroundColor: "{colors.tinta-de-bloque}"
    textColor: "#FFFFFF"
    rounded: "{rounded.control}"
    padding: "7px 15px"
  button-primary-hover:
    backgroundColor: "{colors.negativo-de-detalle}"
  nav-item-active:
    backgroundColor: "{colors.tinta-de-bloque}"
    textColor: "{colors.papel-de-imprenta}"
    rounded: "{rounded.sheet}"
    padding: "8px 12px"
  sheet:
    backgroundColor: "{colors.papel-de-imprenta}"
    textColor: "{colors.tinta-de-bloque}"
    rounded: "{rounded.sheet}"
    padding: "24px"
  spec-label:
    typography: "{typography.label}"
    textColor: "{colors.plata-de-revelado}"
  spec-value:
    typography: "{typography.display}"
    textColor: "{colors.tinta-de-bloque}"
  tag-estado-exito:
    textColor: "{colors.estado-exito}"
    rounded: "{rounded.control}"
---

# Design System: Imagen Perfecta — Sistema de Gestión

## Overview

**Creative North Star: "La Ficha de Impresión"**

El sistema se lee como la ficha técnica de un taller de impresión: hojas de papel casi blanco divididas por filetes de un pelo, tinta casi negra para todo lo que importa, plata para lo que anota, y el código (`IP-XXXX`, hashes, conteos) en mono tabular como tipografía de máquina. La jerarquía no la hacen el color ni la sombra: la hacen la escala, el peso y el aire. El modo oscuro no es un tema genérico — es el **negativo estricto**: invertir la ficha es voltear una fotografía, y todo el sistema (incluidos los tokens de Ant Design) se invierte con ella en un único movimiento orquestado de 260 ms.

La operación manda: el personal del taller de Imagen Perfecta (Centro de Medellín) completa tareas todo el día, así que las mesas son densas, los estados se dicen en color funcional (éxito, alerta, error) y nada decora. Los degradados, las sombras decorativas y las tarjetas icono+título+texto no existen en este mundo.

**Key Characteristics:**
- Papel de imprenta como suelo universal; el blanco puro está prohibido
- Tinta como primario único; el color solo hace trabajos funcionales (estados)
- Filetes de 1 px en lugar de sombras; la profundidad es tonal, no elevada
- Códigos y mediciones en mono tabular; la letra de carácter (Archivo) solo para títulos y valores
- El negativo estricto: invertir el tema invierte TODO, una sola vez, orquestado

## Colors

Paleta de imprenta: dos tintas (papel y bloque) con una rampa de plata para la anotación, y tres colores funcionales que solo hablan de estados.

### Primary
- **Tinta de Bloque** (#141412): la voz principal — texto, botones primarios, nav activa, valores. En el negativo se convierte en el texto (#F2F1EC).

### Secondary
- **Plata de Revelado** (#6B6B66): texto secundario en claro (≥5.1:1 sobre papel).
- **Plata de Anotación** (#6C6B65): notas pequeñas de 10–11 px (≥4.7:1 sobre papel y paneles).

### Tertiary
- **Estado Éxito** (#15803D), **Estado Alerta** (#B45309), **Estado Error** (#B91C1C): los únicos colores permitidos; solo significan estados (Entregado, En proceso/Listo, Urgente/fallo). Nunca decoran.

### Neutral
- **Papel de Imprenta** (#FAFAF8): suelo universal de las hojas, mesas y modales en claro.
- **Papel de Panel** (#F2F1EC): paneles internos, cabeceras de mesa, zonas de trabajo en claro.
- **Filete** (#DCDBD4): la línea de 1 px que divide todo.
- **Negativo de Archivo** (#111110), **Negativo de Panel** (#1B1B18), **Negativo de Detalle** (#262622): la inversión del papel en oscuro.
- **Texto de Negativo** (#F2F1EC), **Filete de Negativo** (#2A2A26 / #3A3A35): la inversión de tinta y filete.

### Named Rules
**La Regla del Negativo Estricto.** En modo oscuro TODO se invierte — fondos, texto, filetes y los tokens de Ant Design (`colorPrimary`, `colorBgContainer`). Nada queda sin invertir; un botón invisible en el negativo es un defecto del mundo, no un detalle.
**La Regla de la Tinta Única.** El primario es una sola tinta. El color aparece únicamente como estado funcional; si un color no dice algo operativo (éxito, alerta, error), es decoración y va fuera.

## Typography

**Display Font:** Archivo (variable 100–900, autohospedada en `src/assets/fonts/archivo-var.woff2`, con fallback a la pila de sistema)
**Body Font:** pila de sistema (ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto)
**Label/Mono Font:** pila mono del sistema (ui-monospace, "SF Mono", "Cascadia Mono", Consolas) con `font-variant-numeric: tabular-nums`

**Character:** Archivo es la grotesca de imprenta — técnica, firme, sin nostalgia; la pila de sistema queda para el cuerpo de datos y la mono es la voz de máquina que mide. Tres voces, un oficio.

### Hierarchy
- **Display** (700, 26 px, -0.015em): título de página en la cabecera.
- **Headline** (700, 15 px): marca del taller en el riel.
- **Title** (700, 14 px, 1.15): título de sección dentro de una hoja.
- **Body** (400, 13 px, 1.5): cuerpo y mesas densas; prosa corrida a máx. 65–75 ch.
- **Label** (500 mono, 10 px, +0.14em, mayúsculas): etiquetas de especificación, códigos, conteos, rótulos de navegación.
- **Value** (700 Archivo, 24 px): cifras de la banda de especificaciones.

### Named Rules
**La Regla de la Letra Medida.** La mono es para datos: códigos `IP-XXXX`, hashes, fechas, kilómetros, pesos de cola. Si un texto no se mide, no va en mono.

## Layout

Riel izquierdo fijo de 224 px (papel, filete derecho de 1 px) con seis ítems de negocio; el área principal con cabecera (título de página + conmutador positivo/negativo) y contenido a máx. 1152 px. La densidad es de ficha: bandas de especificaciones divididas por filetes (5 columnas en escritorio, 2 en móvil), mesas `size="small"` con padding vertical de 10 px, formularios compactos. El ritmo: más aire encima de un título que debajo. En móvil (≤768 px) el riel colapsa su contenido, la banda pasa a 2 columnas con filetes horizontales, y las mesas hacen scroll horizontal.

## Elevation & Depth

No hay sombras. La profundidad es tonal: hoja (papel) → panel (papel-de-panel) → detalle con filete punteado. Un `backdrop-blur` funcional existe solo en la cabecera pegajosa (95 % de opacidad) por legibilidad al hacer scroll. El único movimiento de profundidad es la inversión completa del sistema en el conmutador de tema.

**La Regla del Filete.** Un filete de 1 px divide; una sombra oculta. Si dos superficies necesitan separarse, se separan con `border` o con un paso tonal, nunca con `box-shadow`.

## Shapes

Esquinas de control a 2 px (botones, tags, inputs) y 0 px para hojas y bandas — la ficha se corta recta. Los bordes son la gramática: sólido de 1 px para estructura, punteado para lo vacío (NULL, zonas sin datos). No hay círculos decorativos ni máscaras geométricas; el único silueta memorable es el bloque de tinta de la marca con el diafragma.

## Components

### Buttons
- **Shape:** rectángulo de 2 px.
- **Primary:** bloque de tinta con texto blanco; en negativo, bloque papel con texto de archivo (12.2:1 contra el suelo). Sin sombra.
- **Hover / Focus:** opacidad 85 % en 150 ms; focus visible con anillo de 2 px de tinta (offset 2 px).

### Chips (Tags de estado)
- **Style:** 2 px, texto del color funcional sobre fondo derivado; en claro el "En proceso" es chip de tinta con texto blanco.
- **State:** nunca decorativos; cada color afirma un estado operativo.

### Cards / Containers (Hojas)
- **Corner:** 0 px.
- **Background:** papel sobre suelo de papel; panel para interior.
- **Border:** filete de 1 px; punteado para vacío.
- **Internal Padding:** 24 px.

### Inputs / Fields
- **Style:** 1 px de filete, fondo de papel, 2 px.
- **Focus:** el filete pasa a tinta; el caret y la selección ya vienen tematizados (selección: tinta sobre papel; en negativo, invertido).

### Navigation
- **Style:** ítems de texto de 13 px con icono de trazo 2; inactivo en plata, hover a tinta.
- **Active:** bloque de tinta con borde izquierdo de 2 px y texto de papel; en negativo, invertido.
- **Toggle de tema:** rotulado POSITIVO/NEGATIVO en mono 10 px — es el movimiento firma del mundo.

### Banda de Especificaciones (componente firma)
Cifras del taller en una rejilla dividida por filetes: etiqueta mono de 10 px en plata + valor Archivo 24 px en tinta + nota de 11 px. Es una línea de ficha técnica, no tarjetas; en móvil reparte en 2 columnas.

## Do's and Don'ts

### Do:
- **Do** medir los contrastes: texto de 10–11 px exige ≥4.5:1 en ambos modos.
- **Do** tematizar las superficies del navegador: selección, caret, scrollbar, focus y numerales tabulares llevan la paleta.
- **Do** nombrar errores con problema y recuperación ("Verifica que el backend esté corriendo en el puerto 8000").
- **Do** conservar el español del taller: `IP-XXXX`, `Solicitado/En proceso/Listo/Entregado`, turnos mañana/tarde/noche.

### Don't:
- **Don't** usar blanco puro (#FFFFFF) ni negro puro (#000000): el papel es #FAFAF8 y el negativo #111110.
- **Don't** usar degradados, glass decorativo, `border-left` de color en tarjetas, tarjetas icono+título+texto como estructura, kickers sobre títulos ni emoji como iconos.
- **Don't** decorar con mono: la mono mide; si no es dato, no va en mono.
- **Don't** conectar lógica académica en el frontend: los algoritmos viven en el backend y el UI solo consume HTTP.
