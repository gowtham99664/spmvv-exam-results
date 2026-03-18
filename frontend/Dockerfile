FROM node:18-alpine

WORKDIR /app

ARG VITE_API_URL
ENV NODE_OPTIONS="--max-old-space-size=1536"

# Copy package files first for better layer caching
COPY package.json package-lock.json* ./

# Install dependencies inside container (ensures Linux-compatible binaries)
RUN npm install

# Copy the rest of the source code
COPY . .

# If VITE_API_URL build arg was provided, write it into .env so Vite picks it up
RUN if [ -n "$VITE_API_URL" ]; then echo "VITE_API_URL=$VITE_API_URL" > .env; fi

EXPOSE 2026

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "2026"]
