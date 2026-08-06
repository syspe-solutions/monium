# ===============
# Step 1: UV Binary Extraction
# ===============
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

# ===============
# Step 2: Frontend Build
# ===============
FROM node:20-alpine AS frontend_builder

WORKDIR /build

COPY package.json ./
RUN npm install

COPY apps/ ./apps/
COPY tailwind.config.js tsconfig.json build.mjs ./

RUN npm run build

# ===============
# Step 3: Builder
# ===============
FROM python:3.11-slim AS builder

# Configurações do UV para performance
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /usr/src

# Copia o binário do UV da imagem oficial
COPY --from=uv_bin /uv /uvx /bin/

# Instala apenas dependências de sistema necessárias para compilação (build-time)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de definição de dependências primeiro (otimiza cache de camada)
COPY pyproject.toml uv.lock ./

# Instala dependências usando cache mount do BuildKit para evitar download repetido
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ===============
# Step 3: Runtime
# ===============
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /usr/src

# Instala apenas bibliotecas compartilhadas de runtime (muito mais leves)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmariadb3 \
    libldap2 \
    libsasl2-2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o ambiente virtual (venv) do estágio builder
COPY --from=builder /opt/venv /opt/venv

# Copia o código da aplicação (que mudará com frequência)
COPY . /usr/src

# Sobrescreve com todos os assets compilados pelo estágio frontend (todos os apps)
COPY --from=frontend_builder /build/apps/ /usr/src/apps/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn core.wsgi:application -c gunicorn.conf.py --bind 0.0.0.0:8000 --timeout 60"]
