#!/bin/bash

docker run -it --rm -p 8080:8080 \
  -v "$HOME/a0ae7026506d.json:/etc/generic-qa/creds.json:ro" \
  -e "GOOGLE_APPLICATION_CREDENTIALS=/etc/generic-qa/creds.json" \
  --env-file .env  \
  gcr.io/indian-legal-bert/jugalbandi_genericqa_tap:latest