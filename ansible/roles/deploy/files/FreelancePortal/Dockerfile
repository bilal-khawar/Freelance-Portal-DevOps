# How to test:
# 1. Build the Docker image(in the main folder - Freelance-Portal-DevOps):
#    docker build -t freelance-portal ./FreelancePortal
# 2. Run the Docker container:
#    docker run -p 8000:8000 freelance-portal
# 3. Access the application at http://localhost:8000



# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Set the entrypoint to gunicorn
CMD ["gunicorn", "FreelancePortal.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120"]
