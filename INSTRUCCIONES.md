# 📁 Estructura del Proyecto

## Archivos Python

El proyecto consta de **2 archivos Python** que trabajan en conjunto:

```
ED-II/
├── src/
│   ├── hash_table.py    # Implementación de la tabla hash
│   └── ejemplo.py       # Ejemplo de uso de la tabla hash
├── README.md            # Documentación principal
└── INSTRUCCIONES.md     # Este archivo
```

## 📄 Descripción de Archivos

### 1. `hash_table.py`
Contiene la clase `HashTable` con:
- Implementación de doble hashing
- Funciones de inserción, búsqueda y eliminación
- Visualización de la tabla
- Estadísticas de uso

### 2. `ejemplo.py`
Programa de demostración que:
- Importa y usa la clase `HashTable`
- Muestra ejemplos de inserción, búsqueda y eliminación
- Visualiza el estado de la tabla

## 🚀 Cómo Ejecutar

### Ejecutar el ejemplo:
```bash
cd src
python3 ejemplo.py
```

### Usar la tabla hash en tu código:
```python
from hash_table import HashTable

# Crear una tabla hash
ht = HashTable(size=11)

# Insertar elementos
ht.insert(10, "A")
ht.insert(22, "B")

# Buscar elementos
valor = ht.search(10)  # Retorna "A"

# Eliminar elementos
ht.delete(22)

# Ver la tabla
ht.display()

# Ver estadísticas
stats = ht.get_statistics()
print(stats)
```

## ✅ Verificación

Los archivos están diseñados para trabajar juntos:
- `ejemplo.py` importa `HashTable` desde `hash_table.py`
- Ambos archivos están en la misma carpeta `src/`
- No se requieren dependencias externas

