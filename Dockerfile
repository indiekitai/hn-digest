FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN uv pip install --system -e .

# Expose port
EXPOSE 8080

# Run server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
