# 🌊 Sistema de Predicción de Riesgo de Inundaciones CDMX

Sistema inteligente de monitoreo y predicción de riesgos de inundación para la Ciudad de México que utiliza Machine Learning para generar alertas en tiempo real basadas en datos geográficos y sensores de humedad.

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Componentes Principales](#-componentes-principales)
- [Instalación](#-instalación)
- [Uso del Sistema](#-uso-del-sistema)
- [API Endpoints](#-api-endpoints)
- [Modelo de Machine Learning](#-modelo-de-machine-learning)
- [Sistema de Alertas](#-sistema-de-alertas)
- [Despliegue](#-despliegue)
- [Estructura del Proyecto](#-estructura-del-proyecto)

## 🚀 Características Principales

- *Predicción en Tiempo Real*: Análisis instantáneo basado en coordenadas geográficas y datos de sensores
- *Machine Learning*: Modelo RandomForestRegressor entrenado con datos históricos de CDMX
- *Interfaz Web Moderna*: Dashboard interactivo con mapa de Leaflet y actualizaciones en tiempo real
- *Sistema de Alertas*: Semáforo de 3 niveles (Verde, Amarillo, Rojo) con lógica de negocio avanzada
- *API REST*: Endpoints simples para integración con sensores IoT
- *Validación Geográfica*: Verificación automática de coordenadas dentro del área metropolitana
- *Configuración Persistente*: Almacenamiento de coordenadas y configuraciones
- *Despliegue en la Nube*: Soporte para Cloudflare Tunnels y servidores de producción

## 🏗 Arquitectura del Sistema


┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Sensor IoT    │───▶│   Flask Server   │───▶│   Dashboard     │
│   (Arduino)     │    │   (API REST)     │    │   (Web UI)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   Realtime.py    │
                        │  (Predicción)    │
                        └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │ Modelo ML (.pkl) │
                        │ (RandomForest)   │
                        └──────────────────┘


## 🧩 Componentes Principales

### 1. *Flask_Server.py* - Servidor Web Principal

El corazón del sistema que maneja:
- *API REST* para recepción de datos de sensores
- *Servidor web* para el dashboard
- *Gestión de coordenadas* persistentes
- *Endpoints de estado* y configuración

*Características clave:*
- Mapeo de voltaje a nivel de sensor (0-3)
- Almacenamiento persistente de coordenadas en JSON
- Validación geográfica automática
- Logging detallado para depuración

python
# Mapeo de voltaje del sensor a niveles
if v <= 0.695:    nivel_sensor = 0  # Seco
elif v <= 0.759:  nivel_sensor = 1  # Bajo
elif v <= 0.812:  nivel_sensor = 2  # Medio
else:             nivel_sensor = 3  # Alto


### 2. *Realtime.py* - Motor de Predicción

Módulo especializado en:
- *Carga del modelo* ML entrenado
- *Validación geográfica* de coordenadas CDMX
- *Búsqueda en dataset* para coordenadas exactas
- *Predicción ML* para ubicaciones nuevas
- *Lógica de alertas* combinando riesgo de zona + sensor

*Funciones principales:*
- validar_coordenadas_cdmx(): Verifica ubicación dentro de CDMX
- obtener_riesgo_zona(): Calcula score de riesgo geográfico
- predecir_alerta(): Genera alerta final combinando factores
- clasificar_riesgo_zona(): Categoriza score en BAJO/MEDIO/ALTO

### 3. *Modelo.py* - Entrenamiento del Modelo ML

Script para crear y entrenar el modelo:
- *Carga de datos* procesados
- *División* entrenamiento/prueba
- *Entrenamiento* RandomForestRegressor
- *Evaluación* con métricas (MSE, R²)
- *Persistencia* del modelo entrenado

*Configuración del modelo:*
python
RandomForestRegressor(
    n_estimators=100,    # 100 árboles
    random_state=42,     # Reproducibilidad
    max_depth=10         # Prevenir overfitting
)


### 4. *procesar_dataset.py* - Procesamiento de Datos

Transforma datos categóricos a numéricos:
- *Mapeo de rangos* de intensidad de lluvia
- *Conversión* de porcentajes de área inundable
- *Cálculo de score* combinado (60% intensidad + 40% área)
- *Eliminación* de duplicados
- *Generación* del dataset procesado

## 🔧 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación Rápida

1. *Clonar el repositorio:*
bash
git clone <repository-url>
cd TT2


2. *Instalar dependencias:*
bash
pip install -r requirements.txt


3. *Procesar el dataset:*
bash
cd src
python procesar_dataset.py


4. *Entrenar el modelo:*
bash
python Modelo.py


5. *Iniciar el servidor:*
bash
python Flask_Server.py


### Dependencias


scikit-learn==1.3.2  # Machine Learning
pandas==2.1.4        # Manipulación de datos
numpy==1.24.4        # Cálculos numéricos
matplotlib==3.8.2    # Visualización
flask==3.0.0         # Servidor web
joblib==1.3.2        # Serialización del modelo


## 📊 Uso del Sistema

### 1. Inicialización

bash
cd src
python Flask_Server.py


El servidor iniciará en http://localhost:5000

### 2. Configuración de Coordenadas

*Via Web UI:*
- Acceder al dashboard
- Usar el formulario de coordenadas
- Las coordenadas se guardan automáticamente

*Via API:*
bash
curl -X POST http://localhost:5000/api/coords \
  -H "Content-Type: application/json" \
  -d '{"lat": 19.4326, "lon": -99.1332}'


### 3. Envío de Datos del Sensor

bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{"v": 0.8, "pct": 75.5}'


### 4. Consulta de Estado

bash
curl http://localhost:5000/api/status


## 🌐 API Endpoints

### POST /ingest
*Descripción:* Recibe datos del sensor IoT
*Body:*
json
{
  "v": 0.8,     // Voltaje del sensor (0-3V)
  "pct": 75.5   // Porcentaje de humedad
}


### GET /api/status
*Descripción:* Obtiene el último estado de alerta
*Response:*
json
{
  "alerta": "AMARILLO",
  "riesgo_zona": "MEDIO",
  "riesgo_score": 58.7,
  "nivel_sensor": 2,
  "coordenadas": {"latitud": 19.4326, "longitud": -99.1332}
}


### POST /api/coords
*Descripción:* Actualiza coordenadas del sistema
*Body:*
json
{
  "lat": 19.4326,
  "lon": -99.1332
}


### GET /api/coords
*Descripción:* Obtiene coordenadas actuales
*Response:*
json
{
  "latitud": 19.4326,
  "longitud": -99.1332
}


## 🤖 Modelo de Machine Learning

### Características del Modelo

- *Algoritmo:* Random Forest Regressor
- *Entradas:* Latitud y Longitud
- *Salida:* Score de riesgo (28.5 - 80.2)
- *Precisión:* R² Score ≈ 0.85+

### Proceso de Entrenamiento

1. *Preprocesamiento:*
   - Conversión de rangos categóricos a valores numéricos
   - Cálculo de score combinado: intensidad_mm * 0.6 + area_inundable_pct * 0.4

2. *División de datos:*
   - 80% entrenamiento
   - 20% prueba

3. *Métricas de evaluación:*
   - Error cuadrático medio (MSE)
   - Coeficiente de determinación (R²)
   - Error promedio en puntos de riesgo

### Mapeo de Datos Originales

*Intensidad de Precipitación:*
python
{
    '41 a 54': 47.5,    # BAJO
    '54 a 60': 57.0,    # MEDIO-BAJO
    '60 a 64': 62.0,    # MEDIO-ALTO  
    '64 a 70': 67.0     # ALTO
}


*Porcentaje de Área Inundable:*
python
{
    '0 a 25': 12.5,     # MUY BAJO
    '26 a 49': 37.5,    # BAJO
    '50 a 72': 61.0,    # MEDIO
    '73 a 99': 86.0,    # ALTO
    '100': 100.0        # MUY ALTO
}


## 🚨 Sistema de Alertas

### Clasificación de Riesgo de Zona

- *BAJO:* Score ≤ 45
- *MEDIO:* Score 46-65  
- *ALTO:* Score > 65

### Lógica de Alertas

La alerta final combina el riesgo geográfico con el nivel del sensor:

| Riesgo Zona | Sensor 0 | Sensor 1 | Sensor 2 | Sensor 3 |
|-------------|----------|----------|----------|----------|
| *BAJO*    | 🟢 VERDE | 🟢 VERDE | 🟢 VERDE | 🟡 AMARILLO |
| *MEDIO*   | 🟢 VERDE | 🟢 VERDE | 🟡 AMARILLO | 🔴 ROJO |
| *ALTO*    | 🟢 VERDE | 🟡 AMARILLO | 🔴 ROJO | 🔴 ROJO |

### Niveles de Sensor

- *0:* Seco (≤ 0.695V)
- *1:* Bajo (0.696-0.759V)
- *2:* Medio (0.760-0.812V)
- *3:* Alto (> 0.812V)

## 🌍 Despliegue

### Desarrollo Local

bash
python Flask_Server.py
# Servidor en http://localhost:5000


### Producción con Gunicorn

bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 wsgi:app


### Cloudflare Tunnels

1. *Instalar cloudflared:*
   - Seguir guía en CLOUDFLARE_SETUP.md

2. *Crear túnel:*
bash
cloudflared tunnel create mi-tunel-inundaciones


3. *Configurar y ejecutar:*
bash
cloudflared tunnel run mi-tunel-inundaciones


### Variables de Entorno

bash
export FLASK_ENV=production    # Modo producción
export PORT=5000              # Puerto personalizado


## 📁 Estructura del Proyecto


TT2/
├── src/                          # Código fuente principal
│   ├── Flask_Server.py          # 🌐 Servidor web y API REST
│   ├── Realtime.py              # 🤖 Motor de predicción ML
│   ├── Modelo.py                # 📊 Entrenamiento del modelo
│   ├── procesar_dataset.py      # 🔧 Procesamiento de datos
│   ├── coords_config.json       # 📍 Coordenadas persistentes
│   ├── Dataset - Full(Dataset).csv      # 📋 Dataset original
│   ├── dataset_procesado.csv    # 📋 Dataset limpio y numérico
│   ├── modelo_predictivo.pkl    # 🧠 Modelo entrenado
│   ├── templates/               # 🎨 Templates HTML
│   │   └── index.html          # Dashboard principal
│   └── static/                  # 📱 Recursos estáticos
│       ├── app.js              # JavaScript del frontend
│       └── styles.css          # Estilos CSS
├── tests/                       # 🧪 Pruebas y validaciones
│   ├── prueba_final.py         # Prueba integral
│   ├── test_coordenadas_especificas.py  # Pruebas geográficas
│   └── README.md               # Documentación de pruebas
├── wsgi.py                     # 🚀 Entrada para producción
├── requirements.txt            # 📦 Dependencias Python
├── CLOUDFLARE_SETUP.md        # ☁ Guía de despliegue
├── PUBLIC_SERVER_QUICKSTART.md # 🌐 Guía servidor público
└── README.md                   # 📖 Documentación principal


## 🧪 Pruebas

### Pruebas Unitarias

bash
cd tests
python test_coordenadas_especificas.py
python prueba_final.py


### Pruebas de Integración

bash
# Probar API
curl -X POST http://localhost:5000/ingest -d '{"v":0.8,"pct":75}'

# Verificar predicción
curl http://localhost:5000/api/status


### Pruebas de Coordenadas

bash
cd src
python Realtime.py test


## 🤝 Contribución

1. Fork el repositorio
2. Crear rama de feature (git checkout -b feature/nueva-caracteristica)
3. Commit cambios (git commit -am 'Agregar nueva característica')
4. Push a la rama (git push origin feature/nueva-caracteristica)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## 🆘 Soporte y Contacto

- *Issues:* Usar el sistema de issues de GitHub
- *Documentación:* Ver archivos .md en el repositorio
- *Pruebas:* Ejecutar scripts en la carpeta tests/

## 🔄 Versionado

- *v1.0.0:* Versión inicial con modelo ML básico
- *v1.1.0:* Interfaz web y API REST
- *v1.2.0:* Sistema de coordenadas persistentes
- *v1.3.0:* Despliegue en la nube y optimizaciones

---

Sistema desarrollado para la prevención de riesgos de inundación en la Ciudad de México utilizando tecnologías modernas de Machine Learning e IoT.