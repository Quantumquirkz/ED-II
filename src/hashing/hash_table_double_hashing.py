"""
Tabla Hash con Doble Hashing y Cursores

Características:
- Funciones hash: h1(key) y h2(key) para calcular posiciones
- Manejo de colisiones: Direccionamiento abierto con doble hashing
- Cursores: Simulación de punteros usando índices de la tabla
- Operaciones: Inserción, búsqueda, eliminación y visualización de la tabla
"""


class HashTable:
    """Implementación de tabla hash con doble hashing y cursores."""
    
    def __init__(self, size=11):
        """
        Inicializa la tabla hash.
        
        Args:
            size: Tamaño de la tabla (debe ser un número primo)
        """
        self.size = size
        # Cada entrada contiene: key, value, status y cursor (índice siguiente)
        self.table = [
            {
                'key': None,
                'value': None,
                'status': 'EMPTY',
                'cursor': None  # Simulación de puntero usando índice
            }
            for _ in range(size)
        ]
        # Lista de índices libres (para gestión de memoria con cursores)
        self.free_list = None  # Cursor al inicio de la lista de espacios libres

    def h1(self, key):
        """
        Primera función hash: calcula la posición inicial.
        
        Args:
            key: Clave a hashear
            
        Returns:
            Posición inicial en la tabla
        """
        return key % self.size

    def h2(self, key):
        """
        Segunda función hash: calcula el salto para doble hashing.
        
        Args:
            key: Clave a hashear
            
        Returns:
            Incremento para resolver colisiones
        """
        # Usa un número primo menor que el tamaño de la tabla
        return 7 - (key % 7)

    def insert(self, key, value):
        """
        Inserta un par clave-valor en la tabla.
        
        Args:
            key: Clave a insertar
            value: Valor asociado a la clave
            
        Raises:
            Exception: Si la tabla está llena
        """
        index = self.h1(key)
        i = 0
        
        while True:
            pos = (index + i * self.h2(key)) % self.size
            
            # Si la posición está vacía o fue eliminada
            if self.table[pos]['status'] == 'EMPTY' or self.table[pos]['status'] == 'DELETED':
                # Si es una posición eliminada, actualizamos la lista de libres
                if self.table[pos]['status'] == 'DELETED':
                    # Remover de la lista de libres si está ahí
                    if self.free_list == pos:
                        self.free_list = self.table[pos]['cursor']
                
                # Insertar el nuevo elemento
                self.table[pos] = {
                    'key': key,
                    'value': value,
                    'status': 'OCCUPIED',
                    'cursor': None
                }
                
                # Actualizar cursor si hay colisiones previas
                if i > 0:
                    # Buscar el elemento anterior en la secuencia de sondas
                    prev_pos = (index + (i - 1) * self.h2(key)) % self.size
                    j = i - 1
                    while j >= 0:
                        check_pos = (index + j * self.h2(key)) % self.size
                        if self.table[check_pos]['status'] == 'OCCUPIED':
                            self.table[check_pos]['cursor'] = pos
                            break
                        j -= 1
                
                return
            
            # Si la clave ya existe, actualizar el valor
            if self.table[pos]['key'] == key and self.table[pos]['status'] == 'OCCUPIED':
                self.table[pos]['value'] = value
                return
            
            i += 1
            if i >= self.size:
                raise Exception("Tabla llena: No se puede insertar más elementos")

    def search(self, key):
        """
        Busca un valor en la tabla usando su clave.
        
        Args:
            key: Clave a buscar
            
        Returns:
            Valor asociado a la clave, o None si no se encuentra
        """
        index = self.h1(key)
        i = 0
        current = index  # Cursor actual para seguir la secuencia
        
        while True:
            pos = (index + i * self.h2(key)) % self.size
            
            # Si encontramos la clave y está ocupada
            if self.table[pos]['key'] == key and self.table[pos]['status'] == 'OCCUPIED':
                return self.table[pos]['value']
            
            # Si encontramos un espacio vacío, la clave no existe
            if self.table[pos]['status'] == 'EMPTY':
                return None
            
            # Seguir con el siguiente usando el cursor o la fórmula
            i += 1
            if i >= self.size:
                return None

    def delete(self, key):
        """
        Elimina un elemento de la tabla usando su clave.
        
        Args:
            key: Clave del elemento a eliminar
        """
        index = self.h1(key)
        i = 0
        
        while True:
            pos = (index + i * self.h2(key)) % self.size
            
            # Si encontramos la clave y está ocupada
            if self.table[pos]['key'] == key and self.table[pos]['status'] == 'OCCUPIED':
                # Guardar el cursor antes de marcar como eliminado
                next_cursor = self.table[pos]['cursor']
                
                # Marcar como eliminado (no vaciar completamente para mantener la secuencia)
                self.table[pos]['status'] = 'DELETED'
                self.table[pos]['key'] = None
                self.table[pos]['value'] = None
                
                # Agregar a la lista de espacios libres usando cursores
                self.table[pos]['cursor'] = self.free_list
                self.free_list = pos
                
                return
            
            # Si encontramos un espacio vacío, la clave no existe
            if self.table[pos]['status'] == 'EMPTY':
                return
            
            i += 1
            if i >= self.size:
                return

    def display(self):
        """Muestra el estado actual de la tabla hash."""
        print("\n" + "="*70)
        print("TABLA HASH CON DOBLE HASHING Y CURSORES")
        print("="*70)
        print(f"{'Índice':<8} | {'Clave':<8} | {'Valor':<10} | {'Estado':<12} | {'Cursor':<8}")
        print("-"*70)
        
        for i, entry in enumerate(self.table):
            key_str = str(entry['key']) if entry['key'] is not None else 'None'
            value_str = str(entry['value']) if entry['value'] is not None else 'None'
            cursor_str = str(entry['cursor']) if entry['cursor'] is not None else 'None'
            
            print(f"{i:<8} | {key_str:<8} | {value_str:<10} | {entry['status']:<12} | {cursor_str:<8}")
        
        print("-"*70)
        if self.free_list is not None:
            print(f"Lista de espacios libres (cursor inicial): {self.free_list}")
        else:
            print("Lista de espacios libres: vacía")
        print("="*70)

    def get_statistics(self):
        """
        Obtiene estadísticas de la tabla hash.
        
        Returns:
            Diccionario con estadísticas de la tabla
        """
        occupied = sum(1 for entry in self.table if entry['status'] == 'OCCUPIED')
        empty = sum(1 for entry in self.table if entry['status'] == 'EMPTY')
        deleted = sum(1 for entry in self.table if entry['status'] == 'DELETED')
        
        return {
            'total_slots': self.size,
            'occupied': occupied,
            'empty': empty,
            'deleted': deleted,
            'load_factor': occupied / self.size if self.size > 0 else 0
        }


