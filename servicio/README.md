# Valoración de síntomas

Servicio para que un médico consulte, a partir de cuatro datos del episodio, uno de estos estados:

- `NO ENFERMO`
- `ENFERMEDAD LEVE`
- `ENFERMEDAD AGUDA`
- `ENFERMEDAD CRÓNICA`

## Finalidad

El problema de fondo es estimar si un paciente puede tener una enfermedad a partir de sus síntomas, tanto cuando hay muchos casos (enfermedades comunes) como cuando hay muy pocos (enfermedades huérfanas). El pipeline de esa solución está en `../pipeline_mlops.md`.

Todavía no hay un modelo entrenado. Una función ocupa ese lugar para poder desplegar el servicio. El médico introduce fiebre, intensidad del dolor, días con síntomas y número de síntomas. El servicio responde con un estado y con la regla que se activó. No diagnostica y no reemplaza el criterio del médico.

La función está en `predictor.py` y se llama `predict_state`. Acepta los cuatro valores como argumentos separados (número o texto numérico). La página y el API los reciben como formulario o como JSON.

## Cómo decide la función

Se aplican estas reglas, en este orden:

1. Si los días con síntomas son **90 o más**, el estado es `ENFERMEDAD CRÓNICA`.
2. Si la fiebre es **38.5 °C o más**, el dolor es **7 o más**, o el número de síntomas es **5 o más**, el estado es `ENFERMEDAD AGUDA`.
3. Si la fiebre es **menor de 37.5 °C**, el dolor es **2 o menos**, los síntomas son **1 o menos** y los días son **3 o menos**, el estado es `NO ENFERMO`.
4. En cualquier otro valor dentro del rango, el estado es `ENFERMEDAD LEVE`.

Rangos aceptados: fiebre de 34 a 43 °C, dolor de 0 a 10, días de 0 a 3650 y síntomas de 0 a 30. Fuera de ese rango el servicio responde un error y no inventa un estado. En la fiebre se puede usar coma o punto (`37,6` o `37.6`).

Estos cuatro casos cubren los cuatro estados:

| Fiebre | Dolor | Días | Síntomas | Estado |
| --- | --- | --- | --- | --- |
| 36.6 | 1 | 1 | 0 | NO ENFERMO |
| 37.6 | 4 | 4 | 2 | ENFERMEDAD LEVE |
| 39.2 | 8 | 2 | 6 | ENFERMEDAD AGUDA |
| 37.0 | 3 | 120 | 2 | ENFERMEDAD CRÓNICA |

## Archivos

| Archivo | Para qué |
| --- | --- |
| `predictor.py` | Función que simula el modelo |
| `app.py` | Página web y API |
| `templates/index.html` | Formulario del médico |
| `static/estilos.css` y `static/formulario.js` | Presentación y casos de prueba |
| `requirements.txt` | Dependencia (Flask) |
| `Dockerfile` | Construcción de la imagen |

## Requisitos

- Docker con un motor de contenedores en ejecución, por ejemplo Docker Desktop o Colima.
- Si usa Colima, inícielo con `colima start`.
- La primera construcción descarga la imagen base de Python y necesita internet.

Los comandos de construcción y ejecución funcionan con Docker en Windows, macOS y Linux. El proyecto usa una imagen pública y no requiere una cuenta ni un gestor de credenciales específico para construirla.

Abra una terminal en esta carpeta (`servicio`), que es donde está el `Dockerfile`.

## Construir la imagen

```powershell
docker build -t valoracion-sintomas:0.1 .
```

El punto final indica que el contexto es la carpeta actual. Si Docker responde que no encuentra el `Dockerfile`, no está ubicado en `servicio`.

## Ejecutar el servicio

```powershell
docker run --rm -p 8080:5000 valoracion-sintomas:0.1
```

Deje esa terminal abierta. El servicio queda en `http://localhost:8080`.

- `8080` de la izquierda es el puerto de su equipo.
- `5000` de la derecha es el puerto dentro del contenedor.

En macOS, AirPlay puede ocupar el puerto 5000; por eso se usa 8080 en el equipo. Si 8080 también está ocupado, elija otro puerto, por ejemplo 8081:

