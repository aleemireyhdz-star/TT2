from joblib import load
import pandas as pd
from pathlib import Path

# 1) Cargar el modelo ya entrenado
script_dir = Path(__file__).resolve().parent
model_path = script_dir / "modelo_predictivo.pkl"

try:
    modelo = load(model_path)
    print("✅ Modelo cargado exitosamente")
except FileNotFoundError:
    print("❌ Error: No se encontró 'modelo_predictivo.pkl'")
    print("🔄 Ejecuta primero: python3 Modelo.py")
    exit(1)

def validar_coordenadas_cdmx(latitud, longitud):
    """
    Valida si las coordenadas están dentro del rango aproximado de CDMX.
    
    Args:
        latitud (float): Latitud de la ubicación
        longitud (float): Longitud de la ubicación
    
    Returns:
        bool: True si está dentro de CDMX, False si no
    """
    # Rangos aproximados de CDMX basados en el dataset
    LAT_MIN, LAT_MAX = 19.35, 19.65
    LON_MIN, LON_MAX = -99.35, -98.95
    
    return (LAT_MIN <= latitud <= LAT_MAX and LON_MIN <= longitud <= LON_MAX)

def obtener_riesgo_zona(latitud, longitud):
    """
    Predice el riesgo de zona basado en coordenadas geográficas.
    Primero busca en el dataset si la coordenada exacta existe (con tolerancia).
    Si no, usa el modelo de predicción.
    
    Args:
        latitud (float): Latitud de la ubicación
        longitud (float): Longitud de la ubicación
    
    Returns:
        float: Score de riesgo de zona (39.2 - 77.2)
    """
    # Validar si las coordenadas están dentro de CDMX
    if not validar_coordenadas_cdmx(latitud, longitud):
        print(f"⚠️ ADVERTENCIA: Las coordenadas ({latitud}, {longitud}) están fuera del rango de CDMX")
        print(f"📍 Rango válido: Lat 19.35-19.65, Lon -99.35 a -98.95")
        print(f"🤖 La predicción puede no ser confiable para ubicaciones fuera de CDMX")
    
    # MEJORA: Primero buscar en el dataset si existe esta coordenada exacta
    # Tolerancia de ±0.0001 grados (≈ 10 metros)
    dataset = pd.read_csv(script_dir / "dataset_procesado.csv")
    coincidencia = dataset[
        (abs(dataset['latitud'] - latitud) < 0.0001) & 
        (abs(dataset['longitud'] - longitud) < 0.0001)
    ]
    
    if not coincidencia.empty:
        # Si encontramos la coordenada en el dataset, usar su valor real
        riesgo_score = coincidencia['riesgo_zona_score'].iloc[0]
        print(f"🎯 Coordenada encontrada en dataset → Score: {riesgo_score:.1f}")
        return riesgo_score
    
    # Si no está en el dataset, usar el modelo de predicción
    print(f"🔮 Coordenada no en dataset → Usando modelo de predicción")
    input_data = pd.DataFrame([[latitud, longitud]], columns=['latitud', 'longitud'])
    riesgo_score = modelo.predict(input_data)[0]
    return riesgo_score

def clasificar_riesgo_zona(riesgo_score):
    """
    Clasifica el score de riesgo en categorías.
    
    Args:
        riesgo_score (float): Score de riesgo de zona
    
    Returns:
        str: Nivel de riesgo ('BAJO', 'MEDIO', 'ALTO')
    """
    if riesgo_score <= 45:
        return 'BAJO'
    elif riesgo_score <= 65:
        return 'MEDIO'
    else:
        return 'ALTO'

# Coordenadas hardcoded BAJA
#LATITUD_FIJA = 19.5061618036
#LONGITUD_FIJA = -99.1047492201
# Coordenadas hardcoded ALTA 19.5228166649,-99.1678551529
#LATITUD_FIJA = 19.5228166649
#LONGITUD_FIJA = -99.1678551529
# Coordenadas UPIITA 19.5113119,-99.1251155
#LATITUD_FIJA = 19.5113119
#LONGITUD_FIJA = -99.1251155
#Coordenada hardcoded MEDIA 19.5041017692,-99.0986932319
LATITUD_FIJA = 19.5041017692
LONGITUD_FIJA = -99.0986932319