def main():
    """Función principal con ejemplos de uso."""
    print("="*70)
    print("DEMOSTRACIÓN: TABLA HASH CON DOBLE HASHING Y CURSORES")
    print("="*70)
    
    # Crear tabla hash
    ht = HashTable(size=11)
    
    print("\n1. INSERTANDO ELEMENTOS")
    print("-"*70)
    
    # Insertar varios elementos
    elementos = [
        (10, "A"), (22, "B"), (31, "C"), (4, "D"), (15, "E"),
        (28, "F"), (17, "G"), (88, "H"), (59, "I")
    ]
    
    for key, value in elementos:
        try:
            ht.insert(key, value)
            print(f"✓ Insertado: clave={key}, valor={value}")
        except Exception as e:
            print(f"✗ Error al insertar {key}: {e}")
    
    # Mostrar tabla
    ht.display()
    
    # Mostrar estadísticas
    stats = ht.get_statistics()
    print("\nESTADÍSTICAS:")
    print(f"  - Ocupadas: {stats['occupied']}/{stats['total_slots']}")
    print(f"  - Vacías: {stats['empty']}")
    print(f"  - Eliminadas: {stats['deleted']}")
    print(f"  - Factor de carga: {stats['load_factor']:.2%}")
    
    print("\n2. BÚSQUEDAS")
    print("-"*70)
    
    # Buscar elementos
    busquedas = [22, 99, 15, 31, 100]
    for key in busquedas:
        resultado = ht.search(key)
        if resultado is not None:
            print(f"✓ Encontrado: clave={key} -> valor={resultado}")
        else:
            print(f"✗ No encontrado: clave={key}")
    
    print("\n3. ELIMINACIÓN DE ELEMENTOS")
    print("-"*70)
    
    # Eliminar algunos elementos
    eliminar = [22, 15]
    for key in eliminar:
        ht.delete(key)
        print(f"✓ Eliminado: clave={key}")
    
    # Mostrar tabla después de eliminar
    ht.display()
    
    print("\n4. BÚSQUEDAS DESPUÉS DE ELIMINACIÓN")
    print("-"*70)
    
    # Verificar que los eliminados ya no existen
    verificar = [22, 15, 31]
    for key in verificar:
        resultado = ht.search(key)
        if resultado is not None:
            print(f"✓ Encontrado: clave={key} -> valor={resultado}")
        else:
            print(f"✗ No encontrado: clave={key}")
    
    print("\n5. REINSERCIÓN EN ESPACIOS LIBRES")
    print("-"*70)
    
    # Reinsertar en espacios previamente eliminados
    ht.insert(22, "B_NUEVO")
    ht.insert(15, "E_NUEVO")
    print("✓ Reinsertados elementos en espacios previamente eliminados")
    
    ht.display()
    
    print("\n" + "="*70)
    print("DEMOSTRACIÓN COMPLETADA")
    print("="*70)


if __name__ == "__main__":
    main()
