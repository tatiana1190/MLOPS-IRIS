"""
ETAPA 2 - Validación y control de calidad de los datos.

Revisa cada registro contra data_contract.json usando solo la librería estándar
de Python (csv y json), sin pandas ni librerías de validación externas.

Verifica:
  - Tipos de datos correctos (float en las medidas, int en la especie).
  - Ausencia de valores nulos o celdas vacías.
  - Rangos lógicos (mínimo y máximo de cada medida en centímetros).
  - Dominio de la especie (solo 0, 1 o 2).

Se puede usar de dos formas:
  - python src/validate_data.py         -> valida data/train.csv y data/test.csv
  - validar_registro(dict, contrato)     -> valida una entrada para inferencia
"""
import csv
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_CONTRATO = os.path.join(RAIZ, "data_contract.json")
ARCHIVOS = [os.path.join(RAIZ, "data", "train.csv"), os.path.join(RAIZ, "data", "test.csv")]

VALORES_NULOS = {"", "na", "nan", "null", "none"}


def cargar_contrato(ruta=RUTA_CONTRATO):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def es_nulo(valor):
    if valor is None:
        return True
    return isinstance(valor, str) and valor.strip().lower() in VALORES_NULOS


def convertir_float(valor):
    """Devuelve el valor como float o None si no es numérico.
    Los booleanos se rechazan a propósito (True no es una medida)."""
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        return float(str(valor).strip())
    except ValueError:
        return None


def convertir_int(valor):
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor
    texto = str(valor).strip()
    if texto.lstrip("-").isdigit():
        return int(texto)
    return None


def validar_registro(registro, contrato, incluir_objetivo=False):
    """Valida un registro (diccionario) y devuelve la lista de errores encontrados.
    Lista vacía = registro válido."""
    errores = []

    for nombre, regla in contrato["columnas"].items():
        if nombre not in registro:
            errores.append(f"{nombre}: columna faltante")
            continue

        valor = registro[nombre]
        if es_nulo(valor):
            if not regla["nulo_permitido"]:
                errores.append(f"{nombre}: no puede ser nulo")
            continue

        numero = convertir_float(valor)
        if numero is None:
            errores.append(f"{nombre}: no es de tipo float (valor recibido: {valor!r})")
            continue

        if numero < regla["min"]:
            errores.append(f"{nombre}: {numero} está por debajo del mínimo ({regla['min']})")
        elif numero > regla["max"]:
            errores.append(f"{nombre}: {numero} supera el máximo ({regla['max']})")

    if incluir_objetivo:
        objetivo = contrato["objetivo"]
        nombre = objetivo["nombre"]
        valor = registro.get(nombre)
        if es_nulo(valor):
            errores.append(f"{nombre}: no puede ser nulo")
        else:
            codigo = convertir_int(valor)
            if codigo is None:
                errores.append(f"{nombre}: no es de tipo int (valor recibido: {valor!r})")
            elif codigo not in objetivo["dominio"]:
                errores.append(f"{nombre}: valor {codigo} fuera del dominio {objetivo['dominio']}")

    return errores


def validar_archivo(ruta, contrato):
    """Valida un CSV completo. Devuelve (cantidad_de_filas, lista_de_errores)."""
    errores = []
    esperadas = list(contrato["columnas"].keys()) + [contrato["objetivo"]["nombre"]]

    with open(ruta, newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        encabezado = lector.fieldnames or []
        faltantes = [c for c in esperadas if c not in encabezado]
        if faltantes:
            return 0, [f"Encabezado incompleto, faltan columnas: {faltantes}"]

        filas = 0
        for numero_fila, registro in enumerate(lector, start=2):  # fila 1 = encabezado
            filas += 1
            for error in validar_registro(registro, contrato, incluir_objetivo=True):
                errores.append(f"fila {numero_fila} -> {error}")

    if filas == 0:
        errores.append("El archivo no tiene registros")
    return filas, errores


def main():
    contrato = cargar_contrato()
    print(f"  Contrato: {contrato['nombre']} (v{contrato['version']})")

    total_errores = 0
    for ruta in ARCHIVOS:
        nombre = os.path.basename(ruta)
        if not os.path.exists(ruta):
            print(f"  [ERROR] No existe {nombre}. Ejecute primero la etapa de preparación.")
            total_errores += 1
            continue

        filas, errores = validar_archivo(ruta, contrato)
        if errores:
            print(f"  [ERROR] {nombre}: {len(errores)} errores en {filas} filas")
            for e in errores:
                print(f"     - {e}")
        else:
            print(f"  [OK] {nombre}: {filas} filas cumplen el contrato")
        total_errores += len(errores)

    if total_errores:
        print(f"  Validación fallida: {total_errores} errores. El pipeline se detiene.")
        sys.exit(1)
    print("  Validación superada: tipos, nulos, rangos y dominio correctos.")


if __name__ == "__main__":
    main()
