#!/bin/bash


IP=$(hostname -I | cut -d' ' -f1)


python3 ProxyServer.py --local "$IP" >> output_proxy.log 2>&1 &


echo "ProxyServer.py Running"
