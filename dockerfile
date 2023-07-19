# Use an appropriate base Python image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /backend

# Install system dependencies (if needed)
# For example, if your backend requires additional system libraries or packages
# RUN sudo apt-get install build-essential
# RUN sudo apt update
# RUN sudo apt install libimage-exiftool-perl

# Copy the requirements.txt and install Python dependencies
COPY requirements.txt /backend/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory to the container
COPY . /backend/

# Set environment variables (if needed)
# ENV MY_ENV_VARIABLE=value

# Create and activate the virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
ENV FLASK_ENV=aws

# Expose the port on which your Flask app is listening (replace 5000 with your app's port)
EXPOSE 5000

# Run your Flask app when the container starts
CMD ["python", "app.py"]