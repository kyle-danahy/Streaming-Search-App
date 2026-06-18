#!/bin/sh
set -e

prometheus_host="${PROMETHEUS_HOST:-streaming-search-prometheus-8b66711fac46.herokuapp.com}"
app_host="${APP_HOST:-streaming-search-app-373a9f8fa5f5.herokuapp.com}"

sed \
  -e "s|\${PROMETHEUS_HOST}|${prometheus_host}|g" \
  -e "s|\${APP_HOST}|${app_host}|g" \
  /etc/prometheus/prometheus.yml.template \
  > /tmp/prometheus.yml

exec /bin/prometheus \
  --config.file=/tmp/prometheus.yml \
  --web.listen-address="0.0.0.0:${PORT:-9090}" \
  --storage.tsdb.path=/tmp/prometheus \
  --web.enable-lifecycle
