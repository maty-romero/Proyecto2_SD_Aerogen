# Ejemplo minimo app flask 

FROM python:3.8-slim-buster

WORKDIR /StatNode

# Instalar dependencias del sistema si hace falta
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential \
#    && rm -rf /var/lib/apt/lists/*

# Copiar solo requirements primero (para usar cache)
COPY StatNode/requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY StatNode/ ./          
COPY Shared/ /Shared/      

# Configuración de entorno
ENV PYTHONPATH="/:/StatNode:${PYTHONPATH}"
ENV FLASK_APP=API.server
ENV FLASK_ENV=development

EXPOSE 5000

# Ejecutar Flask y main.py juntos
CMD ["bash", "-c", "python -m flask run --host=0.0.0.0 --port=5000 & python /StatNode/main.py"]

