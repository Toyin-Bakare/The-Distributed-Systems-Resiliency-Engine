FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY rate_limiter ./rate_limiter
COPY demo_api ./demo_api
COPY tools ./tools
ENV PORT=8080
EXPOSE 8080
CMD ["python", "-m", "demo_api.app"]
