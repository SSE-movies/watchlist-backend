# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /watchlist-backend

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt /watchlist-backend/

# Install required dependencies
RUN pip install --no-cache-dir -r /watchlist-backend/requirements.txt

# Copy the rest of the application files
COPY watchlist.py /watchlist-backend/

# Expose port 80
EXPOSE 80

# Define the command to run the application correctly
CMD ["python", "watchlist.py"]