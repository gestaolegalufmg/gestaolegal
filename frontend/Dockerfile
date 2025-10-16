# Build stage - compile SPA
FROM node:24-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build static files
COPY . .
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine AS runner

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static files from build stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create non-root user for nginx
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
