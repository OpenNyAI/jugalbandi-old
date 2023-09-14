#!/bin/bash

docker run -it --rm -p 8080:8080 \
  -v "$HOME/a0ae7026506d.json:/etc/jiva-service/creds.json:ro" \
  -e "GOOGLE_APPLICATION_CREDENTIALS=/etc/jiva-service/creds.json" \
  --env-file .env \
  gcr.io/indian-legal-bert/jiva_service:latest
