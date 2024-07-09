# Aana Application Template

[Aana SDK](https://github.com/mobiusml/aana_sdk) is a powerful framework for building multimodal applications. It facilitates the large-scale deployment of machine learning models, including those for vision, audio, and language, and supports Retrieval-Augmented Generation (RAG) systems. This enables the development of advanced applications such as search engines, recommendation systems, and data insights platforms.

This repository contains a template that you can use to start building your own Aana application. It will help you get started with the Aana SDK and provide you with a basic structure for your application and its dependencies.

## How to use this template

1. Click on [Use this template](https://github.com/mobiusml/aana_app_template/generate).
2. Give your repository a name and click on "Create repository". The name of the repository will also be the name of your application and the Python package.
3. Wait for the first workflow to finish. This will rename the package to match the repository name.
4. Clone the repository to your local machine and start building your application.
5. Change the [LICENSE](/LICENSE) file to match your project's license. The default license is the Apache License 2.0.

## Getting started

The project template uses [Poetry](https://python-poetry.org/) for dependency management. To install the project, run the following commands:

```bash
poetry install
```

See [Tutorial](https://github.com/mobiusml/aana_sdk/blob/main/docs/tutorial.md) for more information on how to build your application.

## Project structure

```
aana_app_project/
├── config/                   | various configs, including settings, deployments and endpoints
│   ├── endpoints.py          | list of endpoints to deploy
│   ├── deployments.py        | list of deployments (models) to deploy
│   └── settings.py           | app settings
├── core/                     | core models and functionality
│   ├── models/               | data models
│   └── prompts/              | prompt templates for LLMs
├── deployments/              | custom deployments
├── endpoints/                | endpoint classes for the app
├── exceptions/               | custom exception classes
├── utils/                    | various utility functionality
└── app.py                    | main application file
```


## Installation

To install the project, follow these steps:

1. Clone the repository.

2. Install additional libraries.

```bash
apt update && apt install -y libgl1
```
> **🗒️ Note**
>
> For optimal performance, you should also install [PyTorch](https://pytorch.org/get-started/locally/) version >=2.1 appropriate for your system. You can continue directly to the next step, but it will install a default version that may not make optimal use of your system's resources, for example, a GPU or even some SIMD operations. Therefore we recommend choosing your PyTorch package carefully and installing it manually.

> **🗒️ Note**
>
> Some models use Flash Attention. Install Flash Attention library for better performance. See [flash attention installation instructions](https://github.com/Dao-AILab/flash-attention?tab=readme-ov-file#installation-and-features) for more details and supported GPUs.

3. Install the package with poetry.

The project is managed with [Poetry](https://python-poetry.org/docs/). See the [Poetry installation instructions](https://python-poetry.org/docs/#installation) on how to install it on your system.

It will install the package and all dependencies in a virtual environment.

```bash
poetry install
```

4. Run the app.

```bash
aana deploy aana_app_project.app:aana_app
```

## Usage

To use the project, follow these steps:

1. Run the app as described in the installation section.

```bash
aana deploy aana_app_project.app:aana_app
```

Once the application is running, you will see the message `Deployed successfully.` in the logs. It will also show the URL for the API documentation.

> **⚠️ Warning**
>
> If the application is using GPU, make sure that the GPU is available and the application can access it.
>
> The applications will detect the available GPU automatically but you need to make sure that `CUDA_VISIBLE_DEVICES` is set correctly.
> 
> Sometimes `CUDA_VISIBLE_DEVICES` is set to an empty string and the application will not be able to detect the GPU. Use `unset CUDA_VISIBLE_DEVICES` to unset the variable.
> 
> You can also set the `CUDA_VISIBLE_DEVICES` environment variable to the GPU index you want to use: `export CUDA_VISIBLE_DEVICES=0`.

2. Send a POST request to the app.

For example, if your application has `/summary` endpoint that accepts videos, you can send a POST request like this:

```bash
curl -X POST http://127.0.0.1:8000/summary -Fbody='{"video":{"url":"https://www.youtube.com/watch?v=VhJFyyukAzA"}}'
```
