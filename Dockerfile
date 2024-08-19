# Use NVIDIA CUDA as base image
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Build args
ARG INSTALL_FLASH_ATTENTION=false

# Set working directory
WORKDIR /app

# Set environment variables to non-interactive (this prevents some prompts)
ENV DEBIAN_FRONTEND=non-interactive

# Install required libraries, tools, and Python3
RUN apt-get update && apt-get install -y ffmpeg curl git python3.10 python3-pip

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Update PATH
RUN echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.bashrc
ENV PATH="/root/.local/bin:$PATH"

# Copy project files into the container
COPY . /app

# Install the package with poetry
RUN poetry install

# Install flash attention
RUN poetry run pip install torch --index-url https://download.pytorch.org/whl/cu121
RUN if [[ "$INSTALL_FLASH_ATTENTION" = "true" ]] ; then \
      poetry run pip install flash-attn --no-build-isolation; \
    else \
      echo Skip flash_atten installation ; \
    fi

# Disable buffering for stdout and stderr to get the logs in real time
ENV PYTHONUNBUFFERED=1

# Expose the desired port
EXPOSE 8000

# Run the app
CMD ["poetry", "run", "aana", "deploy", "aana_chat_with_video.app:aana_app", "--host", "0.0.0.0"]
