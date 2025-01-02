FROM python:3.12-slim

COPY . /app

WORKDIR /app

ENV DATA_FOLDER=/app/data
RUN mkdir -p $DATA_FOLDER

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "main:app"]