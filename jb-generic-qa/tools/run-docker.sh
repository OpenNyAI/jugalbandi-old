#!/bin/bash

docker run -it --rm -p 8080:8080 \
  -v "$HOME/a0ae7026506d.json:creds.json:ro" \
  --env-file .env  \
  -e "GOOGLE_APPLICATION_CREDENTIALS=creds.json" \
  gcr.io/indian-legal-bert/jugalbandi_genericqa_tap:latest