FROM python:3.10-slim

WORKDIR /deployments

COPY . .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN pip install -r requirements.txt

CMD ["python", "deployment.py"]
