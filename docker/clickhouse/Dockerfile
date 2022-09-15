FROM bgp-monitor:latest
LABEL version="1.0" org="CIRCL" description="Tool for BGP monitoring with ClickHouse install"

WORKDIR /opt/clickhouse/
RUN curl -O 'https://builds.clickhouse.com/master/amd64/clickhouse' && chmod a+x clickhouse && ./clickhouse install

RUN chmod +x /opt/bgp-monitor/docker/clickhouse/clickhouse.sh &&\
    cp /opt/bgp-monitor/docker/clickhouse/config.cfg /opt/bgp-monitor/etc/config.cfg

WORKDIR /opt/bgp-monitor/bin
CMD ["/opt/bgp-monitor/docker/clickhouse/clickhouse.sh"]

EXPOSE 9000