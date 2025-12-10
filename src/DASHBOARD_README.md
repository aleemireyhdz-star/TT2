# 🌊 Dashboard Web - Sistema de Alerta de Inundaciones

## 📋 Descripción

Se ha creado una interfaz web moderna para visualizar en tiempo real:
- 📍 **Ubicación actual** con mapa interactivo
- 🚨 **Semáforo de alerta** (VERDE/AMARILLO/ROJO)
- 📡 **Información del sensor** (nivel, riesgo, score)
- 📊 **Historial de eventos** actualizado en tiempo real

## 🚀 Cómo usar

### 1. Iniciar el servidor Flask

```powershell
cd src
python Flask_Server.py
```

El servidor estará disponible en: **http://localhost:5000**

### 2. Abrir en el navegador

Accede a `http://localhost:5000` desde tu navegador web.

### 3. Enviar datos del sensor

El sistema espera datos JSON en el endpoint `/ingest`:

```powershell
# Ejemplo con PowerShell
$data = @{
    v = 0.5
    pct = 25.5
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/ingest" `
    -Method POST `
    -Headers @{"Content-Type" = "application/json"} `
    -Body $data
```

O con curl:
```bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{"v": 0.5, "pct": 25.5}'
```

## 📁 Estructura de archivos

```
src/
├── Flask_Server.py           # Servidor principal
├── Realtime.py               # Lógica de predicción
├── templates/
│   └── index.html           # Página web principal
└── static/
    ├── styles.css           # Estilos CSS
    └── app.js               # Lógica JavaScript del cliente
```

## 🎨 Características de la interfaz

### Mapa Interactivo
- Usa Leaflet.js (OpenStreetMap)
- Marcador dinámico que se actualiza con las coordenadas
- Zoom y desplazamiento libres

### Semáforo de Alerta
- **🟢 VERDE**: Condiciones normales
- **🟡 AMARILLO**: Precaución - Monitoreo continuo
- **🔴 ROJO**: Peligro - Medidas inmediatas

### Información en Tiempo Real
- Nivel del sensor (0-3)
- Riesgo de zona (BAJO/MEDIO/ALTO)
- Score de riesgo (numérico)
- Coordenadas actuales
- Hora de última actualización

### Historial de Eventos
- Registro automático de cambios de alerta
- Últimos 50 eventos
- Timestamp de cada evento
- Evita duplicados consecutivos

## 🔌 Endpoints de la API

### GET `/`
Sirve la página web principal.

### POST `/ingest`
Recibe datos del sensor.

**Parámetros:**
- `v` (float): Voltaje del sensor
- `pct` (float): Porcentaje/humedad

### GET `/api/status`
Retorna el estado actual de la predicción.

**Respuesta:**
```json
{
    "alerta": "ROJO",
    "riesgo_zona": "ALTO",
    "riesgo_score": 72.5,
    "nivel_sensor": 3,
    "coordenadas": {
        "latitud": 19.5041017692,
        "longitud": -99.0986932319
    }
}
```

## 📱 Responsive
La interfaz se adapta automáticamente a:
- Pantallas de escritorio (1400px+)
- Tablets (1024px)
- Móviles (768px)

## 🔄 Actualización automática
La página se actualiza automáticamente cada 2 segundos, obteniéndose del endpoint `/api/status`.

## 📦 Dependencias

- Flask (para el servidor)
- Leaflet.js (para el mapa - CDN)

No requiere instalaciones adicionales de JavaScript.

## 💡 Tips

- Mantén el navegador abierto en la pestaña del dashboard para ver actualizaciones en tiempo real
- El historial se mantiene en memoria del cliente (se limpia al recargar la página)
- Puedes hacer zoom en el mapa con rueda del ratón
- Haz clic en el marcador para ver las coordenadas exactas

## 🆘 Solución de problemas

### "No se carga la página"
- Verifica que Flask esté corriendo: `python Flask_Server.py`
- Asegúrate que el puerto 5000 está disponible

### "Los datos no se actualizan"
- Verifica que estés enviando datos al endpoint `/ingest`
- Revisa la consola del navegador (F12) para errores

### "El mapa no aparece"
- Requiere conexión a internet (para cargar OpenStreetMap)
- Verifica la consola del navegador para errores de CORS

---

**Creado:** Diciembre 2025  
**Sistema:** Alerta de Inundaciones CDMX  
**Responsable:** Proyecto Terminal (TT2)
