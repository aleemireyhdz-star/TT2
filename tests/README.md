# Tests del Sistema de Alertas de Inundación

Esta carpeta contiene los archivos de prueba para validar el funcionamiento del sistema de predicción de alertas de inundación.

## Archivos de prueba:

### `test_coordenadas_especificas.py`
- **Propósito**: Prueba coordenadas específicas solicitadas por el usuario
- **Coordenadas**: (19.4949629462, -99.1486655987)
- **Funcionalidad**: 
  - Valida si las coordenadas están dentro de CDMX
  - Prueba los 4 niveles de sensor (0-3)
  - Analiza patrones de alertas
  - Compara con datos del dataset si están disponibles

### `test_correccion.py` (si existe)
- **Propósito**: Verifica que se corrigieron los problemas originales
- **Casos de prueba**:
  - Coordenadas con bajo % de área inundable
  - Coordenadas hardcoded del sistema
  - Coordenadas fuera de CDMX
  - Pruebas con diferentes niveles de sensor

### `prueba_final.py` (si existe)
- **Propósito**: Prueba final integral del sistema corregido
- **Validaciones**: 
  - Corrección de thresholds
  - Validación geográfica
  - Alertas apropiadas

## Cómo ejecutar los tests:

```bash
# Desde la carpeta del proyecto
cd /Users/armyb/Documents/TT2

# Ejecutar test de coordenadas específicas
python tests/test_coordenadas_especificas.py

# O ejecutar desde la carpeta tests
cd tests
python test_coordenadas_especificas.py
```

## Estructura del sistema:

```
TT2/
├── src/
│   ├── Modelo.py                 # Entrenamiento del modelo
│   ├── Realtime.py              # Sistema de predicción en tiempo real
│   ├── Flask_Server.py          # Servidor web
│   ├── procesar_dataset.py      # Procesamiento de datos
│   ├── modelo_predictivo.pkl    # Modelo entrenado
│   └── dataset_procesado.csv    # Dataset procesado
├── tests/
│   ├── README.md               # Este archivo
│   └── test_*.py              # Archivos de prueba
└── requirements.txt           # Dependencias
```

## Correcciones implementadas:

✅ **Thresholds corregidos**: BAJO ≤45, MEDIO ≤65, ALTO >65  
✅ **Validación geográfica**: Advertencias para coordenadas fuera de CDMX  
✅ **Alertas apropiadas**: Zonas con bajo % área ya no dan rojas incorrectas  
✅ **20 zonas BAJO riesgo**: Ahora el dataset tiene zonas de bajo riesgo  
