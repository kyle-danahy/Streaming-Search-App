FROM grafana/grafana:11.4.0

USER root

COPY templates/ /etc/grafana/templates/
COPY provisioning/dashboards/ /etc/grafana/provisioning/dashboards/
COPY dashboards/ /var/lib/grafana/dashboards/
COPY start-grafana.sh /start-grafana.sh
RUN chmod +x /start-grafana.sh \
    && mkdir -p /etc/grafana/provisioning/datasources \
    && chown -R grafana:root /etc/grafana/provisioning

USER grafana

ENV GF_PATHS_PROVISIONING=/etc/grafana/provisioning
ENV GF_USERS_ALLOW_SIGN_UP=false
ENV PROMETHEUS_URL=https://streaming-search-prometheus-8b66711fac46.herokuapp.com

ENTRYPOINT ["/start-grafana.sh"]
