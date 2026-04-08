# Stage 1: Build
FROM node:18-alpine AS builder

# Clear any proxy settings inherited from Docker daemon
ENV http_proxy="" https_proxy="" HTTP_PROXY="" HTTPS_PROXY="" no_proxy="" NO_PROXY=""
ENV NODE_OPTIONS="--max-old-space-size=1536"

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Bake VITE_API_URL as relative /api so the app works on any host.
# Nginx in the runtime stage proxies /api -> backend container.
RUN echo "VITE_API_URL=/api" > .env && npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default nginx config that would conflict
RUN rm -f /etc/nginx/conf.d/default.conf.default

EXPOSE 2026

CMD ["nginx", "-g", "daemon off;"]
