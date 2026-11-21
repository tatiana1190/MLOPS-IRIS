# Actividad – Pipeline MLOps Reproducible con Validación y Contrato de Datos (Iris)

## Objetivo
Automatizar el entrenamiento y la validación del modelo Random Forest construido en la Actividad 1.1 con el conjunto de datos Iris.
Con un solo comando se preparan los datos, se validan contra un contrato de datos, se entrena el modelo
y se ejecutan pruebas automáticas que confirman que el resultado es aceptable.
---

# Requisitos
Antes de iniciar, verificar que se encuentre instalado:
- Python 3.10 o superior (el proyecto se probó con Python 3.13)
- Visual Studio Code
- Extensión de Python para VS Code
---

# 1. Crear la carpeta del proyecto
- Crear una carpeta para el laboratorio con el nombre:
```
MLOPS-IRIS
```
- Dentro de ella crear dos subcarpetas:
```
src
tests
```
- Abrir la carpeta `MLOPS-IRIS` desde Visual Studio Code (*File → Open Folder*).

> Si ya se cuenta con el archivo `MLOPS-IRIS.zip`, basta con descomprimirlo, abrir la carpeta en VS Code y continuar en el paso 3.
---

# 2. Crear los archivos del proyecto
- Crear cada uno de los siguientes archivos en la ubicación indicada y copiar en ellos el código fuente proporcionado:

| Archivo | Ubicación | Para qué sirve |
|---|---|---|
| `run_pipeline.py` | raíz | Orquesta todo el flujo con un solo comando |
| `prepare.py` | `src/` | Carga Iris y genera train.csv y test.csv (80/20, estratificado) |
| `validate_data.py` | `src/` | Revisa los datos contra el contrato |
| `train.py` | `src/` | Entrena el Random Forest y guarda el modelo y sus métricas |
| `test_model.py` | `tests/` | Verifica archivos, modelo y accuracy mínima |
| `data_contract.json` | raíz | Define cómo deben ser los datos |
| `romper_datos.py` | raíz | Daña los datos a propósito para probar los controles |
| `requirements.txt` | raíz | Librerías necesarias |
| `README.md` | raíz | Este instructivo |
| `.gitignore` | raíz | Archivos que no se suben a GitHub |

- El archivo `requirements.txt` debe tener el siguiente contenido:
```text
scikit-learn>=1.5
pytest>=8.0
```
- **scikit-learn:** dataset Iris, división de datos y Random Forest.
- **pytest:** ejecución de las pruebas automáticas.
- La validación de datos no usa ninguna librería externa; solo `csv` y `json` de Python.

- Al terminar, el panel *Explorer* de VS Code debe verse así:
```
MLOPS-IRIS-SANTOTO
│
├── src/
│   ├── prepare.py
│   ├── train.py
│   └── validate_data.py
├── tests/
│   └── test_model.py
├── .gitignore
├── data_contract.json
├── README.md
├── requirements.txt
├── romper_datos.py
└── run_pipeline.py
```
---

# 3. Abrir la terminal
- En VS Code ir al menú *Terminal → New Terminal*.
- Verificar que la terminal sea **PowerShell** y que la ruta termine en `MLOPS-IRIS-SANTOTO`.
- Verificar la versión de Python:
```powershell
py --list
```
---

# 4. Crear el entorno virtual (solo la primera vez)
- Ejecutar:
```powershell
py -3.13 -m venv .venv
```
- Si se tiene otra versión de Python, cambiar `-3.13` por la que aparezca en `py --list` (por ejemplo `py -3.12 -m venv .venv`).
- Se creará una carpeta llamada `.venv`.
---

# 5. Activar el entorno virtual (cada vez que se abra VS Code)
- Ejecutar:
```powershell
.venv\Scripts\activate
```

Si PowerShell bloquea la ejecución de scripts, ejecutar primero:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
Luego volver a activar el entorno:
```powershell
.venv\Scripts\activate
```
Cuando el entorno esté activo deberá aparecer:
```
(.venv)
```
al inicio de la línea de comandos.
---

# 6. Instalar las dependencias (solo la primera vez)
- Con el entorno activo, ejecutar:
```powershell
pip install -r requirements.txt
```
- Al final debe aparecer `Successfully installed ...`.
---

