import pandas as pd
import numpy as np

# Mapeos de rangos string a valores numéricos
intensidad_map = {
    '41 a 54': 47.5,    # RIESGO BAJO
    '54 a 60': 57.0,    # RIESGO MEDIO-BAJO
    '60 a 64': 62.0,    # RIESGO MEDIO-ALTO  
    '64 a 70': 67.0     # RIESGO ALTO
}

area_map = {
    '0 a 25': 12.5,     # RIESGO MUY BAJO
    '26 a 49': 37.5,    # RIESGO BAJO
    '50 a 72': 61.0,    # RIESGO MEDIO
    '73 a 99': 86.0,    # RIESGO ALTO
    '100': 100.0        # RIESGO MUY ALTO
}

def procesar_dataset():
    print("🔄 Cargando dataset original...")
    
    # Cargar el dataset con encoding correcto
    df = pd.read_csv('Dataset - Full(Dataset).csv', encoding='latin-1')
    
    print(f"✅ Dataset cargado: {len(df)} filas")
    print(f"📊 Columnas originales: {list(df.columns)}")
    
    # Separar coordenadas en latitud y longitud
    print("\n🗺️ Procesando coordenadas...")
    coords = df['coordinates'].str.strip('"').str.split(',', expand=True)
    df['latitud'] = coords[0].astype(float)
    df['longitud'] = coords[1].astype(float)
    
    # Convertir intensidad de precipitación
    print("🌧️ Procesando intensidad de precipitación...")
    df['intensidad_mm'] = df['intens_mm'].map(intensidad_map)
    
    # Convertir porcentaje de área inundable
    print("💧 Procesando porcentaje de área inundable...")
    df['area_inundable_pct'] = df['%_área'].map(area_map)
    
    # Crear score de riesgo combinado (promedio ponderado)
    # Intensidad tiene más peso (60%) que área (40%)
    df['riesgo_zona_score'] = (df['intensidad_mm'] * 0.6 + df['area_inundable_pct'] * 0.4)
    
    # Clasificar zona por nivel de riesgo basado en score
    def clasificar_zona(score):
        if score <= 45:
            return 'BAJO'
        elif score <= 65:
            return 'MEDIO'
        else:
            return 'ALTO'
    
    df['nivel_riesgo_zona'] = df['riesgo_zona_score'].apply(clasificar_zona)
    
    # Crear dataset procesado con columnas relevantes
    df_procesado = df[['latitud', 'longitud', 'intensidad_mm', 'area_inundable_pct', 
                       'riesgo_zona_score', 'nivel_riesgo_zona']].copy()
    
    # Eliminar duplicados para optimizar el dataset
    df_procesado = df_procesado.drop_duplicates()
    
    print(f"\n📈 Dataset procesado:")
    print(f"   • Filas después de eliminar duplicados: {len(df_procesado)}")
    print(f"   • Rango de intensidad: {df_procesado['intensidad_mm'].min():.1f} - {df_procesado['intensidad_mm'].max():.1f} mm")
    print(f"   • Rango de área inundable: {df_procesado['area_inundable_pct'].min():.1f} - {df_procesado['area_inundable_pct'].max():.1f} %")
    print(f"   • Rango de score de riesgo: {df_procesado['riesgo_zona_score'].min():.1f} - {df_procesado['riesgo_zona_score'].max():.1f}")
    
    print(f"\n🎯 Distribución por nivel de riesgo:")
    print(df_procesado['nivel_riesgo_zona'].value_counts())
    
    # Guardar dataset procesado
    output_file = 'dataset_procesado.csv'
    df_procesado.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 Dataset procesado guardado como: {output_file}")
    
    # Mostrar muestra del dataset procesado
    print(f"\n📋 Primeras 5 filas del dataset procesado:")
    print(df_procesado.head())
    
    return df_procesado

if __name__ == "__main__":
    dataset_procesado = procesar_dataset()