```powershell
docker run --rm -p 8081:5000 valoracion-sintomas:0.1
```

En ese caso abra `http://localhost:8081` y use 8081 en los enlaces de abajo.

Para ejecutar en segundo plano:

```powershell
docker run -d --name valoracion-sintomas -p 8080:5000 valoracion-sintomas:0.1
```

## Obtener una predicción

### Página web

1. Abra `http://localhost:8080`.
2. Escriba los cuatro datos y pulse **Obtener estado**.
3. O pulse uno de los botones **Probar**. Cada botón corresponde a un estado de la tabla.

### Enlaces directos

Estos ejemplos usan `curl` en macOS o Linux. En Windows PowerShell use `curl.exe` en lugar de `curl`. Mantenga la dirección entre comillas.

NO ENFERMO:

```powershell
curl -s "http://localhost:8080/api/predecir?fiebre=36.6&intensidad_dolor=1&dias_sintomas=1&numero_sintomas=0"
```

ENFERMEDAD LEVE:

```powershell
curl -s "http://localhost:8080/api/predecir?fiebre=37.6&intensidad_dolor=4&dias_sintomas=4&numero_sintomas=2"
```

ENFERMEDAD AGUDA:

```powershell
curl -s "http://localhost:8080/api/predecir?fiebre=39.2&intensidad_dolor=8&dias_sintomas=2&numero_sintomas=6"
```

ENFERMEDAD CRÓNICA:

```powershell
curl -s "http://localhost:8080/api/predecir?fiebre=37.0&intensidad_dolor=3&dias_sintomas=120&numero_sintomas=2"
```

La respuesta trae `estado`, `regla`, `version` y `entrada`. Ejemplo:

```json
{
  "estado": "NO ENFERMO",
  "regla": "Fiebre, dolor, duración y número de síntomas están por debajo del umbral de enfermedad.",
  "version": "0.1.0",
  "entrada": {
    "fiebre": 36.6,
    "intensidad_dolor": 1,
    "dias_sintomas": 1,
    "numero_sintomas": 0
  }
}
```

### API con POST

En Windows PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/predecir -ContentType "application/json; charset=utf-8" -Body '{"fiebre":39.2,"intensidad_dolor":8,"dias_sintomas":2,"numero_sintomas":6}'
```

En macOS o Linux:

```sh
curl -X POST http://localhost:8080/api/predecir \
  -H 'Content-Type: application/json' \
  -d '{"fiebre":39.2,"intensidad_dolor":8,"dias_sintomas":2,"numero_sintomas":6}'
```

El estado de esa llamada es `ENFERMEDAD AGUDA`. Cambie los cuatro números según la tabla para obtener los otros estados.

Un dato fuera de rango responde con código 400 y un mensaje en `error`. Por ejemplo, una fiebre de 30.

### Comprobar la función dentro de la imagen

Sin abrir el navegador, la imagen puede imprimir los cuatro estados, en el orden de la tabla:

```powershell
docker run --rm --entrypoint python valoracion-sintomas:0.1 predictor.py
```

Salida esperada:

```text
NO ENFERMO
ENFERMEDAD LEVE
ENFERMEDAD AGUDA
ENFERMEDAD CRÓNICA
```

## Detener el servicio

Si lo inició en primer plano, pulse `Ctrl+C`.

Si lo inició en segundo plano:

```powershell
docker stop valoracion-sintomas
docker rm valoracion-sintomas
```

## Problemas frecuentes

| Qué ocurre | Qué hacer |
| --- | --- |
| No se encuentra el Dockerfile | Entre a la carpeta `servicio` y vuelva a construir. |
| El puerto ya está asignado | Use `-p 8081:5000` y abra el puerto 8081. En macOS, AirPlay puede responder en el puerto 5000. |
| La primera construcción falla por red | Confirme la conexión a internet y que el motor de Docker esté en ejecución. |
| La página no abre | Revise que el contenedor siga corriendo y que el puerto de la dirección coincida con el de la izquierda en `docker run`. |
