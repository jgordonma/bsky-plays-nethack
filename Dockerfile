FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install all necessary system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    libbz2-dev \
    libncurses5-dev \
    flex \
    bison \
    libtinfo-dev \
    pkg-config \
    libzmq3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
# Install Python packages
# RUN pip install --no-cache-dir flask
# RUN pip install --no-cache-dir requests numpy pandas
# RUN pip install --no-cache-dir torch
# RUN pip install --no-cache-dir gymnasium==1.0.0
# RUN pip install --no-cache-dir nle==0.9.0
# RUN pip install --no-cache-dir nle-language-wrapper
# Only try to install nle-language-wrapper if absolutely necessary
# RUN pip install --no-cache-dir nle-language-wrapper

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the script when the container launches
CMD ["python", "script.py"]
