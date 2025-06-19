# Simulador Minero - Decisión Operacional

Esta app desarrollada en Taipy permite:
- Evaluar escenarios operacionales ante la detención de una pala de carguío.
- Calcular el Beneficio Económico Neto (BEN) por escenario.
- Visualizar una matriz de pagos entre Producción y Mantención.
- Determinar el equilibrio más favorable basado en teoría de juegos.

## Requisitos

- Python 3.8+
- Librería Taipy

## Instalación

```bash
pip install -r requirements.txt
python app.py
```

## Despliegue en Render

1. Sube este repositorio a GitHub.
2. Crea un nuevo servicio en [Render.com](https://render.com) seleccionando "Web Service".
3. Usa el repo GitHub y el comando de inicio:

```bash
python app.py
```

4. Establece el runtime como Python 3.x.

¡Listo! Se desplegará como una app web.

