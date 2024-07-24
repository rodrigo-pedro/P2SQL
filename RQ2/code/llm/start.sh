#!/bin/bash

if [ "$1" == "CUDA" ]; then
    docker build -t llm -f Dockerfile.gpu .
    docker run --rm -it --gpus all -p 9000:8000 --name="llm" --mount type=bind,source=PATH_TO_MODELS,target=/models \
     llm --model /models/MODEL_NAME  --n_ctx 8192 --n_gpu_layers 81

else
    docker build -t llm -f Dockerfile.cpu .
    docker run --rm -it -p 9000:8000 --name="llm" --mount type=bind,source=PATH_TO_MODELS,target=/models \
     llm --model /models/MODEL_NAME  --n_ctx 8192
fi
