# Ejemplo minimo app flask 

FROM python:3.8-slim-buster

WORKDIR /AuthNode

COPY AuthNode/requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copia codigo fuente
COPY AuthNode/ ./         
COPY Shared/ /Shared/

ENV PYTHONPATH="/:/AuthNode:${PYTHONPATH}"
ENV FLASK_APP=server
ENV FLASK_ENV=development

EXPOSE 5001

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