# 7. Ejecutar el pipeline completo
- Desde la terminal ejecutar:
```powershell
python run_pipeline.py
```
- El script ejecuta, en orden, las cuatro etapas:

| Etapa | Archivo | Qué hace |
|---|---|---|
| 1. Preparación de datos | `src/prepare.py` | Crea `data/train.csv` (120 filas) y `data/test.csv` (30 filas) |
| 2. Validación y control de calidad | `src/validate_data.py` | Revisa tipos, nulos, rangos y especie contra el contrato |
| 3. Entrenamiento del modelo | `src/train.py` | Entrena el Random Forest y guarda `models/model.pkl` y `models/metrics.json` |
| 4. Pruebas automatizadas | `tests/test_model.py` | Ejecuta 10 pruebas sobre archivos, modelo y accuracy |

- Si el pipeline fue exitoso aparecerá un resultado similar a:
```
ETAPA 1: Preparación de datos
ETAPA 2: Validación y control de calidad
ETAPA 3: Entrenamiento del modelo · Accuracy: 0.9000
ETAPA 4: Pruebas automatizadas · 10 passed
PIPELINE FINALIZADO CORRECTAMENTE
```
- En la terminal aparecerán más líneas (el detalle de cada etapa y de cada prueba). Lo anterior es el resumen.
- Si alguna etapa falla, el pipeline se detiene y muestra `PIPELINE DETENIDO EN ETAPA X`.
- Tomar captura de pantalla del resultado para el informe.
---

# 8. Revisar los archivos generados
- Después de ejecutar el pipeline aparecerán en el *Explorer* los siguientes elementos nuevos:
```
├── data/
│   ├── train.csv
│   └── test.csv
└── models/
    ├── model.pkl
    └── metrics.json
```
- Abrir `models/metrics.json` y verificar su contenido. Debe verse similar a:
```json
{
  "fecha_entrenamiento": "2026-11-21T10:20:26",
  "modelo": "RandomForestClassifier",
  "n_estimators": 100,
  "max_depth": null,
  "random_state": 42,
  "filas_train": 120,
  "filas_test": 30,
  "accuracy": 0.9
}
```
- El accuracy siempre será 0.9 porque la división de datos y el modelo usan la semilla fija `random_state=42`.
---

# 9. Ejecutar solo las pruebas (opcional)
- Para correr las 10 pruebas sin repetir todo el pipeline:
```powershell
python -m pytest tests -v
```
- Debe aparecer:
```
10 passed
```

Las pruebas que se ejecutan son:

| # | Prueba | Qué verifica |
|---|---|---|
| 1 | `test_existen_archivos_de_datos` | Que existan train.csv y test.csv |
| 2 | `test_existe_modelo_entrenado` | Que exista models/model.pkl |
| 3 | `test_existe_contrato_de_datos` | Que el contrato tenga columnas y ejemplos |
| 4 | `test_modelo_tiene_metodo_predict` | Que el modelo cargado se pueda usar para predecir |
| 5 | `test_modelo_predice_ejemplo_valido` | Que prediga una especie válida para el ejemplo del contrato |
| 6 | `test_modelo_conoce_las_tres_especies` | Que el modelo haya aprendido las clases 0, 1 y 2 |
| 7 | `test_accuracy_minima` | Que el accuracy sea mayor o igual a 0.80 |
| 8 | `test_metricas_registradas` | Que metrics.json tenga fecha, parámetros y accuracy |
| 9 | `test_contrato_acepta_entrada_valida` | Que el ejemplo válido no genere errores |
| 10 | `test_contrato_rechaza_entrada_invalida` | Que el ejemplo inválido genere los 4 errores esperados |
---

# 10. Revisar la validación de datos
- Abrir el archivo `src/validate_data.py`.
- La validación usa solo la librería estándar de Python y revisa cada fila de `train.csv` y `test.csv`:

| Control | Qué revisa | Mensaje de error |
|---|---|---|
| Tipo de dato | Las 4 medidas deben ser `float` y la especie `int` | `no es de tipo float` |
| Nulos | No se aceptan celdas vacías ni `NA`, `NaN`, `null`, `None` | `no puede ser nulo` |
| Rango | Cada medida entre su mínimo y máximo en centímetros | `supera el máximo` / `está por debajo del mínimo` |
| Dominio | La especie solo puede ser 0, 1 o 2 | `fuera del dominio [0, 1, 2]` |
| Estructura | Que estén todas las columnas y que el archivo tenga filas | `Encabezado incompleto` |

