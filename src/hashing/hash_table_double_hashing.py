"""
HashTable con doble hashing, cursores y lista de espacios libres (free_list).

Implementación de una tabla hash que utiliza doble hashing para resolver colisiones,
con un sistema de cursores para mantener referencias entre elementos relacionados
y una lista de espacios libres para reutilizar slots eliminados.

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
"""

from typing import Optional, Union, Any


# Constantes para los estados de las entradas
STATUS_EMPTY = 'EMPTY'
STATUS_OCCUPIED = 'OCCUPIED'
STATUS_DELETED = 'DELETED'


class HashTable:
    """
    Tabla hash con doble hashing, cursores y lista de espacios libres.
    
    Esta implementación utiliza doble hashing para resolver colisiones,
    manteniendo un sistema de cursores para referenciar elementos relacionados
    y una lista de espacios libres para reutilizar slots eliminados.
    
    Args:
        size: Tamaño de la tabla (debe ser un número primo para mejor distribución).
              Por defecto es 11.
    
    Raises:
        ValueError: Si el tamaño es menor o igual a 0.
    """
    
    def __init__(self, size: int = 11):
        """
        Inicializa la tabla hash.
        
        Args:
            size: Tamaño de la tabla (idealmente primo).
        
        Raises:
            ValueError: Si size <= 0.
        """
        if size <= 0:
            raise ValueError(f"El tamaño de la tabla debe ser mayor a 0. Recibido: {size}")
        
        self.size = size

        # Cada entrada es un dict con: key, value, status, cursor
        self.table = [
            {
                'key': None,
                'value': None,
                'status': STATUS_EMPTY,
                'cursor': None
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
        
        Utiliza la posición y el código ASCII de cada carácter para crear
        un hash determinista que dispersa bien los valores.
        
        Args:
            text: String a convertir.
        
        Returns:
            Entero que representa el string.
        """
        total = 0
        for i, ch in enumerate(text):
            total += (i + 1) * ord(ch)
        return total

    def normalize_numeric_key(self, key: Union[int, str]) -> int:
        """
        Devuelve la representación numérica de la clave.
        
        Args:
            key: Clave que puede ser int o str.
        
        Returns:
            Representación numérica de la clave.
        
        Raises:
            TypeError: Si la clave no es int ni str.
        """
        if isinstance(key, str):
            return self.string_to_int(key)
        elif isinstance(key, int):
            return int(key)
        else:
            raise TypeError(f"La clave debe ser int o str. Recibido: {type(key).__name__}")

    # -------------------------
    # Funciones hash h1 y h2
    # -------------------------
    def h1(self, key: Union[int, str]) -> int:
        """
        Primera función hash que devuelve la posición base.
        
        Calcula la posición inicial en la tabla usando el módulo del tamaño.
        
        Args:
            key: Clave (int o str) a hashear.
        
        Returns:
            Posición base en la tabla (0 a size-1).
        """
        k = self.normalize_numeric_key(key)
        return k % self.size

    def h2(self, key: Union[int, str]) -> int:
        """
        Segunda función hash para obtener el salto (step) en caso de colisión.
        
        Debe devolver un valor > 0 y preferiblemente coprimo con size.
        Usa una fórmula que produce un número no nulo y preferentemente impar.
        
        Args:
            key: Clave (int o str) a hashear.
        
        Returns:
            Valor del salto para resolver colisiones (siempre > 0).
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
                # Ajustar si excede tamaño
                step = 1
        return step

    def hash_key(self, key: Union[int, str], i: int) -> int:
        """
        Hash completo para doble hashing.
        
        Calcula la posición usando la fórmula:
            h(key, i) = (h1(key) + i * h2(key)) % size
        
        Args:
            key: Clave a hashear.
            i: Número de intento (0 para posición inicial, 1, 2, ... para colisiones).
        
        Returns:
            Posición calculada en la tabla.
        """
        return (self.h1(key) + i * self.h2(key)) % self.size

    # -------------------------
    # Inserción
    # -------------------------
    def insert(self, key: Union[int, str], value: Any) -> bool:
        """
        Inserta (key, value) en la tabla usando double hashing y actualizando cursores.
        
        Si la clave ya existe, actualiza el valor. Si hay colisiones, utiliza
        doble hashing para encontrar una posición libre. Reutiliza espacios DELETED
        cuando es posible.
        
        Args:
            key: Clave del elemento (puede ser str o int).
            value: Valor asociado a la clave.
        
        Returns:
            True si se insertó exitosamente, False si la tabla está llena.
        """
        numeric_key = self.normalize_numeric_key(key)
        base_index = self.h1(numeric_key)
        step = self.h2(numeric_key)

        first_deleted_index = None

        for i in range(self.size):
            pos = (base_index + i * step) % self.size
            entry = self.table[pos]

            if entry['status'] == STATUS_OCCUPIED:
                # Si la clave ya existe, actualizamos el valor
                if entry['key'] == key:
                    entry['value'] = value
                    return True
                # Si ocupado con otra clave, seguimos sondando
                continue

            # Si encontramos un espacio DELETED, lo recordamos
            if entry['status'] == STATUS_DELETED and first_deleted_index is None:
                first_deleted_index = pos

            # Si encontramos un espacio EMPTY, insertamos
            if entry['status'] == STATUS_EMPTY:
                insert_pos = first_deleted_index if first_deleted_index is not None else pos

                # Insertar en insert_pos
                self.table[insert_pos] = {
                    'key': key,
                    'value': value,
                    'status': STATUS_OCCUPIED,
                    'cursor': None
                }

                # Si reusamos un DELETED, quitamoslo de la free_list si era el inicio
                if first_deleted_index is not None:
                    self._remove_from_free_list(insert_pos)

                # Actualizar cursor del elemento previo en la secuencia de probes (si existe)
                if i > 0:
                    self._update_previous_cursor(base_index, step, i, insert_pos)

                return True

        # Si llegamos acá, no encontramos EMPTY; pero si encontramos DELETED lo usamos
        if first_deleted_index is not None:
            insert_pos = first_deleted_index
            self.table[insert_pos] = {
                'key': key,
                'value': value,
                'status': STATUS_OCCUPIED,
                'cursor': None
            }
            self._remove_from_free_list(insert_pos)
            return True

        return False

    def _remove_from_free_list(self, pos: int) -> None:
        """
        Remueve un slot de la lista de espacios libres.
        
        Args:
            pos: Posición a remover de la free_list.
        """
        if self.free_list == pos:
            # Si es el inicio de la lista, actualizamos el inicio
            self.free_list = self.table[pos]['cursor']
        else:
            # Si no es el inicio, buscamos el anterior en la lista
            current = self.free_list
            while current is not None:
                if self.table[current]['cursor'] == pos:
                    self.table[current]['cursor'] = self.table[pos]['cursor']
                    break
                current = self.table[current]['cursor']

    def _update_previous_cursor(self, base_index: int, step: int, current_i: int, insert_pos: int) -> None:
        """
        Actualiza el cursor del elemento previo en la secuencia de probes.
        
        Args:
            base_index: Índice base calculado con h1.
            step: Paso calculado con h2.
            current_i: Índice actual en la secuencia de probes.
            insert_pos: Posición donde se insertó el nuevo elemento.
        """
        j = current_i - 1
        while j >= 0:
            prev_pos = (base_index + j * step) % self.size
            if self.table[prev_pos]['status'] == STATUS_OCCUPIED:
                self.table[prev_pos]['cursor'] = insert_pos
                break
            j -= 1

    # -------------------------
    # Búsqueda
    # -------------------------
    def search(self, key: Union[int, str]) -> Optional[Any]:
        """
        Busca y retorna el value asociado a key.
        
        Sigue la misma secuencia de probes que insert. Si encuentra un espacio
        EMPTY, significa que la clave no está en la tabla.
        
        Args:
            key: Clave a buscar.
        
        Returns:
            El valor asociado a la clave si existe, None en caso contrario.
        """
        numeric_key = self.normalize_numeric_key(key)
        base_index = self.h1(numeric_key)
        step = self.h2(numeric_key)

        for i in range(self.size):
            pos = (base_index + i * step) % self.size
            entry = self.table[pos]

            # Si encontramos la clave ocupada, retornamos el valor
            if entry['status'] == STATUS_OCCUPIED and entry['key'] == key:
                return entry['value']

            # Si llegamos a un EMPTY puro, la clave no está
            if entry['status'] == STATUS_EMPTY:
                return None

            # Si es DELETED o OCCUPIED con otra clave, continuamos
            # (el continue es implícito, pero lo dejamos para claridad)

        return None

    # -------------------------
    # Eliminación
    # -------------------------
    def delete(self, key: Union[int, str]) -> bool:
        """
        Elimina un elemento por key.
        
        Marca el slot como DELETED y lo agrega a la lista de espacios libres.
        Mantiene la integridad de los cursores actualizando referencias.
        
        Args:
            key: Clave del elemento a eliminar.
        
        Returns:
            True si se eliminó exitosamente, False si no se encontró.
        """
        numeric_key = self.normalize_numeric_key(key)
        base_index = self.h1(numeric_key)
        step = self.h2(numeric_key)

        for i in range(self.size):
            pos = (base_index + i * step) % self.size
            entry = self.table[pos]

            # Si encontramos el elemento, lo eliminamos
            if entry['status'] == STATUS_OCCUPIED and entry['key'] == key:
                next_cursor = entry['cursor']
                
                # Marcar como DELETED y limpiar
                self.table[pos]['status'] = STATUS_DELETED
                self.table[pos]['key'] = None
                self.table[pos]['value'] = None

                # Insertar en lista de libres (al inicio)
                self.table[pos]['cursor'] = self.free_list
                self.free_list = pos

                # Actualizar cualquier cursor que apuntara a pos
                self._update_cursors_pointing_to(pos, next_cursor)

                return True

            # Si encontramos un EMPTY puro, no existe
            if entry['status'] == STATUS_EMPTY:
                return False

        return False

    def _update_cursors_pointing_to(self, old_pos: int, new_pos: Optional[int]) -> None:
        """
        Actualiza todos los cursores que apuntaban a old_pos para que apunten a new_pos.
        
        Args:
            old_pos: Posición antigua que ya no existe.
            new_pos: Nueva posición a la que deben apuntar (puede ser None).
        """
        for entry in self.table:
            if entry['cursor'] == old_pos:
                entry['cursor'] = new_pos

    # -------------------------
    # Estadísticas y visualización
    # -------------------------
    def get_statistics(self) -> dict:
        """
        Devuelve estadísticas de la tabla.
        
        Returns:
            Diccionario con las siguientes claves:
                - total_slots: Tamaño total de la tabla
                - occupied: Número de slots ocupados
                - empty: Número de slots vacíos
                - deleted: Número de slots eliminados
                - load_factor: Factor de carga (occupied / total_slots)
        """
        occupied = sum(1 for entry in self.table if entry['status'] == STATUS_OCCUPIED)
        empty = sum(1 for entry in self.table if entry['status'] == STATUS_EMPTY)
        deleted = sum(1 for entry in self.table if entry['status'] == STATUS_DELETED)

        return {
            'total_slots': self.size,
            'occupied': occupied,
            'empty': empty,
            'deleted': deleted,
            'load_factor': occupied / self.size if self.size > 0 else 0.0
        }

    def display(self) -> None:
        """
        Imprime el estado actual de la tabla hash de forma tabulada.
        
        Muestra todas las entradas con su índice, clave, valor, estado y cursor.
        También muestra información sobre la lista de espacios libres.
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

    def show_double_hashing_process(self, key: Union[int, str], value: Any = None) -> None:
        """
        Muestra visualmente el proceso de doble hashing para una clave.
        
        Muestra paso a paso cómo se calculan h1, h2 y las posiciones
        en caso de colisiones, ilustrando cómo funciona el doble hashing.
        
        Args:
            key: Clave para la cual mostrar el proceso de hashing.
            value: Valor opcional para mostrar en el proceso.
        """
        numeric_key = self.normalize_numeric_key(key)
        base_index = self.h1(key)
        step = self.h2(key)
        
        print("\n" + "=" * 70)
        print(f"PROCESO DE DOBLE HASHING PARA CLAVE: {key}")
        print("=" * 70)
        
        # Mostrar información de la clave
        print(f"\nClave: {key}")
        print(f"Representación numérica: {numeric_key}")
        print(f"Tamaño de la tabla: {self.size}")
        
        # Calcular y mostrar h1
        print(f"\n{'─' * 70}")
        print("PASO 1: Calcular h1 (posición base)")
        print(f"{'─' * 70}")
        print(f"h1({key}) = {numeric_key} % {self.size} = {base_index}")
        print(f"→ Posición inicial: {base_index}")
        
        # Calcular y mostrar h2
        print(f"\n{'─' * 70}")
        print("PASO 2: Calcular h2 (salto para colisiones)")
        print(f"{'─' * 70}")
        k_mod_7 = numeric_key % 7
        step_calc = 7 - k_mod_7
        if step_calc == 0:
            step_calc = 1
        if step_calc % 2 == 0:
            step_calc += 1
            if step_calc >= self.size:
                step_calc = 1
        print(f"h2({key}) = 7 - ({numeric_key} % 7) = 7 - {k_mod_7} = {step_calc}")
        if step_calc != step:
            print(f"(Ajustado a impar si es necesario: {step})")
        print(f"→ Salto (step): {step}")
        
        # Mostrar secuencia de probes
        print(f"\n{'─' * 70}")
        print("PASO 3: Secuencia de posiciones (probes)")
        print(f"{'─' * 70}")
        print(f"Fórmula: pos = (h1 + i × h2) % size")
        print(f"         pos = ({base_index} + i × {step}) % {self.size}")
        print()
        
        print(f"{'Intento (i)':<12} | {'Cálculo':<25} | {'Posición':<12} | {'Estado':<15} | {'Acción'}")
        print("-" * 70)
        
        found = False
        for i in range(self.size):
            pos = (base_index + i * step) % self.size
            entry = self.table[pos]
            
            # Determinar estado y acción
            if entry['status'] == STATUS_OCCUPIED:
                if entry['key'] == key:
                    estado = "OCCUPIED (misma clave)"
                    accion = "Actualizar valor"
                    found = True
                else:
                    estado = f"OCCUPIED ({entry['key']})"
                    accion = "Colisión → siguiente"
            elif entry['status'] == STATUS_EMPTY:
                estado = "EMPTY"
                accion = "✓ Insertar aquí" if not found else ""
                if not found:
                    found = True
            else:  # DELETED
                estado = "DELETED"
                accion = "Puede reusar" if i == 0 or not found else ""
            
            calculo = f"({base_index} + {i} × {step}) % {self.size}"
            print(f"{i:<12} | {calculo:<25} | {pos:<12} | {estado:<15} | {accion}")
            
            if found and entry['status'] == STATUS_EMPTY:
                break
        
        # Mostrar resumen
        print(f"\n{'─' * 70}")
        print("RESUMEN")
        print(f"{'─' * 70}")
        print(f"Posición base (h1): {base_index}")
        print(f"Salto (h2): {step}")
        print(f"Secuencia completa: ", end="")
        secuencia = [(base_index + i * step) % self.size for i in range(min(5, self.size))]
        print(" → ".join(map(str, secuencia)), end="")
        if self.size > 5:
            print(" → ...")
        else:
            print()
        
        # Mostrar visualización de la tabla con la secuencia marcada
        print(f"\n{'─' * 70}")
        print("VISUALIZACIÓN EN LA TABLA")
        print(f"{'─' * 70}")
        print(f"{'Índice':<8} | {'Estado':<12} | {'Clave':<15} | {'En secuencia?'}")
        print("-" * 70)
        
        secuencia_completa = [(base_index + i * step) % self.size for i in range(self.size)]
        for i in range(self.size):
            entry = self.table[i]
            estado = entry['status']
            clave = str(entry['key']) if entry['key'] is not None else 'None'
            
            if i in secuencia_completa:
                pos_en_secuencia = secuencia_completa.index(i)
                en_secuencia = f"✓ (intento {pos_en_secuencia})"
            else:
                en_secuencia = ""
            
            # Resaltar la posición base
            if i == base_index:
                en_secuencia = f"★ BASE {en_secuencia}".strip()
            
            print(f"{i:<8} | {estado:<12} | {clave:<15} | {en_secuencia}")
        
        print("=" * 70)

    def demonstrate_collisions(self, keys: list) -> None:
        """
        Demuestra cómo se resuelven múltiples colisiones usando doble hashing.
        
        Args:
            keys: Lista de claves para insertar y mostrar el proceso de colisiones.
        """
        print("\n" + "=" * 70)
        print("DEMOSTRACIÓN DE DOBLE HASHING CON COLISIONES")
        print("=" * 70)
        
        print(f"\nInsertando {len(keys)} claves en tabla de tamaño {self.size}")
        print("Mostrando el proceso de resolución de colisiones paso a paso...")
        
        for idx, key in enumerate(keys, 1):
            print(f"\n{'=' * 70}")
            print(f"INSERCIÓN {idx}: Clave = {key}")
            print(f"{'=' * 70}")
            
            # Mostrar el proceso antes de insertar
            self.show_double_hashing_process(key, f"valor_{key}")
            
            # Insertar
            resultado = self.insert(key, f"valor_{key}")
            if resultado:
                print(f"\n✓ Clave {key} insertada exitosamente")
            else:
                print(f"\n✗ No se pudo insertar {key} (tabla llena)")
            
            # Mostrar estado actual de la tabla
            print(f"\nEstado actual de la tabla después de insertar {key}:")
            self.display()
            
            if idx < len(keys):
                input("\nPresiona Enter para continuar con la siguiente inserción...")
        
        print(f"\n{'=' * 70}")
        print("DEMOSTRACIÓN COMPLETADA")
        print(f"{'=' * 70}")

    def analyze_collisions(self) -> dict:
        """
        Analiza la tabla hash y detecta colisiones.
        
        Returns:
            Diccionario con información sobre colisiones:
                - collisions: Lista de colisiones detectadas
                - total_collisions: Número total de colisiones
                - collision_groups: Grupos de claves que colisionaron
        """
        collisions = []
        collision_groups = {}
        
        # Analizar cada elemento ocupado
        for pos, entry in enumerate(self.table):
            if entry['status'] == STATUS_OCCUPIED:
                key = entry['key']
                numeric_key = self.normalize_numeric_key(key)
                base_index = self.h1(key)
                
                # Si la posición actual no es la posición base, hubo colisión
                if pos != base_index:
                    collisions.append({
                        'key': key,
                        'base_position': base_index,
                        'actual_position': pos,
                        'offset': (pos - base_index) % self.size
                    })
                    
                    # Agrupar por posición base
                    if base_index not in collision_groups:
                        collision_groups[base_index] = []
                    collision_groups[base_index].append({
                        'key': key,
                        'position': pos
                    })
        
        return {
            'collisions': collisions,
            'total_collisions': len(collisions),
            'collision_groups': collision_groups
        }

    def show_collisions(self) -> None:
        """
        Muestra información detallada sobre las colisiones en la tabla hash.
        
        Analiza la tabla y muestra qué claves tuvieron colisiones,
        en qué posición base deberían estar y dónde están realmente.
        """
        analysis = self.analyze_collisions()
        
        print("\n" + "=" * 70)
        print("ANÁLISIS DE COLISIONES EN LA TABLA HASH")
        print("=" * 70)
        
        if analysis['total_collisions'] == 0:
            print("\n✓ No se detectaron colisiones.")
            print("Todas las claves están en su posición base calculada por h1.")
        else:
            print(f"\n📊 RESUMEN")
            print(f"{'─' * 70}")
            print(f"Total de colisiones detectadas: {analysis['total_collisions']}")
            print(f"Claves con colisiones: {len(analysis['collisions'])}")
            
            # Mostrar colisiones por grupo
            if analysis['collision_groups']:
                print(f"\n📋 COLISIONES POR POSICIÓN BASE")
                print(f"{'─' * 70}")
                
                for base_pos, keys in sorted(analysis['collision_groups'].items()):
                    print(f"\nPosición base {base_pos} (h1 = {base_pos}):")
                    
                    # Encontrar la clave que está en la posición base
                    base_key = None
                    for pos, entry in enumerate(self.table):
                        if pos == base_pos and entry['status'] == STATUS_OCCUPIED:
                            base_key = entry['key']
                            break
                    
                    if base_key:
                        print(f"  ✓ Clave en posición base: {base_key}")
                    
                    # Mostrar claves que colisionaron
                    for item in keys:
                        key = item['key']
                        actual_pos = item['position']
                        step = self.h2(key)
                        offset = (actual_pos - base_pos) % self.size
                        
                        print(f"  → Colisión: {key}")
                        print(f"    - Debería estar en: {base_pos} (h1({key}) = {base_pos})")
                        print(f"    - Está en: {actual_pos}")
                        print(f"    - Salto usado (h2): {step}")
                        print(f"    - Offset: {offset}")
                        
                        # Mostrar la secuencia de probes
                        secuencia = []
                        for i in range(min(5, self.size)):
                            probe_pos = (base_pos + i * step) % self.size
                            secuencia.append(f"{probe_pos}")
                        print(f"    - Secuencia de probes: {' → '.join(secuencia)}...")
            
            # Mostrar tabla detallada
            print(f"\n{'─' * 70}")
            print("TABLA DETALLADA CON COLISIONES")
            print(f"{'─' * 70}")
            print(f"{'Índice':<8} | {'Clave':<15} | {'h1 (base)':<12} | {'h2 (step)':<12} | {'¿Colisión?':<12}")
            print("-" * 70)
            
            for pos, entry in enumerate(self.table):
                if entry['status'] == STATUS_OCCUPIED:
                    key = entry['key']
                    base_pos = self.h1(key)
                    step = self.h2(key)
                    tiene_colision = "✓ SÍ" if pos != base_pos else "✗ NO"
                    
                    print(f"{pos:<8} | {str(key):<15} | {base_pos:<12} | {step:<12} | {tiene_colision:<12}")
                elif entry['status'] == STATUS_DELETED:
                    print(f"{pos:<8} | {'[DELETED]':<15} | {'-':<12} | {'-':<12} | {'-':<12}")
                else:
                    print(f"{pos:<8} | {'[EMPTY]':<15} | {'-':<12} | {'-':<12} | {'-':<12}")
        
        print("=" * 70)
