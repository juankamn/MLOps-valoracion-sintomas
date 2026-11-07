# Taller MLOps: valoración de síntomas

**Universidad Icesi — Machine Learning Operations (MLOps)**

**Semanas 1 y 2: pipeline de MLOps e imagen de Docker**

## Integrantes

- Jairo Andrés Valencia — A00429914
- Juan Camilo Macias Navarrete — A00427476

## Descripción

El taller propone un pipeline para estimar la posibilidad de enfermedad a partir de síntomas, considerando tanto enfermedades comunes como huérfanas. También incluye un servicio ejecutable en Docker para que un médico ingrese datos y consulte un estado.

El servicio usa una **función simulada**, no un modelo entrenado. Sus resultados son ilustrativos y no constituyen un diagnóstico médico.

## Contenido de la entrega

1. **Pipeline de MLOps:** [descripción de las etapas](pipeline_mlops.md) y [diagrama general](diagrama-pipeline.svg), desde la ingesta y validación de datos hasta el despliegue, monitoreo y reentrenamiento.
2. **Servicio en Docker:** la carpeta [servicio](servicio/) contiene el código de la función, la página web, la API, el Dockerfile y las pruebas. Las instrucciones completas están en [servicio/README.md](servicio/README.md).

## Ejecución rápida

Con Docker y su motor en ejecución, desde la raíz del repositorio:

```sh
docker build -t valoracion-sintomas:0.1 ./servicio
docker run --rm -p 8080:5000 valoracion-sintomas:0.1
```

Abra [http://localhost:8080](http://localhost:8080), ingrese los cuatro datos y pulse **Obtener estado**. El formulario incluye ejemplos para probar los cuatro resultados. Para consultar la API o cambiar el puerto, consulte el [README del servicio](servicio/README.md).
