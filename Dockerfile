# Use official Python image
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first and install them
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all project files into container
COPY . .

# Tell Docker the app runs on port 5000
EXPOSE 5000

# Command to run the app
CMD ["python3", "app.py"]


