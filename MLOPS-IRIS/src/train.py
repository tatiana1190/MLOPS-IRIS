"""
ETAPA 3 - Entrenamiento del modelo.

Entrena un Random Forest con data/train.csv, lo evalúa con data/test.csv y
guarda el modelo entrenado y sus métricas en la carpeta models/, para que las
pruebas automáticas puedan verificarlos.
"""
import csv
import json
import os
import pickle
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_TRAIN = os.path.join(RAIZ, "data", "train.csv")
RUTA_TEST = os.path.join(RAIZ, "data", "test.csv")
CARPETA_MODELOS = os.path.join(RAIZ, "models")
RUTA_MODELO = os.path.join(CARPETA_MODELOS, "model.pkl")
RUTA_METRICAS = os.path.join(CARPETA_MODELOS, "metrics.json")

# Hiperparámetros del baseline
N_ESTIMATORS = 100
MAX_DEPTH = None
SEMILLA = 42

CARACTERISTICAS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
OBJETIVO = "species"


def leer_csv(ruta):
    X, y = [], []
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            X.append([float(fila[c]) for c in CARACTERISTICAS])
            y.append(int(fila[OBJETIVO]))
    return X, y


def main():
    X_train, y_train = leer_csv(RUTA_TRAIN)
    X_test, y_test = leer_csv(RUTA_TEST)

    modelo = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=SEMILLA,
    )
    modelo.fit(X_train, y_train)
    accuracy = modelo.score(X_test, y_test)

    os.makedirs(CARPETA_MODELOS, exist_ok=True)
    with open(RUTA_MODELO, "wb") as f:
        pickle.dump(modelo, f)
    with open(RUTA_METRICAS, "w", encoding="utf-8") as f:
        json.dump(
            {
                "fecha_entrenamiento": datetime.now().isoformat(timespec="seconds"),
                "modelo": "RandomForestClassifier",
                "n_estimators": N_ESTIMATORS,
                "max_depth": MAX_DEPTH,
                "random_state": SEMILLA,
                "filas_train": len(X_train),
                "filas_test": len(X_test),
                "accuracy": accuracy,
            },
            f,
            indent=2,
        )

    print(f"  Modelo: RandomForest (n_estimators={N_ESTIMATORS}, max_depth={MAX_DEPTH})")
    print(f"  Filas de entrenamiento: {len(X_train)} | Filas de prueba: {len(X_test)}")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Modelo guardado en: models/model.pkl")
    print(f"  Métricas guardadas en: models/metrics.json")


if __name__ == "__main__":
    main()
