FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Config
ENV SURREALDB_URL=mem://
ENV LLM_PROVIDER=ollama
ENV LLM_MODEL=llama3.2

# Port
EXPOSE 8001

# Run
CMD ["python", "-m", "backend.main"]