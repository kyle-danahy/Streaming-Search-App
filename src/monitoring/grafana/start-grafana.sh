#!/bin/sh
set -e

export GF_SERVER_HTTP_PORT="${PORT:-3000}"
export GF_SERVER_HTTP_ADDR="0.0.0.0"
export GF_SECURITY_ADMIN_USER="${GF_SECURITY_ADMIN_USER:-admin}"
export GF_SECURITY_ADMIN_PASSWORD="${GF_SECURITY_ADMIN_PASSWORD:-admin}"

prometheus_url="${PROMETHEUS_URL:-https://streaming-search-prometheus-8b66711fac46.herokuapp.com}"
mkdir -p /etc/grafana/provisioning/datasources
sed "s|\${PROMETHEUS_URL}|${prometheus_url}|g" \
  /etc/grafana/templates/prometheus.yml.template \
  > /etc/grafana/provisioning/datasources/prometheus.yml

exec /run.sh
