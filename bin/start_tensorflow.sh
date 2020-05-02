#!/bin/bash

#	-u $(id -u):$(id -g) \
docker run -it -d \
	-p 8888:8888 \
	--name tensorflow \
	--mount src=`pwd`,target=/final,type=bind \
	--gpus all \
	tensorflow/tensorflow:2.1.0-gpu-py3

docker exec -it tensorflow pip install -r final/tensorflow/requirements.txt
