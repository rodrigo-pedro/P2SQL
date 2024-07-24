#!/bin/bash

docker build -t app-backend-chain -f Dockerfile .

docker run --rm -it -p7000:7000 --name="backend" --network="host" app-backend-chain
