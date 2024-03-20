#!/bin/bash

# 使用 ps 命令查找正在运行的进程的 PID
PID=$(ps aux | grep 'ProxyServer.py' | grep -v grep | awk '{print $2}')

# 检查 PID 是否存在
if [ -z "$PID" ]; then
    echo "进程未找到，可能已经停止。"
else
    # 使用 kill 命令终止进程
    kill "$PID"
    echo "进程已停止。"
fi
