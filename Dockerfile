FROM node:22-alpine AS ui
WORKDIR /ui
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir '.[bedrock]'
COPY data ./data
COPY --from=ui /ui/dist ./frontend/dist
RUN useradd --uid 10001 --create-home desk && mkdir /app/runtime && chown desk:desk /app/runtime
USER desk
EXPOSE 8000
CMD ["uvicorn", "freightdesk.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
