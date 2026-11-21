"""
ETAPA 1 - Preparación de datos.

Carga el dataset Iris desde scikit-learn y lo divide en entrenamiento y prueba
(80/20, estratificado por especie). Los archivos quedan en data/train.csv y
data/test.csv para que las siguientes etapas trabajen sobre archivos reales,
igual que pasaría con datos de producción.
"""
import csv
import os

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATOS = os.path.join(RAIZ, "data")
RUTA_TRAIN = os.path.join(CARPETA_DATOS, "train.csv")
RUTA_TEST = os.path.join(CARPETA_DATOS, "test.csv")

COLUMNAS = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
SEMILLA = 42


def guardar_csv(ruta, X, y):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(COLUMNAS)
        for fila, etiqueta in zip(X, y):
            escritor.writerow([round(float(v), 1) for v in fila] + [int(etiqueta)])


def main():
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    datos = load_iris()

    X_train, X_test, y_train, y_test = train_test_split(
        datos.data,
        datos.target,
        test_size=0.2,
        random_state=SEMILLA,
        stratify=datos.target,
    )

    guardar_csv(RUTA_TRAIN, X_train, y_train)
    guardar_csv(RUTA_TEST, X_test, y_test)

    print(f"  Registros totales: {len(datos.data)}")
    print(f"  train.csv -> {len(X_train)} filas")
    print(f"  test.csv  -> {len(X_test)} filas")
    print(f"  Archivos guardados en: {CARPETA_DATOS}")


if __name__ == "__main__":
    main()
