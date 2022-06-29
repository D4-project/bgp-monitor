FROM ubuntu:20.04
LABEL version="1.0" org="CIRCL" description="Tool for BGP monitoring"

WORKDIR /opt/bgp-monitor
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y sudo curl apt-transport-https apt-utils ssl-cert ca-certificates gnupg lsb-release wget\
    && curl -1sLf 'https://dl.cloudsmith.io/public/wand/libwandio/cfg/setup/bash.deb.sh' | sudo -E bash \
    && echo "deb https://pkg.caida.org/os/$(lsb_release -si|awk '{print tolower($0)}') $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/caida.list \
    && sudo wget -O /etc/apt/trusted.gpg.d/caida.gpg https://pkg.caida.org/os/ubuntu/keyring.gpg \
    && curl -s https://pkg.caida.org/os/$(lsb_release -si|awk '{print tolower($0)}')/bootstrap.sh | bash
RUN sudo apt update; sudo apt-get install -y bgpstream \
    && apt-get install -y python3-pip \
    && pip3 install pybgpstream

COPY ./ ./
RUN pip3 install -r requirements.txt

# For future use
# EXPOSE 80/tcp
# EXPOSE 80/udp
# For Github action : tar -zcvf monitor.tar.gz bgp-monitor/docker/
