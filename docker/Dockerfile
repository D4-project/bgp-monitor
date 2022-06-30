FROM ubuntu:20.04
LABEL version="1.0" org="CIRCL" description="Tool for BGP monitoring"

WORKDIR /opt/bgp-monitor
COPY ./ ./
RUN chmod +x ./docker/entrypoint.sh
RUN ./docker/entrypoint.sh

# For future use
# EXPOSE 80/tcp
# EXPOSE 80/udp
# For Github action : tar -zcvf monitor.tar.gz bgp-monitor/docker/
