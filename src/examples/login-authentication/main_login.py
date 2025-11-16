from src.hashing.hash_table_double_hashing import HashTable

class User:
    """
    Clase sencilla para representar un usuario del sistema.
    Contiene un nombre de usuario y una contraseña.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"User(username={self.username}, password={self.password})"


def main():
    """
    Función principal del programa.
    Permite registrar usuarios y autenticar usando una tabla hash
    implementada con doble hashing y manejo de cursores.
    """

    print("Registro de login y autenticación de usuarios usando Hash Table con Doble Hashing y Cursores")

    # Tamaño de la tabla hash
    hash_table_size = 11

    # Crear instancia de la tabla hash
    hash_table = HashTable(hash_table_size)

    # Menú principal del sistema
    while True:
        print("\nSeleccione una opción:")
        print("1. Registrar un nuevo usuario")
        print("2. Autenticar un usuario existente")
        print("3. Mostrar tabla hash")
        print("4. Mostrar estadísticas")
        print("5. Salir")

        option = input("Opción: ")

        # --------------------------------------------------------------
        # OPCIÓN 1: Registrar un nuevo usuario
        # --------------------------------------------------------------
        if option == '1':
            username = input("Ingrese el nombre de usuario: ")
            password = input("Ingrese la contraseña: ")

            # Primero verificar si el usuario ya existe en la tabla
            if hash_table.search(username) is not None:
                print("El usuario ya existe. Intente con otro nombre de usuario.")
            else:
                # Registrar nuevo usuario
                user = User(username, password)
                inserted = hash_table.insert(username, user)

                if inserted:
                    print("Usuario registrado exitosamente.")
                else:
                    print("Error: La tabla hash está llena.")

        # --------------------------------------------------------------
        # OPCIÓN 2: Autenticación de usuario
        # --------------------------------------------------------------
        elif option == '2':
            username = input("Ingrese el nombre de usuario: ")
            password = input("Ingrese la contraseña: ")

            # Buscar el usuario en la tabla hash
            stored_user = hash_table.search(username)

            # Si se encontró y la contraseña coincide, autenticación correcta
            if stored_user and stored_user.password == password:
                print(f"Autenticación exitosa. Bienvenido, {username}.")
            else:
                print("Autenticación fallida. Usuario o contraseña incorrectos.")

        # --------------------------------------------------------------
        # OPCIÓN 3: Mostrar contenido de la tabla hash
        # --------------------------------------------------------------
        elif option == '3':
            # Método que imprime las entradas, su estado y sus cursores
            hash_table.display()

        # --------------------------------------------------------------
        # OPCIÓN 4: Mostrar estadísticas de la tabla
        # --------------------------------------------------------------
        elif option == '4':
            stats = hash_table.get_statistics()
            print("\nEstadísticas de la tabla:")
            for key, value in stats.items():
                print(f"{key}: {value}")

        # --------------------------------------------------------------
        # OPCIÓN 5: Salir del programa
        # --------------------------------------------------------------
        elif option == '5':
            print("Saliendo del sistema...")
            break

        # --------------------------------------------------------------
        # Opción inválida
        # --------------------------------------------------------------
        else:
            print("Opción inválida. Debe seleccionar 1, 2, 3, 4 o 5.")


if __name__ == "__main__":
    main()
