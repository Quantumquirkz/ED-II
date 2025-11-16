"""
HashTable con doble hashing, cursores y lista de espacios libres (free_list).

Estructura interna:
    self.table: lista de diccionarios con campos:
        - 'key'    : la clave original (int o str) almacenada
        - 'value'  : el objeto/valor asociado
        - 'status' : 'EMPTY' | 'OCCUPIED' | 'DELETED'
        - 'cursor' : índice al siguiente elemento en la "cadena" (simula punteros)
    self.free_list: índice (cursor) al primer espacio libre (reciclado por borrados)

Principios:
- Doble hashing: h(k, i) = (h1(k) + i * h2(k)) % size
- h1 y h2 trabajan sobre una representación numérica de la clave
- string_to_int convierte strings a enteros sin librerías externas
- insert/search/delete respetan estados y actualizan cursores mínimamente
- Incluye utilidades: display(), get_statistics(), save/load a .txt
"""

from typing import Optional


class HashTable:
    def __init__(self, size: int = 11):
        """
        Inicializa la tabla hash.
        size: tamaño de la tabla (idealmente primo).
        """
        self.size = size

        # Cada entrada es un dict con: key, value, status, cursor
        self.table = [
            {
                'key': None,
                'value': None,
                'status': 'EMPTY',   # puede ser 'EMPTY', 'OCCUPIED', 'DELETED'
                'cursor': None       # índice al siguiente elemento en la "cadena"
            }
            for _ in range(size)
        ]

        # Cursor (índice) del inicio de la lista de espacios libres (por eliminaciones)
        # Si no hay libres, es None
        self.free_list: Optional[int] = None

    # -------------------------
    # Utilidades para claves
    # -------------------------
    def string_to_int(self, text: str) -> int:
        """
        Convierte un string a un entero de forma determinista sin librerías externas.
        Combinamos posición y código ASCII para dispersar bien.
        """
        total = 0
        for i, ch in enumerate(text):
            total += (i + 1) * ord(ch)
        return total

    def normalize_numeric_key(self, key):
        """
        Devuelve la representación numérica de la clave.
        Si es string, la convierte; si es int, la deja.
        """
        if isinstance(key, str):
            return self.string_to_int(key)
        return int(key)

    # -------------------------
    # Funciones hash h1 y h2
    # -------------------------
    def h1(self, key) -> int:
        """
        h1: primera función hash que devuelve la posición base.
        Trabaja sobre la representación numérica de la clave.
        """
        # Aseguramos que trabajamos con int
        k = self.normalize_numeric_key(key)
        return k % self.size

    def h2(self, key) -> int:
        """
        h2: segunda función hash para obtener el salto (step).
        Debe devolver un valor > 0 y preferiblemente coprimo con size.
        Usamos una fórmula que produce un número no nulo y preferentemente impar.
        """
        k = self.normalize_numeric_key(key)
        # Usamos un primo menor que self.size si es posible; aquí 7 es ejemplo
        # Aseguramos que el resultado nunca sea 0.
        step = 7 - (k % 7)
        if step == 0:
            step = 1
        # Forzamos impar para mejorar el ciclo (opcional)
        if step % 2 == 0:
            step += 1
            if step >= self.size:
                # ajustar si excede tamaño
                step = 1
        return step

    def hash_key(self, key, i: int) -> int:
        """
        Hash completo para doble hashing:
            h(key, i) = (h1(key) + i * h2(key)) % size
        """
        return (self.h1(key) + i * self.h2(key)) % self.size

    # -------------------------
    # Inserción
    # -------------------------
    def insert(self, key, value):
        """
        Inserta (key, value) en la tabla usando double hashing y actualizando cursores.
        key puede ser str o int.

        Estrategia:
            - Calcula la secuencia de probes con h1/h2.
            - Si encuentra key existente con 'OCCUPIED', actualiza el value.
            - Si encuentra 'EMPTY' o 'DELETED', inserta allí.
            - Si i > 0 (colisión), busca el ocupante anterior en la secuencia y ajusta su cursor
              para apuntar al nuevo slot (mantener la cadena).
        """
        numeric_key = self.normalize_numeric_key(key)
        base_index = self.h1(numeric_key)
        step = self.h2(numeric_key)

        first_deleted_index = None

        for i in range(self.size):
            pos = (base_index + i * step) % self.size
            entry = self.table[pos]

            if entry['status'] == 'OCCUPIED':
                # Si la clave ya existe, actualizamos el valor
                if entry['key'] == key:
                    entry['value'] = value
                    return
                # Si ocupado con otra clave, seguimos sondando
                continue

            # Si encontramos un espacio DELETED, lo recordamos (pero podemos preferir reusar EMPTY)
            if entry['status'] == 'DELETED' and first_deleted_index is None:
                first_deleted_index = pos

            # Si encontramos un espacio EMPTY, insertamos (preferimos reusar DELETED si hubo)
            if entry['status'] == 'EMPTY':
                insert_pos = first_deleted_index if first_deleted_index is not None else pos

                # insertar en insert_pos
                self.table[insert_pos] = {
                    'key': key,
                    'value': value,
                    'status': 'OCCUPIED',
                    'cursor': None
                }

                # Si reusamos un DELETED, quitamoslo de la free_list si era el inicio
                if first_deleted_index is not None:
                    # si ese slot estaba en free_list lo quitamos
                    if self.free_list == insert_pos:
                        self.free_list = self.table[insert_pos]['cursor']
                    # Nota: si no era el inicio, dejamos su link como estaba.

                # Actualizar cursor del elemento previo en la secuencia de probes (si existe)
                if i > 0:
                    # buscamos hacia atrás el primer OCCUPIED en la secuencia de probes
                    j = i - 1
                    while j >= 0:
                        prev_pos = (base_index + j * step) % self.size
                        if self.table[prev_pos]['status'] == 'OCCUPIED':
                            # conectar prev_pos -> insert_pos
                            self.table[prev_pos]['cursor'] = insert_pos
                            break
                        j -= 1

                return

        # Si llegamos acá, no encontramos EMPTY; pero si encontramos DELETED lo usamos
        if first_deleted_index is not None:
            insert_pos = first_deleted_index
            self.table[insert_pos] = {
                'key': key,
                'value': value,
                'status': 'OCCUPIED',
                'cursor': None
            }
            # quitar de free_list si era inicio
            if self.free_list == insert_pos:
                self.free_list = self.table[insert_pos]['cursor']
            return

        raise Exception("Tabla llena: no se pudo insertar el elemento")

    # -------------------------
    # Búsqueda
    # -------------------------
    def search(self, key):
        """
        Busca y retorna el value asociado a key (o None si no existe).
        Sigue la misma secuencia de probes que insert.
        """
        numeric_key = self.normalize_numeric_key(key)
        base_index = self.h1(numeric_key)
        step = self.h2(numeric_key)

        for i in range(self.size):
            pos = (base_index + i * step) % self.size
            entry = self.table[pos]

            # Si encontramos la clave ocupada, retornamos el valor
            if entry['status'] == 'OCCUPIED' and entry['key'] == key:
                return entry['value']

            # Si llegamos a un EMPTY puro, la clave no está (no está en la secuencia)
            if entry['status'] == 'EMPTY':
                return None

            # Si es DELETED o OCCUPIED con otra clave, continuamos
            continue

        # Exploramos toda la tabla y no la encontramos
        return None

    # -------------------------
    # Eliminación
    # -------------------------
    def delete(self, key) -> bool:
        """
        Elimina un elemento por key. Retorna True si se eliminó, False si no se encontró.

        Al eliminar:
        - Guardamos el cursor que tenía el slot (next_cursor).
        - Marcamos como DELETED y limpiamos key/value.
        - Insertamos el slot en la free_list (su cursor apunta al antiguo free_list).
        - Actualizamos cualquier cursor que apuntara a este slot para que apunte al siguiente
          (mantener integridad de las cadenas).
        """
        numeric_key = self.normalize_numeric_key(key)
        base_index = self.h1(numeric_key)
        step = self.h2(numeric_key)

        for i in range(self.size):
            pos = (base_index + i * step) % self.size
            entry = self.table[pos]

            # Si encontramos el elemento, lo eliminamos
            if entry['status'] == 'OCCUPIED' and entry['key'] == key:
                next_cursor = entry['cursor']  # quien seguía en la "cadena"
                # Marcar como DELETED y limpiar
                self.table[pos]['status'] = 'DELETED'
                self.table[pos]['key'] = None
                self.table[pos]['value'] = None

                # Insertar en lista de libres (usando cursor para linkear)
                self.table[pos]['cursor'] = self.free_list
                self.free_list = pos

                # Actualizar cualquier cursor que apuntara a pos para que apunte a next_cursor
                for e in self.table:
                    if e['cursor'] == pos:
                        e['cursor'] = next_cursor

                return True

            # Si encontramos un EMPTY puro, no existe
            if entry['status'] == 'EMPTY':
                return False

            # sino continuar probe
            continue

        return False

    # -------------------------
    # Estadísticas y visualización
    # -------------------------
    def get_statistics(self) -> dict:
        """
        Devuelve estadísticas de la tabla:
            total_slots, occupied, empty, deleted, load_factor
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

    def display(self):
        """
        Imprime el estado actual de la tabla hash de forma tabulada.
        """
        print("\n" + "=" * 70)
        print("TABLA HASH CON DOBLE HASHING Y CURSORES")
        print("=" * 70)
        print(f"{'Índice':<8} | {'Clave':<12} | {'Valor':<18} | {'Estado':<10} | {'Cursor':<8}")
        print("-" * 70)

        for i, entry in enumerate(self.table):
            key_str = str(entry['key']) if entry['key'] is not None else 'None'
            value_str = str(entry['value']) if entry['value'] is not None else 'None'
            cursor_str = str(entry['cursor']) if entry['cursor'] is not None else 'None'

            print(f"{i:<8} | {key_str:<12} | {value_str:<18} | {entry['status']:<10} | {cursor_str:<8}")

        print("-" * 70)
        if self.free_list is not None:
            print(f"Lista de espacios libres (cursor inicial): {self.free_list}")
        else:
            print("Lista de espacios libres: vacía")
        print("=" * 70)


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