- Para ejecutar solo la validación:
```powershell
python src/validate_data.py
```
- Debe aparecer:
```
[OK] train.csv: 120 filas cumplen el contrato
[OK] test.csv: 30 filas cumplen el contrato
Validación superada: tipos, nulos, rangos y dominio correctos.
```
---

# 11. Revisar el contrato de datos
- Abrir el archivo `data_contract.json`.
- El contrato define las reglas que deben cumplir los datos para el entrenamiento y para la futura inferencia (medidas en centímetros):

| Columna | Tipo | Nulos | Mínimo | Máximo |
|---|---|---|---|---|
| sepal_length | float | No | 4.0 | 8.0 |
| sepal_width | float | No | 2.0 | 4.5 |
| petal_length | float | No | 1.0 | 7.0 |
| petal_width | float | No | 0.1 | 2.5 |
| species | int | No | Solo 0, 1 o 2 | — |

- Ejemplo de **entrada válida** incluido en el contrato:
```json
{ "sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2 }
```
- Ejemplo de **entrada inválida** incluido en el contrato:
```json
{ "sepal_length": "cinco", "sepal_width": null, "petal_length": 65.0, "petal_width": -0.3 }
```

| Campo | Regla que incumple |
|---|---|
| sepal_length = "cinco" | No es de tipo float |
| sepal_width = null | No puede ser nulo |
| petal_length = 65.0 | Supera el máximo (7.0) |
| petal_width = -0.3 | Está por debajo del mínimo (0.1) |

- Para comprobar el contrato desde la terminal, ejecutar:
```powershell
python -c "import sys; sys.path.insert(0,'src'); from validate_data import cargar_contrato, validar_registro; c=cargar_contrato(); print('Valida:', validar_registro(c['ejemplo_entrada_valida'], c)); print('Invalida:', validar_registro(c['ejemplo_entrada_invalida'], c))"
```
- Debe aparecer `Valida: []` (sin errores) y `Invalida:` con 4 errores.
---

# 12. Probar los controles con datos saboteados
- Ver la lista de sabotajes:
```powershell
python romper_datos.py
```
- Ejecutar los 7 sabotajes, **uno por uno**:
```powershell
python romper_datos.py 1
python romper_datos.py 2
python romper_datos.py 3
python romper_datos.py 4
python romper_datos.py 5
python romper_datos.py 6
python romper_datos.py 7
```
- Cada comando parte de datos limpios, daña el archivo `data/train.csv` y corre el pipeline. Al final de cada uno aparece una línea `RESULTADO:` que indica si fue detenido o no.
- Tomar captura de pantalla de cada resultado.

Resultado esperado de cada sabotaje:

| Sabotaje | Lo detuvo | Evidencia en la terminal |
|---|---|---|
| 1. «cinco» en lugar de un número | A · Validación | No es de tipo float |
| 2. Celda vacía en petal_width | A · Validación | No puede ser nulo |
| 3. Registro en milímetros | A · Validación | Supera el máximo (4 errores) |
| 4. Especie con código 3 | A · Validación | Fuera del dominio [0, 1, 2] |
| 5. Sin flores virginica | C · Pruebas | Accuracy 0,67 < 0,80 |
| 6. 40 % de etiquetas erradas | C · Pruebas | Accuracy 0,53 < 0,80 |
| 7. Prueba copiada en entrenamiento | D · Nadie | Accuracy 1,00 y 10 pruebas OK |

**Interpretación:** los sabotajes 1 a 4 dañan la *forma* de los datos y la validación los detiene antes de entrenar. Los sabotajes 5 y 6 dejan datos con formato correcto pero producen un modelo malo, y los detecta la prueba de accuracy mínima. El sabotaje 7 es una fuga de datos: el modelo ve las respuestas de la prueba durante el entrenamiento, obtiene 1,00 y pasa todos los controles. Un resultado perfecto no garantiza un buen modelo.
---

# 13. Restaurar los datos limpios
- Al terminar los sabotajes, ejecutar:
```powershell
python romper_datos.py restaurar
```
- Debe aparecer nuevamente:
```
Accuracy: 0.9000
10 passed
PIPELINE FINALIZADO CORRECTAMENTE
```
---

