#!/bin/bash


IP=$(hostname -I | cut -d' ' -f1)


python3 Data_Storage.py --local "$IP" --proxy "Your proxy server's ip" >> output_server.log 2>&1 &


echo "Data_Storage.py Running"
