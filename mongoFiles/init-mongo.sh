#!/bin/bash
set -e

mongoimport \
  --db windfarm_db \
  --collection turbines \
  --file /dataset.json \
  --mode insert

echo "✓ Dataset importado exitosamente"