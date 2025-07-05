#!/bin/bash

echo "================================================"
echo "           亚马逊爬虫依赖包安装"
echo "================================================"
echo

# 检查Python
echo "正在检查Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "✅ Python已安装"
echo

# 升级pip
echo "正在升级pip..."
python3 -m pip install --upgrade pip

echo
echo "正在安装依赖包..."
echo "这可能需要几分钟时间，请耐心等待..."
echo

# 运行安装脚本
python3 install_deps.py

echo
echo "安装完成！" 