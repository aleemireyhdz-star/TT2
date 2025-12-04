from flask import Flask, request, render_template, jsonify
from Realtime import predecir_alerta
import logging
from pathlib import Path

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configurar logging para que las salidas se vean claramente en la terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
app.logger.setLevel(logging.INFO)

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
        if v <= 0.683:
            nivel_sensor = 0
        elif v <= 0.759:
            nivel_sensor = 1
        elif v <= 0.812:
            nivel_sensor = 2
        else:
            nivel_sensor = 3
        
        # Hacer predicción con coordenadas hardcoded (se definen en Realtime.py)
        resultado = predecir_alerta(nivel_sensor)
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
            'coordenadas': {'latitud': 0, 'longitud': 0},
            'mensaje': 'Esperando datos del sensor...'
        })
    return jsonify(ultimo_resultado)

if __name__ == "__main__":
    app.logger.info("Iniciando servidor Flask (reloader desactivado para evitar cargas duplicadas)...")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    

