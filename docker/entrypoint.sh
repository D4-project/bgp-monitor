#!/bin/sh
apt-get update
apt-get upgrade -y
apt-get install -y sudo curl apt-transport-https apt-utils ssl-cert ca-certificates gnupg lsb-release wget python3-pip libpq-dev

curl -1sLf 'https://dl.cloudsmith.io/public/wand/libwandio/cfg/setup/bash.deb.sh' | sudo -E bash
echo "deb https://pkg.caida.org/os/$(lsb_release -si|awk '{print tolower($0)}') $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/caida.list
sudo wget -O /etc/apt/trusted.gpg.d/caida.gpg https://pkg.caida.org/os/ubuntu/keyring.gpg
curl -s https://pkg.caida.org/os/$(lsb_release -si|awk '{print tolower($0)}')/bootstrap.sh | bash

sudo apt update; sudo apt-get install -y bgpstream

pip3 install -r requirements.txt