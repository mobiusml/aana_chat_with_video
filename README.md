# Chat with Video App

**Chat with Video App** is a multimodal chat application that allows users to upload a video and ask questions about the video content based on the visual and audio information. See [Chat with Video Demo notebook](notebooks/chat_with_video_demo.ipynb) for more information.

## Installation

To install the project, follow these steps:

1. Clone the repository.

2. Install additional libraries.

For optimal performance, you should also install [PyTorch](https://pytorch.org/get-started/locally/) version >=2.1 appropriate for your system. You can continue directly to the next step, but it will install a default version that may not make optimal use of your system's resources, for example, a GPU or even some SIMD operations. Therefore we recommend choosing your PyTorch package carefully and installing it manually.

Some models use Flash Attention. Install Flash Attention library for better performance. See [flash attention installation instructions](https://github.com/Dao-AILab/flash-attention?tab=readme-ov-file#installation-and-features) for more details and supported GPUs.

3. Install the package with poetry.

The project is managed with [Poetry](https://python-poetry.org/docs/). See the [Poetry installation instructions](https://python-poetry.org/docs/#installation) on how to install it on your system.

It will install the package and all dependencies in a virtual environment.

```bash
poetry install
```

4. Run the app.

```bash
CUDA_VISIBLE_DEVICES="0" aana deploy aana_chat_with_video.app:aana_app
```

## Usage

To use the project, follow these steps:

1. Run the app as described in the installation section.

```bash
CUDA_VISIBLE_DEVICES="0" aana deploy aana_chat_with_video.app:aana_app
```

Once the application is running, you will see the message `Deployed successfully.` in the logs. It will also show the URL for the API documentation.

> **⚠️ Warning**
>
> The applications require 1 largs GPUs to run. GPU should have at least 48GB of memory.
>
> The applications will detect the available GPU automatically but you need to make sure that `CUDA_VISIBLE_DEVICES` is set correctly.
> 
> Sometimes `CUDA_VISIBLE_DEVICES` is set to an empty string and the application will not be able to detect the GPU. Use `unset CUDA_VISIBLE_DEVICES` to unset the variable.
> 
> You can also set the `CUDA_VISIBLE_DEVICES` environment variable to the GPU index you want to use: `export CUDA_VISIBLE_DEVICES=0`.

2. Send a POST request to the app.

See [Chat with Video Demo notebook](notebooks/chat_with_video_demo.ipynb) for more information.

## Running with Docker

We provide a docker-compose configuration to run the application in a Docker container.

Requirements:

- Docker Engine >= 26.1.0
- Docker Compose >= 1.29.2
- NVIDIA Driver >= 525.60.13

To run the application, simply run the following command:

```bash
docker-compose up
```

The application will be accessible at `http://localhost:8000` on the host server.


> **⚠️ Warning**
>
> The applications require 1 GPUs to run.
>
> The applications will detect the available GPU automatically but you need to make sure that `CUDA_VISIBLE_DEVICES` is set correctly.
> 
> Sometimes `CUDA_VISIBLE_DEVICES` is set to an empty string and the application will not be able to detect the GPU. Use `unset CUDA_VISIBLE_DEVICES` to unset the variable.
> 
> You can also set the `CUDA_VISIBLE_DEVICES` environment variable to the GPU index you want to use: `CUDA_VISIBLE_DEVICES=0 docker-compose up`.


> **💡Tip**
>
> Some models use Flash Attention for better performance. You can set the build argument `INSTALL_FLASH_ATTENTION` to `true` to install Flash Attention. 
>
> ```bash
> INSTALL_FLASH_ATTENTION=true docker-compose build
> ```
>
> After building the image, you can use `docker-compose up` command to run the application.
>
> You can also set the `INSTALL_FLASH_ATTENTION` environment variable to `true` in the `docker-compose.yaml` file.
