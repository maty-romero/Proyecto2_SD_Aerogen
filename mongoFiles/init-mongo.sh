#!/bin/bash

mongoimport \
  --db windfarm_db \
  --collection telemetry \
  --file /docker-entrypoint-initdb.d/dataset.json \
  --mode insert

echo "âœ“ Dataset importado exitosamente"