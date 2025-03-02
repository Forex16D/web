FROM python:3.12

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libfreetype6-dev \
    libsdl2-dev \
    libsdl2-mixer-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    libpng-dev \
    libjpeg-dev \
    libgl1-mesa-dev \
    swig \
    git \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

EXPOSE 5000 5555 5557

CMD ["python", "-m", "flask", "run", "--debug", "--host=0.0.0.0"]
