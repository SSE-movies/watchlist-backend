# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /watchlist-backend

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt .

# Install required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set environment variables
ENV PYTHONPATH=/watchlist-backend

# Expose port 5000
EXPOSE 5000

# Define the command to run the application
CMD ["python", "app.py"]
