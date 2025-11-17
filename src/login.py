"""
Sistema de registro y autenticación de usuarios usando tabla hash.

Este programa utiliza la tabla hash con doble hashing para gestionar
el registro y autenticación de usuarios de forma eficiente.
"""

import sys
import os

# Ajustar el path para que funcione desde cualquier ubicación
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.hashing.hash_table_double_hashing import HashTable


class User:
    """
    Clase sencilla para representar un usuario del sistema.
    
    Contiene un nombre de usuario y una contraseña.
    """
    
    def __init__(self, username: str, password: str):
        """
        Inicializa un usuario.
        
        Args:
            username: Nombre de usuario.
            password: Contraseña del usuario.
        """
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        """
        Representación en string del usuario.
        
        Returns:
            String con la información del usuario.
        """
        return f"User(username={self.username}, password=***)"


def _get_user_input(prompt: str, allow_empty: bool = False) -> str:
    """
    Obtiene entrada del usuario con validación.
    
    Args:
        prompt: Mensaje a mostrar al usuario.
        allow_empty: Si True, permite entrada vacía.
    
    Returns:
        String ingresado por el usuario (puede estar vacío si allow_empty=True).
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value and not allow_empty:
                print("Error: Este campo no puede estar vacío.")
                continue
            return value
        except (EOFError, KeyboardInterrupt):
            print("\n\nOperación cancelada.")
            return ""


def _register_user(hash_table: HashTable) -> None:
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        hash_table: Instancia de HashTable para almacenar usuarios.
    """
    username = _get_user_input("Ingrese el nombre de usuario: ")
    if not username:
        return
    
    # Verificar si el usuario ya existe
    if hash_table.search(username) is not None:
        print("El usuario ya existe. Intente con otro nombre de usuario.")
        return
    
    password = _get_user_input("Ingrese la contraseña: ")
    if not password:
        return
    
    # Registrar nuevo usuario
    user = User(username, password)
    inserted = hash_table.insert(username, user)
    
    if inserted:
        print("✓ Usuario registrado exitosamente.")
    else:
        print("✗ Error: La tabla hash está llena.")


def _authenticate_user(hash_table: HashTable) -> None:
    """
    Autentica un usuario existente.
    
    Args:
        hash_table: Instancia de HashTable para buscar usuarios.
    """
    username = _get_user_input("Ingrese el nombre de usuario: ")
    if not username:
        return
    
    password = _get_user_input("Ingrese la contraseña: ")
    if not password:
        return
    
    # Buscar el usuario en la tabla hash
    stored_user = hash_table.search(username)
    
    # Si se encontró y la contraseña coincide, autenticación correcta
    if stored_user and isinstance(stored_user, User) and stored_user.password == password:
        print(f"✓ Autenticación exitosa. Bienvenido, {username}.")
    else:
        print("✗ Autenticación fallida. Usuario o contraseña incorrectos.")


def _show_statistics(hash_table: HashTable) -> None:
    """
    Muestra las estadísticas de la tabla hash.
    
    Args:
        hash_table: Instancia de HashTable.
    """
    stats = hash_table.get_statistics()
    print("\n" + "=" * 70)
    print("ESTADÍSTICAS DE LA TABLA")
    print("=" * 70)
    print(f"  Total de slots: {stats['total_slots']}")
    print(f"  Ocupados: {stats['occupied']}")
    print(f"  Vacíos: {stats['empty']}")
    print(f"  Eliminados: {stats['deleted']}")
    print(f"  Factor de carga: {stats['load_factor']:.2%}")
    print("=" * 70)


def main() -> None:
    """
    Función principal del programa.
    
    Permite registrar usuarios y autenticar usando una tabla hash
    implementada con doble hashing y manejo de cursores.
    """
    print("=" * 70)
    print("Sistema de Registro y Autenticación de Usuarios")
    print("Usando Hash Table con Doble Hashing y Cursores")
    print("=" * 70)

    # Tamaño de la tabla hash
    hash_table_size = 11

    try:
        # Crear instancia de la tabla hash
        hash_table = HashTable(hash_table_size)
    except ValueError as e:
        print(f"Error al inicializar la tabla hash: {e}")
        return

    # Menú principal del sistema
    while True:
        try:
            print("\n" + "-" * 70)
            print("Seleccione una opción:")
            print("1. Registrar un nuevo usuario")
            print("2. Autenticar un usuario existente")
            print("3. Mostrar tabla hash")
            print("4. Mostrar estadísticas")
            print("5. Mostrar análisis de colisiones")
            print("6. Salir")
            print("-" * 70)

            option = input("Opción: ").strip()

            # OPCIÓN 1: Registrar un nuevo usuario
            if option == '1':
                _register_user(hash_table)

            # OPCIÓN 2: Autenticación de usuario
            elif option == '2':
                _authenticate_user(hash_table)

            # OPCIÓN 3: Mostrar contenido de la tabla hash
            elif option == '3':
                hash_table.display()

            # OPCIÓN 4: Mostrar estadísticas de la tabla
            elif option == '4':
                _show_statistics(hash_table)

            # OPCIÓN 5: Mostrar análisis de colisiones
            elif option == '5':
                hash_table.show_collisions()

            # OPCIÓN 6: Salir del programa
            elif option == '6':
                print("\nSaliendo del sistema...")
                print("¡Hasta luego!")
                break

            # Opción inválida
            else:
                print("✗ Opción inválida. Debe seleccionar 1, 2, 3, 4, 5 o 6.")

        except (EOFError, KeyboardInterrupt):
            print("\n\nOperación cancelada. Saliendo...")
            break
        except Exception as e:
            print(f"\n✗ Error inesperado: {e}")
            print("Por favor, intente nuevamente.")


if __name__ == "__main__":
    main()
