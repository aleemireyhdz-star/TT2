import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from joblib import dump
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# 1) Cargar el dataset procesado con coordenadas y valores numéricos
print("🔄 Cargando dataset procesado...")
df = pd.read_csv("dataset_procesado.csv")

print("📊 Primeras filas del dataset:")
print(df.head())
print(f"\n📈 Dataset: {len(df)} ubicaciones únicas")
print(f"📍 Rango de coordenadas:")
print(f"   • Latitud: {df['latitud'].min():.6f} a {df['latitud'].max():.6f}")
print(f"   • Longitud: {df['longitud'].min():.6f} a {df['longitud'].max():.6f}")
print(f"⚡ Rango de riesgo: {df['riesgo_zona_score'].min():.1f} a {df['riesgo_zona_score'].max():.1f}")

print(f"\n🎯 Distribución por nivel de riesgo de zona:")
print(df['nivel_riesgo_zona'].value_counts())

# 2) Definir características (X) y etiqueta objetivo (y)
# ENTRADA: [latitud, longitud] -> SALIDA: riesgo_zona_score
X = df[["latitud", "longitud"]]
y = df["riesgo_zona_score"]

print(f"\n🧠 Configuración del modelo:")
print(f"   • Entradas: {list(X.columns)}")
print(f"   • Salida: riesgo_zona_score (continuo)")
print(f"   • Algoritmo: Random Forest Regressor")

# 3) Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4) Crear y entrenar el modelo Random Forest Regressor
print(f"\n🚀 Entrenando modelo...")
modelo = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    max_depth=10
)
modelo.fit(X_train, y_train)

# 5) Evaluar el modelo
y_pred = modelo.predict(X_test)

print(f"\n📊 Evaluación del modelo:")
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"   • Error cuadrático medio: {mse:.2f}")
print(f"   • R² Score: {r2:.3f}")
print(f"   • Error promedio: ±{np.sqrt(mse):.2f} puntos de riesgo")

# 6) Mostrar importancia de características
feature_importance = modelo.feature_importances_
print(f"\n🎯 Importancia de características:")
for i, feature in enumerate(X.columns):
    print(f"   • {feature}: {feature_importance[i]:.3f}")

# 7) Visualizar predicciones vs reales
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.6)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Riesgo Real')
plt.ylabel('Riesgo Predicho')
plt.title('Predicciones vs Valores Reales - Riesgo de Zona')
plt.grid(True, alpha=0.3)
plt.show()

# 8) Guardar el modelo entrenado
try:
    # Si estamos ejecutando el archivo directamente
    script_dir = Path(__file__).resolve().parent
    model_path = script_dir / "modelo_predictivo.pkl"
except NameError:
    # Si estamos ejecutando desde un snippet (sin __file__)
    model_path = Path("modelo_predictivo.pkl")

dump(modelo, model_path)
print(f"\n💾 Modelo guardado como: 'modelo_predictivo.pkl'")

print(f"\n✅ Modelo entrenado y guardado exitosamente!")
print(f"🔄 Para usar el modelo, ejecuta: python3 Realtime.py")
print(f"🌐 Para el servidor web, ejecuta: python3 Flask_Server.py")