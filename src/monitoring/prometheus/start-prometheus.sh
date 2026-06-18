#!/bin/sh
set -e

exec /bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --web.listen-address="0.0.0.0:${PORT:-9090}" \
  --storage.tsdb.path=/tmp/prometheus \
  --web.enable-lifecycle
