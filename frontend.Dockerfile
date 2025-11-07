# --- Stage 1: Build ---
# Usa una imagen de Node.js para construir el proyecto de Vite/React
FROM node:20-alpine as builder

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todo el código fuente del frontend al contenedor
COPY FrontendNode/ .

# Renombra el archivo de entorno para que Vite lo use durante el build
COPY .env.frontend ./.env

# Instala las dependencias del proyecto
RUN npm install

# Ejecuta el script de build para generar los archivos estáticos de producción
# Usamos 'set -e' para que el script falle si 'npm run build' devuelve un error.
RUN npm run build

# --- Stage 2: Serve ---
# Usa una imagen ligera de Nginx para servir los archivos estáticos
FROM nginx:1.25-alpine

# Copia los archivos estáticos construidos en la etapa anterior al directorio web de Nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Copia el archivo de configuración personalizado de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf