# syntax=docker/dockerfile:1
#
# Frontend image. Build context is ./frontend (set in docker-compose.yml).
# nginx.conf comes from a second build context named "infra" (./infra/docker).
#
# Stage 1 ("build") uses Node 24 + pnpm to produce static files in dist/.
# Stage 2 ("runtime") is nginx serving those files, running as a non-root user.

# ---------- build ----------
FROM node:24-trixie-slim AS build

# Corepack reads "packageManager" in package.json and provides that exact pnpm.
RUN corepack enable

WORKDIR /app

# Dependencies first: this layer is cached until package.json or the lockfile changes.
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Then the source, then the production build.
COPY . .
RUN pnpm build

# ---------- runtime ----------
# NGINX's own unprivileged image: runs as the "nginx" user and listens on 8080.
FROM nginxinc/nginx-unprivileged:1.31-alpine AS runtime

COPY --from=infra nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
