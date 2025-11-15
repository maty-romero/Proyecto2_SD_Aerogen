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


EXPOSE 5001

# manejar multiples requests sin necesidad de usar ServidorHTTP
CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:5001", "server:app"] 

# ENV FLASK_ENV=development
# CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
