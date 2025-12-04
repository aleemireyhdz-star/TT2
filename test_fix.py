#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la corrección del problema de predicción
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from Realtime import predecir_alerta_con_coordenadas

def main():
    print("\n" + "="*70)
    print("TEST: Verificar que la coordenada problemática ahora da 39.2")
    print("="*70)
    
    # Coordenada que estaba dando 48.4 pero debería dar 39.2
    lat = 19.5061618036
    lon = -99.1047492201
    nivel_sensor = 0  # No importa para el test de riesgo_score
    
    print(f"\nCoordenadas: ({lat}, {lon})")
    print(f"Valor esperado en dataset: 39.2 (BAJO)")
    print(f"Valor que daba antes: 48.4")
    print("\nHaciendo predicción...")
    
    resultado = predecir_alerta_con_coordenadas(lat, lon, nivel_sensor)
    
    print(f"\n" + "-"*70)
    print("RESULTADO:")
    print("-"*70)
    print(f"Score predicho: {resultado['riesgo_score']}")
    print(f"Clasificación: {resultado['riesgo_zona']}")
    print(f"Alerta (sensor nivel {nivel_sensor}): {resultado['alerta']}")
    
    # Verificar si es correcto
    if resultado['riesgo_score'] == 39.2:
        print("\n✅ CORRECTO - El problema ha sido SOLUCIONADO")
    else:
        print(f"\n⚠️ Valor inesperado: {resultado['riesgo_score']} (esperado 39.2)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
