# Sistema de Predicción de Riesgo de Inundaciones

Sistema modernizado de predicción de riesgo de inundaciones que utiliza Machine Learning para determinar alertas basadas en coordenadas geográficas y niveles de sensores.

## 🚀 Características

- **Modelo predictivo**: Utiliza RandomForestRegressor entrenado con datos reales
- **Entradas simplificadas**: Solo coordenadas (lat, lon) y nivel del sensor (0-3)
- **API REST**: Endpoint simple que recibe voltaje del sensor y devuelve alerta
- **Reglas de negocio**: Mapeo inteligente de voltaje a nivel y determinación de alertas
- **Separación de responsabilidades**: Entrenamiento separado de la predicción en tiempo real

## 📁 Estructura del Proyecto

```
TT2/
├── src/
│   ├── Flask_Server.py          # API REST principal
│   ├── Modelo.py                # Entrenamiento del modelo ML
│   ├── Realtime.py              # Predicción en tiempo real
│   ├── procesar_dataset.py      # Procesamiento de datos
│   ├── Dataset - Full(Dataset).csv      # Dataset original
│   ├── dataset_procesado.csv    # Dataset procesado numéricamente
│   └── modelo_predictivo.pkl    # Modelo entrenado
└── README.md
```

## 🔧 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/aleemireyhdz-star/TT2.git
   cd TT2
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Uso

### 1. Entrenar el modelo (opcional, ya está entrenado)
```bash
cd src
python Modelo.py
```

### 2. Ejecutar la API
```bash
cd src
python Flask_Server.py
```

### 3. Probar predicciones
```bash
# Endpoint: POST http://localhost:5000/ingest
# Body (JSON): {"v": 2.5, "pct": 80.0}
curl -X POST http://localhost:5000/ingest \
     -H "Content-Type: application/json" \
     -d '{"v": 2.5, "pct": 80.0}'
```

## 📊 Funcionamiento

### Flujo de predicción:
1. **Entrada**: Voltaje del sensor (0.0 - 5.0V)
2. **Mapeo**: Voltaje → Nivel del sensor (0-3)
3. **Predicción**: Coordenadas hardcoded → Score de riesgo de zona
4. **Reglas de negocio**: (Score de zona + Nivel sensor) → Alerta final

### Mapeo de niveles:
- **0.0-1.25V** → Nivel 0 (Sin riesgo)
- **1.25-2.5V** → Nivel 1 (Riesgo bajo)
- **2.5-3.75V** → Nivel 2 (Riesgo medio)
- **3.75-5.0V** → Nivel 3 (Riesgo alto)

### Alertas resultantes:
- 🟢 **Verde**: Sin riesgo / Riesgo muy bajo
- 🟡 **Amarillo**: Riesgo medio / Precaución
- 🔴 **Rojo**: Riesgo alto / Evacuación recomendada

## 🔄 Desarrollo

### Comandos Git:
```bash
git add .                                              # Agregar cambios
git commit -m "Descripción de los cambios"             # Crear commit
git push origin master                                 # Subir a GitHub
```

## 🎯 Próximas mejoras

- [ ] Coordenadas dinámicas en la API
- [ ] Conexión con sensores IoT en tiempo real
- [ ] Dashboard web para visualización
- [ ] Historial de predicciones
- [ ] Notificaciones automáticas

## 👥 Contribución

Para contribuir al proyecto:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un Pull Request

---
**Repositorio**: https://github.com/aleemireyhdz-star/TT2
