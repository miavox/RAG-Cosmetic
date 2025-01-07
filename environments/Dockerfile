# Use the official Miniconda3 base image
FROM continuumio/miniconda3

# Set the working directory in the container
WORKDIR /app

# Prevent tzdata from prompting for geographic area selection
ENV DEBIAN_FRONTEND=noninteractive

# Install git, OpenGL libraries, build-essential, and other dependencies
RUN apt-get update && \
    apt-get install -y git libgl1-mesa-glx libglib2.0-0 build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create a new Conda environment with Python 3.10
RUN conda create -n team01 python=3.10 -y

# Set the environment path to use the newly created Conda environment
ENV PATH="/opt/conda/envs/team01/bin:$PATH"

# Upgrade pip in the Conda environment
RUN /bin/bash -c "source activate team01 && pip install --upgrade pip"

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install the dependencies from requirements.txt into the Conda environment
RUN /bin/bash -c "source activate team01 && pip install --no-cache-dir -r /app/requirements.txt"

# Copy all project files into the container
COPY . /app

# Expose port 8000 for FastAPI
EXPOSE 8000

# Set the default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]