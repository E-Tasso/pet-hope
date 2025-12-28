# Production Dockerfile for PetHope Frontend

FROM node:20-alpine as base

# Build arguments (needed at build time for Nuxt)
ARG NUXT_PUBLIC_API_BASE=/api

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy app files
COPY . .

# Set env for build
ENV NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy built application
COPY --from=base /app/.output /app/.output
COPY --from=base /app/package*.json /app/

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=production
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the application
CMD ["node", ".output/server/index.mjs"]
