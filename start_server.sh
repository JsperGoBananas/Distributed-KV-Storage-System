#!/bin/bash

# 获取本机 IP 地址
IP=$(hostname -I | cut -d' ' -f1)

# 执行 Datastorage.py 脚本，传递命令行参数，并将输出重定向到 output.log 文件中
python3 Data_Storage.py --local "$IP" --proxy "10.8.5.138" >> output_server.log 2>&1 &

# 提示消息
echo "Data_Storage.py Running"
