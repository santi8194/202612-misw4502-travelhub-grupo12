# Etapa 1: Construcción (Build) usando Node.js
FROM node:20-alpine AS build

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias (solo los package para cachear la capa)
COPY package*.json ./

# Instalar dependencias limpias para CI o producción
RUN npm ci

# Copiar el resto del código
COPY . .

# Compilar la aplicación en modo producción
RUN npm run build --configuration=production

# Etapa 2: Servidor Web Ligero usando NGINX
FROM nginx:alpine

# Copiar la configuración personalizada de NGINX para evitar errores de ruteo 404
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar los archivos compilados estáticos del frontend desde la primera etapa
# (Angular 17+ guarda los archivos estáticos dentro de browser/)
COPY --from=build /app/dist/partner-web/browser /usr/share/nginx/html

# Exponer el puerto 80 del contenedor
EXPOSE 80

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
