#!/bin/bash
set -euo pipefail

#############################################
# Script Name: openwebui-update.sh
# Description: Update  Open WebUI to the
#              latest version
# Usage: ./openwebui-update.sh
# Author: Michael K Alber
# Version: 1.0
#############################################

docker pull ghcr.io/open-webui/open-webui:main
docker stop open-webui
docker rm open-webui
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