def predecir_alerta(nivel_sensor):
    """
    Función principal que predice el color de alerta basado en:
    - Ubicación geográfica (coordenadas hardcoded)
    - Nivel del sensor (0-3)
    
    Args:
        nivel_sensor (int): Nivel del sensor (0=seco, 1=bajo, 2=medio, 3=alto)
    
    Returns:
        dict: {
            'alerta': str ('VERDE', 'AMARILLO', 'ROJO'),
            'riesgo_zona': str ('BAJO', 'MEDIO', 'ALTO'),
            'riesgo_score': float,
            'nivel_sensor': int,
            'coordenadas': dict
        }
    """
    # Paso 1: Obtener riesgo de la zona usando coordenadas hardcoded
    riesgo_score = obtener_riesgo_zona(LATITUD_FIJA, LONGITUD_FIJA)
    nivel_riesgo = clasificar_riesgo_zona(riesgo_score)
    
    # Paso 2: Aplicar reglas de negocio combinando riesgo de zona + nivel sensor
    if nivel_riesgo == 'BAJO':
        # Zona de BAJO riesgo: 0-2→Verde, 3→Amarillo
        if nivel_sensor <= 2:
            alerta = 'VERDE'
        else:
            alerta = 'AMARILLO'
    
    elif nivel_riesgo == 'MEDIO':
        # Zona de riesgo MEDIO: 0-1→Verde, 2→Amarillo, 3→Rojo
        if nivel_sensor <= 1:
            alerta = 'VERDE'
        elif nivel_sensor == 2:
            alerta = 'AMARILLO'
        else:
            alerta = 'ROJO'
    
    else:  # ALTO riesgo
        # Zona de ALTO riesgo: 0→Verde, 1→Amarillo, 2-3→Rojo
        if nivel_sensor == 0:
            alerta = 'VERDE'
        elif nivel_sensor == 1:
            alerta = 'AMARILLO'
        else:
            alerta = 'ROJO'
    
    return {
        'alerta': alerta,
        'riesgo_zona': nivel_riesgo,
        'riesgo_score': round(riesgo_score, 1),
        'nivel_sensor': nivel_sensor,
        'coordenadas': {'latitud': LATITUD_FIJA, 'longitud': LONGITUD_FIJA}
    }

def predecir_alerta_con_coordenadas(latitud, longitud, nivel_sensor):
    """
    Función auxiliar para pruebas con coordenadas personalizadas
    """
    riesgo_score = obtener_riesgo_zona(latitud, longitud)
    nivel_riesgo = clasificar_riesgo_zona(riesgo_score)
    
    if nivel_riesgo == 'BAJO':
        if nivel_sensor <= 2:
            alerta = 'VERDE'
        else:
            alerta = 'AMARILLO'
    elif nivel_riesgo == 'MEDIO':
        if nivel_sensor <= 1:
            alerta = 'VERDE'
        elif nivel_sensor == 2:
            alerta = 'AMARILLO'
        else:
            alerta = 'ROJO'
    else:  # ALTO riesgo
        if nivel_sensor == 0:
            alerta = 'VERDE'
        elif nivel_sensor == 1:
            alerta = 'AMARILLO'
        else:
            alerta = 'ROJO'
    
    return {
        'alerta': alerta,
        'riesgo_zona': nivel_riesgo,
        'riesgo_score': round(riesgo_score, 1),
        'nivel_sensor': nivel_sensor,
        'coordenadas': {'latitud': latitud, 'longitud': longitud}
    }




def test_coordenadas_especificas():
    """
    Función para probar coordenadas específicas y diagnosticar problemas
    """
    print("\n" + "="*60)
    print("🧪 MODO PRUEBA DE COORDENADAS ESPECÍFICAS")
    print("="*60)
    
    # Coordenadas de prueba
    coordenadas_prueba = [
        (19.4326, -99.1332, "Ciudad de México (Centro)"),
        (19.5061618036, -99.1047492201, "Coordenada hardcoded del sistema"),
        (40.7128, -74.0060, "Nueva York (fuera de CDMX)"),
        (25.7617, -100.3016, "Monterrey (fuera de CDMX)"),
        (19.35, -99.35, "Límite sudoeste de CDMX"),
        (19.65, -98.95, "Límite nordeste de CDMX")
    ]
    
    print("Probando diferentes coordenadas con sensor nivel 2 (medio):")
    print("-" * 60)
    
    for lat, lon, descripcion in coordenadas_prueba:
        print(f"\n📍 {descripcion}")
        print(f"   Coordenadas: ({lat}, {lon})")
        
        # Validar si está en CDMX
        en_cdmx = validar_coordenadas_cdmx(lat, lon)
        print(f"   En CDMX: {'✅ Sí' if en_cdmx else '❌ No'}")
        
        # Hacer predicción
        try:
            resultado = predecir_alerta_con_coordenadas(lat, lon, 2)
            print(f"   Riesgo zona: {resultado['riesgo_zona']} (score: {resultado['riesgo_score']})")
            print(f"   Alerta: {resultado['alerta']}")
        except Exception as e:
            print(f"   ❌ Error en predicción: {e}")

