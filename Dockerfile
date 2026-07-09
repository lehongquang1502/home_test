# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies if required (e.g., for uv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (astral-sh)
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh

# Copy the requirements-related files first to leverage Docker cache
# If you don't have a requirements.txt but use uv, we can just install from pyproject.toml or generate it
# Assuming you have standard pip requirements or uv setup:
# For now, let's just copy everything and use uv sync if pyproject exists, or pip install.
# Since we don't know the exact project file structure (pyproject.toml vs requirements.txt),
# we will just use pip with uv for speed for the known dependencies:
RUN uv pip install --system requests markdownify python-dotenv google-genai

# Copy the rest of the application code
COPY . .

# Run the main pipeline script when the container launches
CMD ["python", "main.py"]
