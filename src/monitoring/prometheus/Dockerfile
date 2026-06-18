FROM prom/prometheus:v2.53.4

COPY prometheus.yml.template /etc/prometheus/prometheus.yml.template
COPY start-prometheus.sh /start-prometheus.sh

USER root
RUN chmod +x /start-prometheus.sh
USER nobody

ENTRYPOINT ["/start-prometheus.sh"]
