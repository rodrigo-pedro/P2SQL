#!/bin/bash

docker build -t app-frontend  .

docker run --rm -it -p 7860:7860 --name="app-frontend" --network="host" app-frontend
