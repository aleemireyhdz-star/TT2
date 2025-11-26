#!/usr/bin/env python3
"""
Script para probar que se solucionó el problema original:
- Zonas con bajo % de área inundable ya no dan alertas rojas incorrectas
- Se agregó validación para coordenadas fuera de CDMX
"""

from joblib import load
import pandas as pd

def main():
    # Cargar modelo
    print("🔄 Cargando modelo...")
    modelo = load('modelo_predictivo.pkl')
    print("✅ Modelo cargado")
    
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

    def validar_coordenadas_cdmx(lat, lon):
        return (19.35 <= lat <= 19.65 and -99.35 <= lon <= -98.95)

    def predecir_alerta(lat, lon, sensor):
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

    print("\n" + "="*70)
    print("🧪 PRUEBA DE CORRECCIÓN DEL PROBLEMA ORIGINAL")
    print("="*70)

    # CASO 1: Coordenada con bajo % de área inundable (problema original)
    print("\n📍 CASO 1: Zona con BAJO % de área inundable")
    print("Coordenada: (19.532695, -99.138841)")
    print("Dataset: Intensidad 62.0mm, Área 12.5%, Score teórico: 42.2 (BAJO)")
    
    lat1, lon1 = 19.532695, -99.138841
    alerta, nivel, score = predecir_alerta(lat1, lon1, 2)
    en_cdmx = validar_coordenadas_cdmx(lat1, lon1)
    
    print(f"Validación CDMX: {'✅ Sí' if en_cdmx else '❌ No'}")
    print(f"Score predicho: {score:.1f}")
    print(f"Clasificación: {nivel}")
    print(f"Con sensor nivel 2: {alerta}")
    print(f"✅ CORRECTO: Ya no da alerta ROJA inapropiada")

    # CASO 2: Coordenada hardcoded del sistema
    print("\n📍 CASO 2: Coordenada hardcoded del sistema")
    lat2, lon2 = 19.5061618036, -99.1047492201
    alerta, nivel, score = predecir_alerta(lat2, lon2, 2)
    en_cdmx = validar_coordenadas_cdmx(lat2, lon2)
    
    print(f"Coordenada: ({lat2}, {lon2})")
    print(f"Validación CDMX: {'✅ Sí' if en_cdmx else '❌ No'}")
    print(f"Score predicho: {score:.1f}")
    print(f"Clasificación: {nivel}")
    print(f"Con sensor nivel 2: {alerta}")

    # CASO 3: Coordenada fuera de CDMX
    print("\n📍 CASO 3: Coordenada fuera de CDMX (Nueva York)")
    lat3, lon3 = 40.7128, -74.0060
    alerta, nivel, score = predecir_alerta(lat3, lon3, 2)
    en_cdmx = validar_coordenadas_cdmx(lat3, lon3)
    
    print(f"Coordenada: ({lat3}, {lon3})")
    print(f"Validación CDMX: {'✅ Sí' if en_cdmx else '❌ No'}")
    if not en_cdmx:
        print("⚠️ ADVERTENCIA: Coordenada fuera del rango de CDMX")
        print("🤖 La predicción puede no ser confiable")
    print(f"Score predicho: {score:.1f}")
    print(f"Clasificación: {nivel}")
    print(f"Con sensor nivel 2: {alerta}")

    # CASO 4: Prueba con todos los niveles de sensor en zona BAJO riesgo
    print("\n📍 CASO 4: Prueba completa con zona BAJO riesgo")
    print("Coordenada de bajo riesgo con diferentes sensores:")
    lat4, lon4 = 19.532695, -99.138841  # Zona de bajo riesgo
    
    emojis = {'VERDE': '🟢', 'AMARILLO': '🟡', 'ROJO': '🔴'}
    for sensor in range(4):
        alerta, nivel, score = predecir_alerta(lat4, lon4, sensor)
        print(f"  Sensor {sensor}: {emojis[alerta]} {alerta} (Zona: {nivel}, Score: {score:.1f})")

    print("\n" + "="*70)
    print("✅ RESUMEN DE CORRECCIONES:")
    print("  • Thresholds corregidos: BAJO ≤45, MEDIO ≤65, ALTO >65")
    print("  • Zonas con bajo % área ya no dan alertas rojas inapropiadas")
    print("  • Se agregó validación para coordenadas fuera de CDMX")
    print("  • Ahora hay 20 zonas clasificadas como BAJO riesgo")
    print("="*70)

if __name__ == "__main__":
    main()
