#!/usr/bin/env python3
"""
Prueba específica para las coordenadas: 19.4949629462, -99.1486655987
"""

from joblib import load
import pandas as pd

def main():
    # Coordenadas solicitadas
    lat, lon = 19.4949629462, -99.1486655987
    
    print("🧪 === PRUEBA CON COORDENADAS ESPECÍFICAS ===")
    print(f"📍 Coordenadas: ({lat}, {lon})")
    print("=" * 60)
    
    # Cargar modelo
    modelo = load('modelo_predictivo.pkl')
    
    def validar_coordenadas_cdmx(lat, lon):
        return (19.35 <= lat <= 19.65 and -99.35 <= lon <= -98.95)

    def obtener_riesgo_zona(lat, lon):
        input_data = pd.DataFrame([[lat, lon]], columns=['latitud', 'longitud'])
        return modelo.predict(input_data)[0]

    def clasificar_riesgo_zona(score):
        if score <= 45:
            return 'BAJO'
        elif score <= 65:
            return 'MEDIO'
        else:
            return 'ALTO'

    def predecir_alerta_completa(lat, lon, sensor):
        riesgo_score = obtener_riesgo_zona(lat, lon)
        nivel_riesgo = clasificar_riesgo_zona(riesgo_score)
        
        if nivel_riesgo == 'BAJO':
            alerta = 'VERDE' if sensor <= 2 else 'AMARILLO'
        elif nivel_riesgo == 'MEDIO':
            if sensor <= 1:
                alerta = 'VERDE'
            elif sensor == 2:
                alerta = 'AMARILLO'
            else:
                alerta = 'ROJO'
        else:  # ALTO
            if sensor == 0:
                alerta = 'VERDE'
            elif sensor == 1:
                alerta = 'AMARILLO'
            else:
                alerta = 'ROJO'
        
        return alerta, nivel_riesgo, riesgo_score

    # Validar si está en CDMX
    en_cdmx = validar_coordenadas_cdmx(lat, lon)
    print(f"🗺️ Validación geográfica: {'✅ Dentro de CDMX' if en_cdmx else '❌ Fuera de CDMX'}")
    
    if not en_cdmx:
        print("⚠️ ADVERTENCIA: Coordenada fuera del rango de CDMX")
        print("📍 Rango válido: Lat 19.35-19.65, Lon -99.35 a -98.95")
        print("🤖 La predicción puede no ser confiable")

    # Obtener información base de la zona
    riesgo_score = obtener_riesgo_zona(lat, lon)
    nivel_riesgo = clasificar_riesgo_zona(riesgo_score)
    
    print(f"🎯 Riesgo base de la zona: {nivel_riesgo} (score: {riesgo_score:.1f})")

    # Verificar si esta coordenada está en el dataset
    df = pd.read_csv('dataset_procesado.csv')
    coord_en_dataset = df[(abs(df['latitud'] - lat) < 0.0001) & (abs(df['longitud'] - lon) < 0.0001)]

    if not coord_en_dataset.empty:
        row = coord_en_dataset.iloc[0]
        print(f"📊 ENCONTRADA EN DATASET:")
        print(f"   • Intensidad: {row['intensidad_mm']} mm")
        print(f"   • Área inundable: {row['area_inundable_pct']}%")
        print(f"   • Score dataset: {row['riesgo_zona_score']:.1f}")
        print(f"   • Nivel dataset: {row['nivel_riesgo_zona']}")
        print(f"   • Score modelo: {riesgo_score:.1f}")
        print(f"   • Diferencia: {abs(riesgo_score - row['riesgo_zona_score']):.1f} puntos")
    else:
        print("📊 Coordenada NO encontrada exactamente en dataset")

    print(f"\n🚨 PRUEBA CON TODOS LOS NIVELES DE SENSOR:")
    print("=" * 60)
    print(f"{'Sensor':<8} {'Alerta':<10} {'Emoji':<5} {'Explicación'}")
    print("-" * 60)

    emojis = {'VERDE': '🟢', 'AMARILLO': '🟡', 'ROJO': '🔴'}

    for sensor in range(4):
        alerta, nivel, score = predecir_alerta_completa(lat, lon, sensor)
        emoji = emojis[alerta]
        
        if alerta == 'VERDE':
            explicacion = 'Condiciones normales'
        elif alerta == 'AMARILLO':
            explicacion = 'Precaución recomendada'
        else:
            explicacion = 'Peligro - Acción inmediata'
        
        print(f"{sensor:<8} {alerta:<10} {emoji:<5} {explicacion}")

    print(f"\n🔍 ANÁLISIS DE REGLAS DE NEGOCIO:")
    print(f"   • Zona clasificada como: {nivel_riesgo}")

    if nivel_riesgo == 'BAJO':
        print("   • Regla BAJO: Sensor 0-2 → Verde, Sensor 3 → Amarillo")
    elif nivel_riesgo == 'MEDIO':
        print("   • Regla MEDIO: Sensor 0-1 → Verde, Sensor 2 → Amarillo, Sensor 3 → Rojo")
    else:
        print("   • Regla ALTO: Sensor 0 → Verde, Sensor 1 → Amarillo, Sensor 2-3 → Rojo")

    print(f"\n✅ RESULTADO: Las alertas siguen las reglas apropiadas para zona {nivel_riesgo}")
    
    # Comparación con coordenada hardcoded
    print(f"\n🔄 COMPARACIÓN CON COORDENADA HARDCODED DEL SISTEMA:")
    lat_hard, lon_hard = 19.5061618036, -99.1047492201
    score_hard = obtener_riesgo_zona(lat_hard, lon_hard)
    nivel_hard = clasificar_riesgo_zona(score_hard)
    
    print(f"   • Coordenada hardcoded: ({lat_hard}, {lon_hard})")
    print(f"   • Score hardcoded: {score_hard:.1f} ({nivel_hard})")
    print(f"   • Score nueva coordenada: {riesgo_score:.1f} ({nivel_riesgo})")
    print(f"   • Diferencia: {abs(riesgo_score - score_hard):.1f} puntos")

if __name__ == "__main__":
    main()
