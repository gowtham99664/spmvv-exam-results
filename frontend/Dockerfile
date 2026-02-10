FROM node:18-alpine

WORKDIR /app

# Build argument for API URL
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Limit memory for low-resource VMs
ENV NODE_OPTIONS="--max-old-space-size=1536"
ENV npm_config_prefer_offline=true

# Copy package files
COPY package*.json ./

# Install with minimal memory footprint
RUN npm ci --omit=dev --ignore-scripts || npm install --legacy-peer-deps --no-audit

# Copy app files
COPY . .

EXPOSE 2026

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "2026"]
