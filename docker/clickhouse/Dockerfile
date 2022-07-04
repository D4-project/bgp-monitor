FROM bgp-monitor:latest
LABEL version="1.0" org="CIRCL" description="Tool for BGP monitoring with kvrocks install"


ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /opt/clickhouse/
RUN curl -O 'https://builds.clickhouse.com/master/aarch64/clickhouse' && chmod a+x ./clickhouse && sudo ./clickhouse install

RUN chmod +x /opt/bgp-monitor/docker/clickhouse/clickhouse.sh &&\
    cp /opt/bgp-monitor/docker/clickhouse/config.cfg /opt/bgp-monitor/etc/config.cfg

WORKDIR /opt/bgp-monitor
CMD ["/opt/bgp-monitor/docker/clickhouse/clickhouse.sh"]
