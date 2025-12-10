from flask import Flask, request, render_template, jsonify
from Realtime import predecir_alerta_con_coordenadas, validar_coordenadas_cdmx, LATITUD_FIJA, LONGITUD_FIJA
import logging
from pathlib import Path
import json

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configurar logging para que las salidas se vean claramente en la terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
app.logger.setLevel(logging.INFO)

# Directorio y archivo de configuración para coordenadas persistentes
script_dir = Path(__file__).resolve().parent
_coords_config_file = script_dir / "coords_config.json"

# Coordenadas actuales (inicializadas desde Realtime defaults)
coordenadas_actuales = {
    'latitud': LATITUD_FIJA,
    'longitud': LONGITUD_FIJA
}

# Intentar cargar coordenadas persistidas si existen
try:
    if _coords_config_file.exists():
        with open(_coords_config_file, 'r', encoding='utf-8') as _f:
            data = json.load(_f)
            if 'latitud' in data and 'longitud' in data:
                coordenadas_actuales['latitud'] = float(data['latitud'])
                coordenadas_actuales['longitud'] = float(data['longitud'])
                app.logger.info(f"📍 Coordenadas cargadas desde {_coords_config_file}")
except Exception as _e:
    app.logger.warning(f"No se pudieron cargar coordenadas guardadas: {_e}")

# Variable global para almacenar el último resultado de predicción
ultimo_resultado = None

@app.route("/ingest", methods=["POST"])
def ingest():
    global ultimo_resultado
    data = request.get_json(force=True, silent=True) or {}
    v = data.get("v")
    pct = data.get("pct")
    
    if isinstance(v, (int, float)) and isinstance(pct, (int, float)):
        app.logger.info(f"v={v:.3f} V | pct={pct:.2f} %")
        
        # Mapear voltaje a nivel de sensor (0-3)
        # Asumiendo rangos: 0-0.75V=0, 0.75-1.5V=1, 1.5-2.25V=2, 2.25-3V=3
        if v <= 0.695:
            nivel_sensor = 0
        elif v <= 0.759:
            nivel_sensor = 1
        elif v <= 0.812:
            nivel_sensor = 2
        else:
            nivel_sensor = 3
        
        # Hacer predicción usando las coordenadas guardadas actualmente
        resultado = predecir_alerta_con_coordenadas(
            coordenadas_actuales['latitud'],
            coordenadas_actuales['longitud'],
            nivel_sensor
        )
        ultimo_resultado = resultado
        
        app.logger.info(f"🚨 Nivel sensor: {nivel_sensor} → Alerta: {resultado['alerta']}")
        app.logger.info(f"Detalles de la predicción: {resultado}")

    else:
        app.logger.info(f"Datos recibidos inválidos o vacíos: {data}")
    
    return {"ok": True}


@app.route("/", methods=["GET"])
def index():
    """Sirve la página web principal"""
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    """API endpoint que retorna el último estado de predicción"""
    if ultimo_resultado is None:
        return jsonify({
            'alerta': 'GRIS',
            'riesgo_zona': 'DESCONOCIDO',
            'riesgo_score': 0,
            'nivel_sensor': -1,
            'coordenadas': coordenadas_actuales,
            'mensaje': 'Esperando datos del sensor...'
        })
    return jsonify(ultimo_resultado)


@app.route("/api/coords", methods=["GET"])
def api_get_coords():
    """Devuelve las coordenadas actualmente configuradas"""
    return jsonify(coordenadas_actuales)


@app.route("/api/coords", methods=["POST"])
def api_set_coords():
    """Permite establecer coordenadas desde la web. Guarda en disco."""
    global coordenadas_actuales
    data = request.get_json(force=True, silent=True) or {}
    lat = data.get('lat')
    lon = data.get('lon')
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'lat y lon deben ser números'}), 400

    coordenadas_actuales['latitud'] = lat
    coordenadas_actuales['longitud'] = lon

    # Guardar persistente
    try:
        with open(_coords_config_file, 'w', encoding='utf-8') as _f:
            json.dump(coordenadas_actuales, _f)
    except Exception as e:
        app.logger.warning(f"No se pudo guardar coordenadas: {e}")

    # Log de validación geográfica (opcional)
    if not validar_coordenadas_cdmx(lat, lon):
        app.logger.warning(f"⚠️ Coordenadas fuera de rango CDMX: ({lat}, {lon})")

    app.logger.info(f"📍 Coordenadas actualizadas → {coordenadas_actuales}")
    return jsonify({'ok': True, 'coordenadas': coordenadas_actuales})

if __name__ == "__main__":
    import os
    
    # Detectar ambiente (desarrollo vs producción)
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    if debug_mode:
        app.logger.info("🔧 MODO DESARROLLO - Iniciando servidor Flask...")
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    else:
        app.logger.info("🚀 MODO PRODUCCIÓN - Iniciando servidor Flask...")
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    

