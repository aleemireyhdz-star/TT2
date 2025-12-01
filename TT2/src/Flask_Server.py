from flask import Flask, request
from Realtime import predecir_alerta
import logging

app = Flask(__name__)

# Configurar logging para que las salidas se vean claramente en la terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
app.logger.setLevel(logging.INFO)

@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json(force=True, silent=True) or {}
    v = data.get("v")
    pct = data.get("pct")
    
    if isinstance(v, (int, float)) and isinstance(pct, (int, float)):
        app.logger.info(f"v={v:.3f} V | pct={pct:.2f} %")
        
        # Mapear voltaje a nivel de sensor (0-3)
        # Asumiendo rangos: 0-0.75V=0, 0.75-1.5V=1, 1.5-2.25V=2, 2.25-3V=3
        if v <= 0.75:
            nivel_sensor = 0
        elif v <= 1.5:
            nivel_sensor = 1
        elif v <= 2.25:
            nivel_sensor = 2
        else:
            nivel_sensor = 3
        
        # Hacer predicción con coordenadas hardcoded (se definen en Realtime.py)
        resultado = predecir_alerta(nivel_sensor)
        
        app.logger.info(f"🚨 Nivel sensor: {nivel_sensor} → Alerta: {resultado['alerta']}")
        
    else:
        app.logger.info(f"Datos recibidos inválidos o vacíos: {data}")
    
    return {"ok": True}


@app.route("/", methods=["GET"])
def health():
    """Endpoint simple para comprobar que el servidor está arriba"""
    app.logger.info("Health check recibido")
    return {"ok": True, "status": "running"}

if __name__ == "__main__":
    app.logger.info("Iniciando servidor Flask (reloader desactivado para evitar cargas duplicadas)...")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    