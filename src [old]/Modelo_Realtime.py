from joblib import load
import numpy as np
import pandas as pd

# 1) Cargar el modelo ya entrenado
modelo = load("src [old]/modelo_riesgo.pkl")

def predecir_riesgo(precipitacion_mm: float, area_inundable: float = 100.0):
    """
    Devuelve:
      - nivel_riesgo_str: 'Bajo' o 'Alto'
      - prob_riesgo: probabilidad (confianza) asociada a la clase predicha
      - clase_binaria: 0 (Bajo) o 1 (Alto)
    """
    # Construir el vector de entrada con la misma estructura que en el entrenamiento
    X = pd.DataFrame([{
    "Precipitación_mm": precipitacion_mm,
    "Área_Inundable_%": area_inundable
    }])

    # Predicción de clase (0 o 1)
    clase = modelo.predict(X)[0]

    # Probabilidades por clase [P(Bajo), P(Alto)]
    probs = modelo.predict_proba(X)[0]
    prob_clase = probs[int(clase)]

    nivel = "Bajo" if clase == 0 else "Alto"
    return nivel, float(prob_clase), int(clase)


if __name__ == "__main__":
    print("=== Prueba rápida de predicción de riesgo ===")
    precip_str = input("Ingresa la precipitación (mm/24h): ")

    try:
        precip = float(precip_str)
    except ValueError:
        print("Valor no válido. Debes ingresar un número.")
        exit(1)

    # Por ahora usamos 100% como valor fijo de área inundable (de tu dataset)
    nivel, conf, clase = predecir_riesgo(precip)

    print(f"\nResultado del modelo:")
    print(f"  Precipitación: {precip:.2f} mm/24h")
    print(f"  Área inundable usada: 100 %")
    print(f"  Riesgo predicho: {nivel} (clase={clase})")
    print(f"  Confianza aproximada del modelo: {conf*100:.1f} %")