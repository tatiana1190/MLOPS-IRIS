"""
Orquestador del pipeline MLOps - Iris.

Ejecuta las cuatro etapas en orden con un solo comando:

    python run_pipeline.py

  ETAPA 1: Preparación de datos         (src/prepare.py)
  ETAPA 2: Validación y control de calidad (src/validate_data.py)
  ETAPA 3: Entrenamiento del modelo         (src/train.py)
  ETAPA 4: Pruebas automatizadas         (tests/test_model.py)

Si una etapa falla, el pipeline se detiene y no continúa con las siguientes.

Opción:
    python run_pipeline.py --sin-preparar
        Omite la etapa 1 y trabaja con los CSV que ya están en data/.
        La usa romper_datos.py para que los datos saboteados no se sobrescriban.
"""
import argparse
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

ETAPAS = [
    ("ETAPA 1", "Preparación de datos", [PYTHON, os.path.join("src", "prepare.py")]),
    ("ETAPA 2", "Validación y control de calidad", [PYTHON, os.path.join("src", "validate_data.py")]),
    ("ETAPA 3", "Entrenamiento del modelo", [PYTHON, os.path.join("src", "train.py")]),
    ("ETAPA 4", "Pruebas automatizadas", [PYTHON, "-m", "pytest", "tests", "-v", "-p", "no:cacheprovider"]),
]

LINEA = "=" * 64


def ejecutar_etapa(codigo, nombre, comando):
    print(f"\n{LINEA}\n{codigo}: {nombre}\n{LINEA}")
    inicio = time.time()
    resultado = subprocess.run(comando, cwd=RAIZ)
    duracion = time.time() - inicio
    if resultado.returncode != 0:
        print(f"\n[X] {codigo} falló (código {resultado.returncode}) tras {duracion:.1f} s.")
        return False
    print(f"[OK] {codigo} completada en {duracion:.1f} s.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Pipeline MLOps del dataset Iris")
    parser.add_argument(
        "--sin-preparar",
        action="store_true",
        help="Omite la etapa 1 y usa los CSV existentes en data/",
    )
    args = parser.parse_args()

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    print(f"{LINEA}\nPIPELINE MLOPS - IRIS (Universidad Santo Tomás)\n{LINEA}")

    etapas = ETAPAS[1:] if args.sin_preparar else ETAPAS
    if args.sin_preparar:
        print("Etapa 1 omitida: se usan los datos actuales de data/.")

    for codigo, nombre, comando in etapas:
        if not ejecutar_etapa(codigo, nombre, comando):
            print(f"\n{LINEA}\nPIPELINE DETENIDO EN {codigo}\n{LINEA}")
            sys.exit(1)

    print(f"\n{LINEA}\nPIPELINE FINALIZADO CORRECTAMENTE\n{LINEA}")


if __name__ == "__main__":
    main()
