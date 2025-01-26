FROM python:3.14.0a3-alpine3.21

RUN apk update && apk add \
    build-base \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--debug", "--host=0.0.0.0"]