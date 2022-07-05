FROM bgp-monitor:latest
LABEL version="1.0" org="CIRCL" description="Tool for BGP monitoring"


WORKDIR /opt/
RUN wget -O quest.tar.gz https://github.com/questdb/questdb/releases/download/6.4.2/questdb-6.4.2-rt-linux-amd64.tar.gz &&\
    tar -xvf quest.tar.gz &&\
    cp /opt/bgp-monitor/docker/quest/config.cfg /opt/bgp-monitor/etc/config.cfg &&\
    chmod +x /opt/bgp-monitor/docker/quest/quest.sh

WORKDIR /opt/bgp-monitor/bin
CMD ["/opt/bgp-monitor/docker/quest/quest.sh"]
EXPOSE 9000