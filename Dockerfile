# Use the official lightweight Python image.
FROM python:3.12-slim-bullseye

# Allow statements and log messages to immediately appear in the logs.
ENV PYTHONUNBUFFERED True

# Set the working directory.
WORKDIR /usr/src/app

# Copy requirements.txt first to leverage Docker cache
COPY ./requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt

# Copy local code to the container image.
COPY ./src ./

# Expose port 60727
EXPOSE 5000
EXPOSE 60727

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]