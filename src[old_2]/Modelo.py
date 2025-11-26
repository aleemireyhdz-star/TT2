import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, classification_report
from joblib import dump
import matplotlib.pyplot as plt
from pathlib import Path

# 1) Cargar el CSV generado por el script de datos sintéticos
# Asegúrate de que el archivo está en la misma carpeta que este script,
# o reemplaza el nombre por la ruta completa.
df = pd.read_csv("src/precipitaciones_sinteticas.csv")

print("Primeras filas del dataset:")
print(df.head())
print("\nDescripción estadística:")
print(df.describe())

# 2) Crear etiqueta de riesgo basada en la precipitación
#    Aquí definimos una regla simple para tener 2 clases (0 = bajo, 1 = alto).
#    Ajusta el umbral (58) si lo consideras conveniente.
umbral_alto = 58.0  # mm/24h

df["Riesgo"] = (df["Precipitación_mm"] >= umbral_alto).astype(int)

print("\nDistribución de la etiqueta Riesgo:")
print(df["Riesgo"].value_counts())

# 3) Definir características (X) y etiquetas (y)
#    Usamos tanto la precipitación como el área inundable como entradas del modelo.
X = df[["Precipitación_mm", "Área_Inundable_%"]]
y = df["Riesgo"]

# 4) Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 5) Crear y entrenar el modelo de Árbol de Decisión
modelo = DecisionTreeClassifier(
    random_state=42,
    max_depth=3  # puedes cambiar esto para hacer el árbol más complejo o más simple
)
modelo.fit(X_train, y_train)

# 6) Evaluar el modelo
y_pred = modelo.predict(X_test)

print("\nPrecisión del modelo:", accuracy_score(y_test, y_pred))
print("\nReporte de clasificación:")
print(classification_report(y_test, y_pred, target_names=["Bajo", "Alto"]))

# 7) Visualizar el árbol de decisión (opcional pero muy útil)
plt.figure(figsize=(10, 6))
plot_tree(
    modelo,
    filled=True,
    feature_names=["Precipitación_mm", "Área_Inundable_%"],
    class_names=["Bajo", "Alto"],
    rounded=True
)
plt.title("Árbol de decisión - Riesgo de inundación (prototipo)")
plt.tight_layout()
plt.show()

# 8) Guardar el modelo entrenado en un archivo .pkl dentro de la misma carpeta del script
script_dir = Path(__file__).resolve().parent
model_path = script_dir / "modelo_predictivo.pkl"
dump(modelo, model_path)
print(f"\nModelo guardado como: 'modelo_predictivo.pkl'")