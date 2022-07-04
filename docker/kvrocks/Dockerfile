FROM bgp-monitor:latest
LABEL version="1.0" org="CIRCL" description="Tool for BGP monitoring with kvrocks install"

ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /opt/incubator-kvrocks
RUN curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg &&\
    echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list &&\
    sudo apt-get update &&\
    sudo apt-get -y install gcc g++ make cmake autoconf automake libtool redis git &&\
    git clone https://github.com/apache/incubator-kvrocks.git /opt/incubator-kvrocks &&\
    /opt/incubator-kvrocks/build.sh build &&\
    chmod +x /opt/bgp-monitor/docker/kvrocks/kvrocks.sh &&\
    cp /opt/bgp-monitor/docker/kvrocks/config.cfg /opt/bgp-monitor/etc/config.cfg

CMD ["/opt/bgp-monitor/docker/kvrocks/kvrocks.sh"]

EXPOSE 6666
