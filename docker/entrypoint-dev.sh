#!/bin/bash

if [ ! -d /usr/src/app/configs ]; then
  echo "[STARTUP] Configs empty... copying the defaults"
  mkdir -p /usr/src/app/configs
  cp /usr/src/app/base_configs/* /usr/src/app/configs
else
  echo "[STARTUP] Configs found!"
fi

exec "$@"