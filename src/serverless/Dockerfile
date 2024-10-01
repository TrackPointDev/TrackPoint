# Use the Python slim-bullseye-3.12 base image
FROM python:3.12-slim-bullseye

# Set the working directory
WORKDIR /serverless

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

ENV PORT=8080

# Command to run the application (adjust as needed)
CMD ["python", "app.py"]