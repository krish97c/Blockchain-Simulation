# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary system dependencies for bcrypt
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8501 for Streamlit to run
EXPOSE 8501

# Set the command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]
