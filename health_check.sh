#!/bin/bash

# Perform your health check here, replace this example with appropriate logic
# In this example, we're just checking if the web server is running and responding
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)

if [[ $response -eq 200 ]]; then
  exit 0  # Health check passed (HTTP 200 OK)
else
  exit 1  # Health check failed
fi

