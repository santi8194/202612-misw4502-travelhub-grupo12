FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG BUILD_CONFIGURATION=production
ARG PUBLIC_APP_BASE_URL=http://localhost:4200
RUN if [ "$BUILD_CONFIGURATION" = "compose" ]; then \
      PUBLIC_APP_BASE_URL="$PUBLIC_APP_BASE_URL" node -e "const fs=require('fs'); const p='src/environments/environment.compose.ts'; const s=fs.readFileSync(p,'utf8').replace('__PUBLIC_APP_BASE_URL__', process.env.PUBLIC_APP_BASE_URL); fs.writeFileSync(p,s);" ; \
    fi
RUN npm run build -- --configuration=${BUILD_CONFIGURATION}

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/user-web/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
