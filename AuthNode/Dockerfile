# Ejemplo minimo app flask 

FROM python:3.8-slim-buster

WORKDIR /app

COPY AuthNode/requirements.txt ./AuthNode/requirements.txt
RUN pip3 install --no-cache-dir -r ./AuthNode/requirements.txt

# Copia codigo fuente
COPY AuthNode/ ./AuthNode/
COPY Shared/ ./Shared/

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV FLASK_APP=AuthNode.server
ENV FLASK_ENV=development

EXPOSE 5001

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
