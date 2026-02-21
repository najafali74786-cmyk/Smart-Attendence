FROM python:3.11

# Set up a new user to avoid permission issues on Hugging Face
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Switch to Root to install system software (cmake and opencv dependencies)
USER root
RUN apt-get update && apt-get install -y \
    cmake \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Switch back to regular user
USER user

# Copy files and give ownership to user
COPY --chown=user . $HOME/app

# Install Python requirements
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir cmake
RUN pip install --no-cache-dir -r requirements.txt

# Hugging Face hamesha Port 7860 par chalta hai
EXPOSE 7860

# Start NA Corp OS Server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]