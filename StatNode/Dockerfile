FROM python:3.8-slim-buster

# Establecemos el directorio de trabajo principal
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY StatNode/requirements.txt ./StatNode/requirements.txt
RUN pip3 install --no-cache-dir -r ./StatNode/requirements.txt

# Copiar el código fuente creando la estructura de paquetes correcta
COPY StatNode/ ./StatNode/
COPY Shared/ ./Shared/

# Corregir fin de línea de entrypoint
RUN sed -i 's/\r$//' /app/StatNode/entrypoint/entrypoint.sh

# Variables de entorno
# Añadimos /app al PYTHONPATH para que encuentre los módulos StatNode y Shared
ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV FLASK_APP=StatNode.API.server
ENV FLASK_ENV=development

EXPOSE 5000

# ENTRYPOINT → usando /bin/sh porque slim NO trae bash
ENTRYPOINT ["/bin/sh", "/app/StatNode/entrypoint/entrypoint.sh"]
