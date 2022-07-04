FROM ubuntu:20.04
LABEL version="1.0" org="CIRCL" description="Tool for BGP monitoring"

WORKDIR /opt/bgp-monitor
COPY ./ ./
RUN chmod +x ./docker/entrypoint.sh && ./docker/entrypoint.sh
