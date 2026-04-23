# Estágio 1: build do React/Vite
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# A URL do backend é injetada em build time via variável de ambiente
# Defina VITE_API_URL no Easypanel apontando para o domínio do seu backend
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Estágio 2: servir com Nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# Config do Nginx para SPA (roteamento do React funcionar)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
