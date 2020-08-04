#!/bin/bash
docker build -t generator:generator .
docker run -d -p 5000:5000 generator\
  --name=generator \
  -v $PWD:/app generator
