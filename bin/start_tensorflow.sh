#!/bin/bash

docker run -it -d \
	-p 8888:8888 \
	--name tensorflow \
	--mount src=`pwd`,target=/tf/final,type=bind \
	--gpus all \
	tensorflow/tensorflow:2.1.0-gpu-py3-jupyter

# installing git
docker exec -u root -it tensorflow apt update
docker exec -u root -it tensorflow apt install git -y

docker exec -it tensorflow pip install -r /tf/final/tensorflow/requirements.txt
