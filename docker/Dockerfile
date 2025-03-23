FROM python:3.12-slim

WORKDIR /app

# Install uv and dependencies
RUN pip install --no-cache-dir --upgrade pip uv

# Copy requirements only to leverage Docker caching
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"] 