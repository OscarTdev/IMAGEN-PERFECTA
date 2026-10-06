from collections import deque
import heapq
from datetime import datetime
from typing import Optional

class Nodo:
    """Nodo para la Lista Enlazada."""
    def __init__(self, valor: str):
        self.valor = valor
        self.siguiente: Optional['Nodo'] = None

class ListaEnlazada:
    """Implementación manual de una Lista Enlazada para las etapas de producción."""
    def __init__(self):
        self.cabeza: Optional[Nodo] = None
    
    def agregar(self, valor: str) -> None:
        """Agrega un nuevo nodo al final de la lista."""
        nuevo_nodo = Nodo(valor)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
            return
        
        actual = self.cabeza
        while actual.siguiente:
            actual = actual.siguiente
        actual.siguiente = nuevo_nodo

    def recorrer(self) -> list[str]:
        """Recorre la lista y retorna una lista de Python con los valores."""
        elementos = []
        actual = self.cabeza
        while actual:
            elementos.append(actual.valor)
            actual = actual.siguiente
        return elementos

    def to_dict(self) -> dict:
        """Retorna una representación en diccionario de la estructura."""
        elementos = self.recorrer()
        estructura_str = " → ".join(elementos) + (" → NULL" if elementos else "NULL")
        return {
            "tipo": "Lista Enlazada",
            "descripcion": "Estructura lineal donde cada elemento apunta al siguiente. Usada para el flujo de producción.",
            "etapas": elementos,
            "estructura": estructura_str
        }

class Pila:
    """Implementación de una Pila (LIFO) usando una lista de Python para el historial de acciones."""
    def __init__(self):
        self._items: list[dict] = []
    
    def push(self, accion: dict) -> None:
        """Agrega una acción a la cima de la pila."""
        self._items.append(accion)
    
    def pop(self) -> Optional[dict]:
        """Extrae y retorna la acción en la cima de la pila."""
        if not self.is_empty():
            return self._items.pop()
        return None
    
    def peek(self) -> Optional[dict]:
        """Retorna la acción en la cima de la pila sin extraerla."""
        if not self.is_empty():
            return self._items[-1]
        return None
    
    def size(self) -> int:
        """Retorna el número de elementos en la pila."""
        return len(self._items)
        
    def is_empty(self) -> bool:
        """Verifica si la pila está vacía."""
        return len(self._items) == 0

    def to_dict(self) -> dict:
        """Retorna una representación en diccionario de la estructura."""
        return {
            "tipo": "Pila (LIFO)",
            "descripcion": "Estructura donde el último en entrar es el primero en salir. Usada para el historial de acciones recientes.",
            "items": list(reversed(self._items)),  # Mostramos del más reciente al más antiguo
            "tamanio": self.size(),
            "tope": self.peek()
        }

class Cola:
    """Implementación de una Cola (FIFO) usando collections.deque para la cola de producción."""
    def __init__(self):
        self._items: deque = deque()
    
    def enqueue(self, pedido: dict) -> None:
        """Agrega un pedido al final de la cola."""
        self._items.append(pedido)
    
    def dequeue(self) -> Optional[dict]:
        """Extrae y retorna el pedido al inicio de la cola."""
        if not self.is_empty():
            return self._items.popleft()
        return None
    
    def peek(self) -> Optional[dict]:
        """Retorna el pedido al inicio de la cola sin extraerlo."""
        if not self.is_empty():
            return self._items[0]
        return None
    
    def size(self) -> int:
        """Retorna el número de elementos en la cola."""
        return len(self._items)
        
    def is_empty(self) -> bool:
        """Verifica si la cola está vacía."""
        return len(self._items) == 0

    def to_dict(self) -> dict:
        """Retorna una representación en diccionario de la estructura."""
        return {
            "tipo": "Cola (FIFO)",
            "descripcion": "Estructura donde el primero en entrar es el primero en salir. Usada para la cola de producción estándar.",
            "items": list(self._items),
            "tamanio": self.size(),
            "proximo": self.peek()
        }

class ColaPrioridad:
    """Implementación de una Cola de Prioridad usando heapq para pedidos con urgencia."""
    def __init__(self):
        self._heap: list = []
        self._counter: int = 0
    
    def insertar(self, pedido: dict, prioridad: int) -> None:
        """Inserta un pedido en la cola de prioridad."""
        # heapq es min-heap, menor número = mayor prioridad
        heapq.heappush(self._heap, (prioridad, self._counter, pedido))
        self._counter += 1
    
    def extraer(self) -> Optional[dict]:
        """Extrae y retorna el pedido con mayor prioridad (menor número)."""
        if not self.is_empty():
            prioridad, count, pedido = heapq.heappop(self._heap)
            return pedido
        return None
    
    def peek(self) -> Optional[dict]:
        """Retorna el pedido con mayor prioridad sin extraerlo."""
        if not self.is_empty():
            prioridad, count, pedido = self._heap[0]
            return pedido
        return None
    
    def size(self) -> int:
        """Retorna el número de elementos en la cola de prioridad."""
        return len(self._heap)
        
    def is_empty(self) -> bool:
        """Verifica si la cola está vacía."""
        return len(self._heap) == 0

    def to_dict(self) -> dict:
        """Retorna una representación en diccionario de la estructura."""
        # Retorna copias sin modificar el heap actual
        items_ordenados = []
        heap_copia = list(self._heap)
        heapq.heapify(heap_copia)
        
        while heap_copia:
            pri, count, ped = heapq.heappop(heap_copia)
            items_ordenados.append({
                "prioridad": pri,
                "pedido": ped
            })
            
        return {
            "tipo": "Heap / Cola de Prioridad",
            "descripcion": "Estructura donde el elemento con mayor prioridad sale primero. Usada para pedidos urgentes.",
            "items": items_ordenados,
            "tamanio": self.size(),
            "proximo": self.peek(),
            "explicacion": "Prioridades: Urgente=1, Alta=2, Normal=3. Menor número implica mayor prioridad en el Heap."
        }

# Instancias a nivel de módulo
lista_produccion = ListaEnlazada()
for etapa in ['Impresión', 'Acabado', 'Enmarcado', 'Empaque', 'Despachado']:
    lista_produccion.agregar(etapa)

pila_historial = Pila()
acciones_iniciales = [
    'Crear pedido IP-0001',
    'Agregar producto: Marco dorado',
    'Cambiar estado a En proceso',
    'Modificar cantidad a 5',
    'Crear pedido IP-0002'
]
for acc in acciones_iniciales:
    pila_historial.push({"accion": acc, "detalle": "Acción del sistema", "timestamp": datetime.now().isoformat()})

cola_produccion = Cola()
cola_produccion.enqueue({"codigo": "IP-0001", "cliente": "Juan Perez", "productos": "Marco Dorado", "fecha": "2023-10-01"})
cola_produccion.enqueue({"codigo": "IP-0002", "cliente": "Maria Lopez", "productos": "Foto 10x15", "fecha": "2023-10-02"})

heap_prioridad = ColaPrioridad()
heap_prioridad.insertar({"codigo": "IP-0003", "cliente": "Carlos Ruiz", "productos": "Foto Carnet"}, 3) # Normal
heap_prioridad.insertar({"codigo": "IP-0004", "cliente": "Ana Torres", "productos": "Retrato Grande"}, 1) # Urgente
heap_prioridad.insertar({"codigo": "IP-0005", "cliente": "Luis Gomez", "productos": "Album de bodas"}, 2) # Alta
