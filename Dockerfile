FROM python:3.10-slim

WORKDIR .

COPY . .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN pip install -r requirements.txt

#CMD ["python", "-m", "src.main_script", "2024", "9", "17", "ignore_gnosis_transfers"]
CMD ["python", "deployment.py"]
