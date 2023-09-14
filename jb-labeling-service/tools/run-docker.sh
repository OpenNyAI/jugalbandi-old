#!/bin/bash

docker run -it --rm -p 8000:8000 \
  --env-file .env \
  gcr.io/indian-legal-bert/labeling_service:latest
