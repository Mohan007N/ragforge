# ==========================================================
# RAGForge Frontend - Production Multi-Stage Dockerfile
# Stage 1: Build Vite React SPA
# Stage 2: Serve with Nginx Alpine
# ==========================================================

# ----------------- Stage 1: Build -----------------
FROM node:20-alpine AS builder

WORKDIR /app/react-frontend

# Copy package files for dependency caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build

# ----------------- Stage 2: Serve -----------------
FROM nginx:1.25-alpine AS runner

# Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder stage (vite outputs to ../frontend or dist)
COPY --from=builder /app/frontend /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
