#!/bin/bash

docker build -t app-backend-agent -f Dockerfile .

docker run --rm -it -p7000:7000 --name="app-backend-agent" --network="host" app-backend-agent
