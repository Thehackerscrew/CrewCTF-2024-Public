#!/bin/sh

docker build -t format-muscle .
docker run -p 1337:1337 -it format-muscle
