# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias del sistema necesarias para pyodbc
RUN apt-get update \
    && apt-get install -y \
        unixodbc \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requisitos y el código de la aplicación al contenedor
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
