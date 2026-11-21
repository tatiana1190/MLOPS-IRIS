"""
ETAPA 4 - Pruebas automatizadas.

Verifican que los archivos existan, que el modelo se pueda cargar y predecir,
que el accuracy supere el mínimo exigido y que el contrato de datos funcione.
Se ejecutan con:  python -m pytest tests -v
"""
import json
import os
import pickle
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from validate_data import cargar_contrato, validar_registro  # noqa: E402

RUTA_TRAIN = os.path.join(RAIZ, "data", "train.csv")
RUTA_TEST = os.path.join(RAIZ, "data", "test.csv")
RUTA_MODELO = os.path.join(RAIZ, "models", "model.pkl")
RUTA_METRICAS = os.path.join(RAIZ, "models", "metrics.json")
RUTA_CONTRATO = os.path.join(RAIZ, "data_contract.json")

ACCURACY_MINIMA = 0.80


@pytest.fixture(scope="module")
def contrato():
    return cargar_contrato(RUTA_CONTRATO)


@pytest.fixture(scope="module")
def modelo():
    with open(RUTA_MODELO, "rb") as f:
        return pickle.load(f)


@pytest.fixture(scope="module")
def metricas():
    with open(RUTA_METRICAS, encoding="utf-8") as f:
        return json.load(f)


# --- Archivos ---------------------------------------------------------------

def test_existen_archivos_de_datos():
    assert os.path.exists(RUTA_TRAIN), "Falta data/train.csv"
    assert os.path.exists(RUTA_TEST), "Falta data/test.csv"


def test_existe_modelo_entrenado():
    assert os.path.exists(RUTA_MODELO), "Falta models/model.pkl"


def test_existe_contrato_de_datos(contrato):
    assert "columnas" in contrato
    assert "ejemplo_entrada_valida" in contrato
    assert "ejemplo_entrada_invalida" in contrato


# --- Modelo -----------------------------------------------------------------

def test_modelo_tiene_metodo_predict(modelo):
    assert hasattr(modelo, "predict")


def test_modelo_predice_ejemplo_valido(modelo, contrato):
    ejemplo = contrato["ejemplo_entrada_valida"]
    columnas = list(contrato["columnas"].keys())
    prediccion = modelo.predict([[ejemplo[c] for c in columnas]])
    assert int(prediccion[0]) in contrato["objetivo"]["dominio"]


def test_modelo_conoce_las_tres_especies(modelo):
    assert sorted(int(c) for c in modelo.classes_) == [0, 1, 2]


# --- Métricas ---------------------------------------------------------------

def test_accuracy_minima(metricas):
    accuracy = metricas["accuracy"]
    assert accuracy >= ACCURACY_MINIMA, (
        f"Accuracy {accuracy:.2f} < {ACCURACY_MINIMA:.2f}: el modelo no cumple el mínimo"
    )


def test_metricas_registradas(metricas):
    for clave in ["fecha_entrenamiento", "n_estimators", "filas_train", "filas_test", "accuracy"]:
        assert clave in metricas, f"Falta '{clave}' en models/metrics.json"


# --- Contrato de datos ------------------------------------------------------

def test_contrato_acepta_entrada_valida(contrato):
    assert validar_registro(contrato["ejemplo_entrada_valida"], contrato) == []


def test_contrato_rechaza_entrada_invalida(contrato):
    errores = validar_registro(contrato["ejemplo_entrada_invalida"], contrato)
    assert len(errores) == len(contrato["errores_esperados_entrada_invalida"])
