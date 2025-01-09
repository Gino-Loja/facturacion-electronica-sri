# Usar Alpine como base
FROM python:3.11-alpine

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk
ENV PATH="$JAVA_HOME/bin:$PATH"

# Instalar dependencias del sistema
RUN apk add --no-cache \
    bash \
    openjdk8 \
    build-base \
    libffi-dev \
    postgresql-dev \
    musl-dev \
    && pip install --no-cache-dir --upgrade pip setuptools

# Crear un directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias y el código fuente
COPY requirements.txt /app/
COPY . /app

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto (por defecto, FastAPI usa 8000)
EXPOSE 8096

# Comando para iniciar la aplicación con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8096", "--reload"]
