import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Parámetros para las precipitaciones
media_precipitacion = 57  # Promedio de 54 a 60 mm/24h
desviacion_estandar = 2   # Desviación estándar ajustable

# Generación de 1000 datos sintéticos de precipitaciones (en mm/24h)
np.random.seed(42)  # Fijar semilla para reproducibilidad
precipitaciones_sinteticas = np.random.normal(media_precipitacion, desviacion_estandar, 1000)

# Crear DataFrame
df = pd.DataFrame(precipitaciones_sinteticas, columns=["Precipitación_mm"])

# Filtrar valores negativos (si ocurren, lo cual no tiene sentido físico)
df = df[df["Precipitación_mm"] > 0]

# Parámetro adicional: área inundable (este es un dato constante basado en tu dataset)
area_inundable = 100  # Porcentaje de área inundable (valor del 100%)

# Agregar área inundable como columna constante en el DataFrame
df["Área_Inundable_%"] = area_inundable

# Mostrar las primeras filas
print(df.head())

# Visualizar los datos generados
plt.hist(df["Precipitación_mm"], bins=30, edgecolor='black')
plt.title('Distribución de Precipitaciones Sintéticas')
plt.xlabel('Precipitación (mm/24h)')
plt.ylabel('Frecuencia')
plt.show()

# Guardar el DataFrame generado en un archivo CSV dentro de la misma carpeta del script
script_dir = Path(__file__).resolve().parent
output_csv = script_dir / "precipitaciones_sinteticas.csv"
df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"Archivo CSV guardado en: {output_csv}")