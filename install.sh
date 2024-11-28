#!/bin/sh
poetry install
poetry run pip install flash-attn --no-build-isolation # temporary fix for flash-attn bug in vLLM