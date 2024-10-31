# Use the official lightweight Python image.
FROM python:3.12-slim-bullseye

# Allow statements and log messages to immediately appear in the logs.
ENV PYTHONUNBUFFERED True
ENV PORT 5000

# Copy local code to the container image.
COPY . .

# Set the working directory.
WORKDIR /src

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt /src/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /src/requirements.txt

# Expose port 60727
EXPOSE 60727

CMD ["uvicorn", "src/main:app", "--host", "0.0.0.0", "--port", "$PORT"]

