# Valoración de síntomas

Estimación de una posible enfermedad a partir de síntomas, para enfermedades comunes y huérfanas.

## 1. Pipeline

- [pipeline_mlops.md](pipeline_mlops.md): problema, diseño, etapas y criterios para avanzar.
- [diagrama-pipeline.svg](diagrama-pipeline.svg): diagrama general. Ábralo en el navegador si el visor de Markdown no muestra la imagen.

## 2. Servicio para el médico

La carpeta [servicio](servicio/) contiene la función que ocupa el lugar del modelo, el `Dockerfile` y las instrucciones.

Para construir la imagen, ejecutarla y obtener los cuatro estados, siga [servicio/README.md](servicio/README.md).
