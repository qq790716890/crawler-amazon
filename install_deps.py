#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速安装依赖包脚本
"""

import subprocess
import sys
import time

def install_package(package_name):
    """安装单个包"""
    print(f"正在安装 {package_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ {package_name} 安装成功")
            return True
        else:
            print(f"❌ {package_name} 安装失败")
            print(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {package_name} 安装超时")
        return False
    except Exception as e:
        print(f"❌ {package_name} 安装异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("亚马逊爬虫依赖包安装")
    print("=" * 50)
    
    # 需要安装的包列表
    packages = [
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "pandas==2.1.4", 
        "openpyxl==3.1.2",
        "selenium==4.16.0",
        "webdriver-manager==4.0.1",
        "fake-useragent==1.4.0",
        "lxml==4.9.3",
        "python-dotenv==1.0.0"
    ]
    
    print(f"需要安装 {len(packages)} 个依赖包")
    print("开始安装...\n")
    
    success_count = 0
    failed_packages = []
    
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}]", end=" ")
        
        if install_package(package):
            success_count += 1
        else:
            failed_packages.append(package)
        
        # 短暂等待
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"安装完成！成功: {success_count}/{len(packages)}")
    
    if failed_packages:
        print(f"失败的包: {', '.join(failed_packages)}")
        print("\n请尝试手动安装失败的包:")
        for package in failed_packages:
            print(f"pip install {package}")
    else:
        print("✅ 所有依赖包安装成功！")
    
    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n安装过程中出现错误: {e}")
        sys.exit(1) 