#!/bin/bash

docker run -it -d \
	-p 8888:8888 \
	--name tensorflow \
	--mount src=`pwd`,target=/tf/final,type=bind \
	--gpus all \
	tensorflow/tensorflow:2.1.0-gpu-py3-jupyter

docker exec -it tensorflow pip install -r /tf/final/tensorflow/requirements.txt
