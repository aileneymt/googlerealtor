# Use the official Python image as the base
FROM python:3.11-slim

# Set the working directory
WORKDIR /app/api

# Copy the requirements file first to leverage Docker cache
COPY ./requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install -q condacolab
#RUN conda install -c conda-forge pmdarima -y

# Copy the rest of the application
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=development
ENV FLASK_APP=app.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]

