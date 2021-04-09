#!/usr/bin/env sh

## Write VPN ovpn files to seperate folders

# Top-level Dir for ovpns
mkdir ovpn_configs

# NordVPN
mkdir -p ovpn_configs/nordvpn
wget -q -O ovpn_configs/nordvpn/ovpn_tmp.zip https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip
unzip -q ovpn_configs/nordvpn/ovpn_tmp.zip -d ovpn_configs/nordvpn
rm ovpn_configs/nordvpn/ovpn_tmp.zip
rm -r ovpn_configs/nordvpn/ovpn_udp

# PIA
mkdir -p ovpn_configs/pia/ovpn_tcp
wget -q -O ovpn_configs/pia/ovpn_tcp/pia_tmp.zip https://www.privateinternetaccess.com/openvpn/openvpn.zip
unzip -q ovpn_configs/pia/ovpn_tcp/pia_tmp.zip -d ovpn_configs/pia/ovpn_tcp
rm ovpn_configs/pia/ovpn_tcp/pia_tmp.zip
#cp pia/* nordvpn/ovpn_tcp/

#Windscribe
mkdir -p ovpn_configs/wind
wget -q -O ovpn_configs/wind/ovpn_tcp.zip https://vpnrotate.s3.amazonaws.com/ovpn_tcp.zip
unzip -q ovpn_configs/wind/ovpn_tcp.zip -d ovpn_configs/wind/

rm ovpn_configs/wind/ovpn_tcp.zip