"""
Laboratorio de sabotaje: daña los datos a propósito para comprobar qué
control del pipeline detecta cada problema.

Uso:
    python romper_datos.py            -> muestra la lista de sabotajes
    python romper_datos.py 3          -> aplica el sabotaje 3 y ejecuta el pipeline
    python romper_datos.py restaurar  -> regenera los datos limpios y corre el pipeline normal

Cada sabotaje parte de datos limpios (vuelve a ejecutar src/prepare.py), daña
data/train.csv y luego corre "run_pipeline.py --sin-preparar" para que el daño
no se sobrescriba.

| # | Sabotaje                            | Quién lo detiene   |
|---|-------------------------------------|--------------------|
| 1 | "cinco" en lugar de un número       | A - Validación     |
| 2 | Celda vacía en petal_width          | A - Validación     |
| 3 | Registro en milímetros              | A - Validación     |
| 4 | Especie con código 3                | A - Validación     |
| 5 | Sin flores virginica                | C - Pruebas        |
| 6 | 40 % de etiquetas erradas           | C - Pruebas        |
| 7 | Prueba copiada en entrenamiento     | D - Nadie          |
"""
import csv
import os
import random
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
RUTA_TRAIN = os.path.join(RAIZ, "data", "train.csv")
RUTA_TEST = os.path.join(RAIZ, "data", "test.csv")
PYTHON = sys.executable


# --- utilidades de lectura y escritura --------------------------------------

def leer(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        return lector.fieldnames, list(lector)


def escribir(ruta, columnas, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


# --- sabotajes ---------------------------------------------------------------

def sabotaje_1(columnas, filas):
    """Escribe la palabra 'cinco' donde debería ir un número."""
    filas[0]["sepal_length"] = "cinco"
    return "Fila 2 de train.csv: sepal_length = 'cinco'"


def sabotaje_2(columnas, filas):
    """Deja vacía una celda de petal_width."""
    filas[4]["petal_width"] = ""
    return "Fila 6 de train.csv: petal_width vacío"


def sabotaje_3(columnas, filas):
    """Un registro llega en milímetros (las cuatro medidas multiplicadas por 10)."""
    for i, fila in enumerate(filas):
        if float(fila["petal_width"]) >= 0.3:  # así las 4 medidas superan el máximo
            for c in ["sepal_length", "sepal_width", "petal_length", "petal_width"]:
                fila[c] = str(round(float(fila[c]) * 10, 1))
            return f"Fila {i + 2} de train.csv: medidas en milímetros"
    return "No se encontró fila candidata"


def sabotaje_4(columnas, filas):
    """Aparece una especie que no existe (código 3)."""
    filas[9]["species"] = "3"
    return "Fila 11 de train.csv: species = 3"


def sabotaje_5(columnas, filas):
    """Se eliminan todas las virginica del entrenamiento."""
    antes = len(filas)
    filas[:] = [f for f in filas if f["species"] != "2"]
    return f"Se eliminaron {antes - len(filas)} flores virginica de train.csv"


def sabotaje_6(columnas, filas):
    """El 40 % de las etiquetas de entrenamiento se cambian por otra especie."""
    azar = random.Random(32)  # semilla fija: el daño es reproducible
    indices = azar.sample(range(len(filas)), k=int(len(filas) * 0.40))
    for i in indices:
        actual = filas[i]["species"]
        filas[i]["species"] = azar.choice([e for e in ["0", "1", "2"] if e != actual])
    return f"Se cambiaron {len(indices)} de {len(filas)} etiquetas en train.csv"


def sabotaje_7(columnas, filas):
    """Fuga de datos: las filas de prueba se copian dentro del entrenamiento."""
    _, filas_test = leer(RUTA_TEST)
    filas.extend(filas_test)
    return f"Se copiaron las {len(filas_test)} filas de test.csv dentro de train.csv"


SABOTAJES = {
    1: ("«cinco» en lugar de un número", sabotaje_1, "A · Validación"),
    2: ("Celda vacía en petal_width", sabotaje_2, "A · Validación"),
    3: ("Registro en milímetros", sabotaje_3, "A · Validación"),
    4: ("Especie con código 3", sabotaje_4, "A · Validación"),
    5: ("Sin flores virginica", sabotaje_5, "C · Pruebas"),
    6: ("40 % de etiquetas erradas", sabotaje_6, "C · Pruebas"),
    7: ("Prueba copiada en entrenamiento", sabotaje_7, "D · Nadie"),
}


def mostrar_menu():
    print("Sabotajes disponibles:\n")
    for n, (nombre, _, quien) in SABOTAJES.items():
        print(f"  {n}. {nombre:<36} -> lo detiene: {quien}")
    print("\nUso: python romper_datos.py <número>   |   python romper_datos.py restaurar")


def main():
    if len(sys.argv) < 2:
        mostrar_menu()
        return

    opcion = sys.argv[1].strip().lower()

    if opcion == "restaurar":
        print("Restaurando datos limpios y ejecutando el pipeline completo...")
        sys.exit(subprocess.run([PYTHON, "run_pipeline.py"], cwd=RAIZ).returncode)

    if not opcion.isdigit() or int(opcion) not in SABOTAJES:
        mostrar_menu()
        sys.exit(1)

    numero = int(opcion)
    nombre, funcion, quien = SABOTAJES[numero]

    # 1. Partir siempre de datos limpios
    subprocess.run([PYTHON, os.path.join("src", "prepare.py")], cwd=RAIZ,
                   check=True, stdout=subprocess.DEVNULL)

    # 2. Aplicar el daño
    columnas, filas = leer(RUTA_TRAIN)
    detalle = funcion(columnas, filas)
    escribir(RUTA_TRAIN, columnas, filas)

    print("#" * 64)
    print(f"SABOTAJE {numero}: {nombre}")
    print(f"Detalle: {detalle}")
    print(f"Control que debería detenerlo: {quien}")
    print("#" * 64)

    # 3. Ejecutar el pipeline sin regenerar los datos
    codigo = subprocess.run([PYTHON, "run_pipeline.py", "--sin-preparar"], cwd=RAIZ).returncode

    print("\n" + "#" * 64)
    if codigo != 0:
        print(f"RESULTADO: el pipeline detuvo el sabotaje {numero}.")
    else:
        print(f"RESULTADO: el sabotaje {numero} pasó todos los controles sin ser detectado.")
        print("Una fuga de datos infla el accuracy y las pruebas no la ven.")
    print("Para volver a la normalidad: python romper_datos.py restaurar")
    print("#" * 64)


if __name__ == "__main__":
    main()
