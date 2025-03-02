# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /SSE-MovieAPI

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt /SSE-MovieAPI/

# Install required dependencies
RUN pip install --no-cache-dir -r /SSE-MovieAPI/requirements.txt

# Copy the rest of the application files
COPY watchlist.py /SSE-MovieAPI/

# Expose port 80
EXPOSE 80

# Define the command to run the application correctly
CMD ["python", "watchlist.py"]