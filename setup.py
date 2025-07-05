#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
亚马逊爬虫项目安装脚本
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n📦 正在安装依赖包...")
    
    try:
        # 升级pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 安装依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ 依赖包安装成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def check_chrome():
    """检查Chrome浏览器"""
    print("\n🌐 检查Chrome浏览器...")
    
    system = platform.system().lower()
    
    if system == "windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
    elif system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser"
        ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ 找到Chrome浏览器: {path}")
            return True
    
    print("⚠️  未找到Chrome浏览器，请手动安装:")
    if system == "windows":
        print("   下载地址: https://www.google.com/chrome/")
    elif system == "darwin":
        print("   下载地址: https://www.google.com/chrome/")
    else:
        print("   Ubuntu/Debian: sudo apt install google-chrome-stable")
        print("   CentOS/RHEL: sudo yum install google-chrome-stable")
    
    return False

def create_directories():
    """创建必要的目录"""
    print("\n📁 创建项目目录...")
    
    directories = ["logs", "data", "exports"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")
        else:
            print(f"✅ 目录已存在: {directory}")

def test_installation():
    """测试安装"""
    print("\n🧪 测试安装...")
    
    try:
        # 测试导入
        import selenium
        import pandas
        import requests
        from fake_useragent import UserAgent
        
        print("✅ 所有依赖包导入成功")
        
        # 测试ChromeDriver
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver安装成功: {driver_path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 依赖包导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("=" * 50)
    
    print("1. 交互式使用:")
    print("   python main.py")
    print()
    
    print("2. 基础爬虫:")
    print("   python example.py")
    print()
    
    print("3. 测试功能:")
    print("   python test_crawler.py")
    print()
    
    print("4. 编程使用:")
    print("   from amazon_crawler import AmazonCrawler")
    print("   crawler = AmazonCrawler()")
    print("   products = crawler.search_products('laptop')")
    print()

def main():
    """主安装函数"""
    print("=" * 60)
    print("          亚马逊爬虫项目安装向导")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 检查Chrome
    check_chrome()
    
    # 创建目录
    create_directories()
    
    # 测试安装
    if not test_installation():
        print("❌ 安装测试失败，请检查错误信息")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 安装完成！")
    print("=" * 60)
    
    show_usage_examples()
    
    print("📝 注意事项:")
    print("- 请确保网络连接正常")
    print("- 首次运行会自动下载ChromeDriver")
    print("- 建议在虚拟环境中运行")
    print("- 遵守网站使用条款")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 安装成功！可以开始使用了。")
        else:
            print("\n❌ 安装失败，请检查错误信息。")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中出现未知错误: {e}")
        sys.exit(1) 