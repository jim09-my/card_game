#!/bin/bash
# 后端服务快速启动脚本（Linux/macOS）

echo "========================================"
echo "后端服务快速启动"
echo "========================================"
echo

cd "$(dirname "$0")"

echo "检查依赖..."
python3 -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "缺少依赖，正在安装..."
    pip3 install -r ../requirements.txt
    if [ $? -ne 0 ]; then
        echo "依赖安装失败！"
        exit 1
    fi
fi

echo
echo "启动后端服务..."
echo "访问地址: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo

python3 start_server.py

