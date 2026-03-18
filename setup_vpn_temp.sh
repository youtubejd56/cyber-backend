#!/bin/sh
echo "yes" | easyrsa init-pki
echo "yes" | easyrsa build-ca nopass
easyrsa build-server-full server nopass
openvpn --genkey secret pki/ta.key
