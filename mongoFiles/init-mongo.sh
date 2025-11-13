#!/bin/bash
set -e

mongoimport \
  --db windfarm_db \
  --collection telemetry \
  --file /dataset.json \
  --mode insert

echo "✓ Dataset importado exitosamente"