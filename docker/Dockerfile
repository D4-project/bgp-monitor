FROM ubuntu:20.04
LABEL version="1.0" org="CIRCL" description="Tool for BGP monitoring"
ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /opt/bgp-monitor
COPY ./ ./
RUN chmod +x ./docker/entrypoint.sh && ./docker/entrypoint.sh
