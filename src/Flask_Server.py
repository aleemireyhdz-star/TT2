from flask import Flask, request
from Realtime import predecir_alerta

app = Flask(__name__)

@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json(force=True, silent=True) or {}
    v = data.get("v")
    pct = data.get("pct")
    
    if isinstance(v, (int, float)) and isinstance(pct, (int, float)):
        print(f"v={v:.3f} V | pct={pct:.2f} %")
        
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
        
        print(f"🚨 Nivel sensor: {nivel_sensor} → Alerta: {resultado['alerta']}")
        
    else:
        print(data)
    
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    