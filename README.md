# Calculadora de Distancias entre Contenedores

Aplicación Python para calcular la matriz de distancias en carretera entre 48 contenedores ubicados en Jaén.

## Características

- ✅ Lee datos de latitud/longitud desde archivo Excel
- ✅ Calcula distancias en carretera usando OSRM (Open Street Map Routing)
- ✅ Genera matriz completa de distancias entre todos los pares de contenedores
- ✅ Interfaz gráfica amigable (GUI)
- ✅ Exporta resultados en múltiples formatos:
  - Excel (.xlsx)
  - JSON
  - CSV
- ✅ Opción de cálculo rápido con distancia en línea recta (Haversine)

## Requisitos

- Python 3.7+
- Archivo `destinos.xlsx` con datos de contenedores (ID, Latitud, Longitud)

## Instalación

### 1. Asegurar que Python está configurado

En la terminal, verifica que Python está disponible:
```powershell
python --version
```

### 2. Instalar dependencias (si no están instaladas)

```powershell
pip install pandas openpyxl requests
```

## Uso

### Opción A: Interfaz Gráfica (Recomendado)

Ejecuta la aplicación con GUI:

```powershell
python main.py
```

**Pasos en la GUI:**

1. **Cargar datos**: Haz clic en "1. Cargar datos (Excel)"
   - Automáticamente busca `destinos.xlsx` en la carpeta actual
   - Muestra información de los contenedores cargados

2. **Calcular Distancias**: Haz clic en "2. Calcular Distancias"
   - Puedes elegir el método:
     - ✓ OSRM: Distancia real en carretera (más preciso, ~5-15 min)
     - ☐ Haversine: Distancia en línea recta (rápido, <1 min)
   - La aplicación mostrará el progreso
   - Se genera la matriz de distancias en una tabla

3. **Exportar Datos**: Haz clic en "3. Exportar Datos"
   - Selecciona el formato deseado
   - Elige ubicación para guardar el archivo

4. **Visualizar Datos**:
   - La tabla muestra la distancia entre cada par de contenedores
   - Cada fila es un contenedor de origen
   - Cada columna es un contenedor de destino
   - Los valores están en km

### Opción B: Línea de Comandos

Ejecuta el script CLI para automatizar todo:

```powershell
python script_cli.py
```

El script:
- Carga datos automáticamente del Excel
- Te pregunta qué método usar (OSRM o Haversine)
- Calcula la matriz completa
- Exporta a Excel, JSON y CSV automáticamente

## Formato de entrada (destinos.xlsx)

El archivo Excel debe tener la siguiente estructura:

| Contenedor | Latitud | Longitud |
|-----------|---------|----------|
| 1 | 37.7821714163432 | -3.8197137415925 |
| 2 | 37.7812619855146 | -3.81721258173619 |
| ... | ... | ... |

## Archivos generados

Después de exportar, tendrás:

### distancias_matriz.xlsx
- Matriz de distancias en formato Excel
- Fácil de usar en cálculos posteriores
- Compatible con cualquier hoja de cálculo

### distancias_matriz.json
```json
{
  "fecha_generacion": "2024-03-25T10:30:45.123456",
  "num_contenedores": 48,
  "matriz": {
    "1": {
      "1": 0.0,
      "2": 1.23,
      "3": 5.67
    },
    ...
  }
}
```

### distancias_matriz.csv
- Formato CSV estándar
- Importable en cualquier herramienta de análisis

## Métodos de cálculo

### OSRM (Open Source Routing Machine)
- **Ventaja**: Calcula distancias reales en carretera y carreteras
- **Desventaja**: Más lento (~0.1-0.2 seg por par)
- **Tiempo estimado**: 5-15 minutos para 48 contenedores
- **API**: router.project-osrm.org (gratuita, sin límite de peticiones)

### Haversine
- **Ventaja**: Muy rápido
- **Desventaja**: Solo calcula distancia en línea recta, no sigue carreteras
- **Tiempo estimado**: <1 minuto para 48 contenedores
- **Uso**: Buena aproximación para análisis rápidos

## Estructura de archivos

```
TFG_org/
├── main.py                    # Aplicación GUI
├── script_cli.py              # Script de línea de comandos
├── data_handler.py            # Módulo de E/S de datos
├── distance_calculator.py     # Módulo de cálculo de distancias
├── destinos.xlsx              # Datos de entrada
├── distancias_matriz.xlsx     # Salida (generado)
├── distancias_matriz.json     # Salida (generado)
├── distancias_matriz.csv      # Salida (generado)
└── README.md                  # Este archivo
```

## Solución de problemas

### Error: "archivo 'destinos.xlsx' no encontrado"
- Verifica que `destinos.xlsx` está en la misma carpeta que `main.py`
- Comprueba el nombre exacto del archivo (mayúsculas/minúsculas)

### La aplicación es lenta con OSRM
- Es normal, calcula distancias reales en carretera
- Para una vista previa rápida, usa Haversine
- Deja que termine, el proceso es automático

### Error de conexión con OSRM
- Comprueba tu conexión a Internet
- OSRM requiere acceso a internet
- Si no hay conexión, la aplicación usa Haversine automáticamente

### El Excel no se importa correctamente
- Verifica que las columnas están en orden: ID, Latitud, Longitud
- Asegúrate de que los valores de latitud y longitud son números
- Elimina filas vacías al final del archivo

## Información técnica

- **Lenguaje**: Python 3
- **GUI**: tkinter (incluido en Python)
- **Librerías**: pandas, openpyxl, requests
- **API de enrutamiento**: OSRM (Open Source Routing Machine)
- **Fórmula distancia**: Haversine para distancia en línea recta

## Licencia

Código de propósito educativo para TFG.

## Autor

Desarrollado para el Trabajo de Fin de Grado.

## Notas finales

- La aplicación no almacena datos personales
- Las coordenadas se envían a OSRM para calcular distancias (datos públicos)
- Todos los datos se procesan localmente después
- Los archivos generados se guardan en tu disco duro