def main_original():
    """Código principal original del sistema"""
    print("🚨 === Sistema de Predicción de Alertas de Inundación ===")
    print(f"📍 Coordenadas fijas: ({LATITUD_FIJA}, {LONGITUD_FIJA})")
    print("📋 Nivel sensor: 0=seco, 1=bajo, 2=medio, 3=alto")
    
    try:
        sensor_str = input("\n📡 Ingresa nivel del sensor (0-3): ")
        nivel_sensor = int(sensor_str)
        
        # Validar nivel del sensor
        if not 0 <= nivel_sensor <= 3:
            print("❌ Error: El nivel del sensor debe estar entre 0 y 3")
            exit(1)
        
        # Hacer predicción con coordenadas hardcoded
        resultado = predecir_alerta(nivel_sensor)
        
        # Mostrar resultado
        print(f"\n" + "="*50)
        print(f"📊 RESULTADO DE LA PREDICCIÓN")
        print(f"="*50)
        print(f"📍 Coordenadas: ({resultado['coordenadas']['latitud']}, {resultado['coordenadas']['longitud']})")
        print(f"📡 Nivel sensor: {nivel_sensor}")
        print(f"🎯 Riesgo zona: {resultado['riesgo_zona']} (score: {resultado['riesgo_score']})")
        
        # Mostrar alerta con emoji
        emoji_alerta = {
            'VERDE': '🟢',
            'AMARILLO': '🟡', 
            'ROJO': '🔴'
        }
        print(f"🚨 ALERTA: {emoji_alerta[resultado['alerta']]} {resultado['alerta']}")
        
        # Explicación de la alerta
        print(f"\n💡 Explicación:")
        if resultado['alerta'] == 'VERDE':
            print("   ✅ Condiciones normales - No se requiere acción")
        elif resultado['alerta'] == 'AMARILLO':
            print("   ⚠️ Precaución - Monitoreo continuo recomendado")
        else:
            print("   🚨 Peligro - Tomar medidas de seguridad inmediatas")
        
        # Pruebas adicionales con diferentes niveles
        print(f"\n🧪 Pruebas con diferentes niveles de sensor en esta ubicación:")
        for test_nivel in range(4):
            test_resultado = predecir_alerta(test_nivel)
            emoji = emoji_alerta[test_resultado['alerta']]
            print(f"   Sensor {test_nivel}: {emoji} {test_resultado['alerta']}")
        
        # Diagnóstico adicional
        print(f"\n🔍 Diagnóstico detallado:")
        print(f"   • Validación geográfica: {'✅ Dentro de CDMX' if validar_coordenadas_cdmx(LATITUD_FIJA, LONGITUD_FIJA) else '❌ Fuera de CDMX'}")
        print(f"   • Rango esperado de score: 28.5 (BAJO) - 80.2 (ALTO)")
        print(f"   • Score actual: {resultado['riesgo_score']}")
        
        # Mostrar cómo se calcularía manualmente
        print(f"\n🧮 Cálculo teórico del score (para referencia):")
        print(f"   • Formula: intensidad_mm * 0.6 + area_inundable_pct * 0.4")
        print(f"   • Rango intensidad: 47.5-67.0 mm")
        print(f"   • Rango área: 12.5-100.0 %")
        print(f"   • Score mínimo: 47.5*0.6 + 12.5*0.4 = {47.5*0.6 + 12.5*0.4}")
        print(f"   • Score máximo: 67.0*0.6 + 100.0*0.4 = {67.0*0.6 + 100.0*0.4}")
        
    except ValueError:
        print("❌ Error: El nivel del sensor debe ser un número entero entre 0 y 3.")
        exit(1)

# Agregar opción para ejecutar las pruebas
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_coordenadas_especificas()
    else:
        main_original()