FROM python:3.13-slim

WORKDIR /app

# Install dependencies first so this layer is cached unless requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway and most PaaS inject $PORT; default to 8000 for a plain `docker run`.
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
