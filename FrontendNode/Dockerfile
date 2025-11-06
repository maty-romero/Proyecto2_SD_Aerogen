# --- Contenido para FrontendNode/Dockerfile ---
FROM node:18-alpine

WORKDIR /app

# Copiar solo los archivos de manifiesto para cachear las dependencias
COPY package.json package-lock.json* ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# El comando se proporcionará desde docker-compose
