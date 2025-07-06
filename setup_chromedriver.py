#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChromeDriver 配置脚本 - 国内用户专用
"""

import os
import platform
import urllib.request
import zipfile
from pathlib import Path

def get_chrome_version():
    """获取Chrome浏览器版本"""
    system = platform.system().lower()
    
    if system == "windows":
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        except:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            except:
                return None
    else:
        # Linux/macOS 可以通过命令行获取版本
        try:
            import subprocess
            result = subprocess.run(['google-chrome', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split()[-1]
        except:
            pass
        return None

def check_chromedriver_exists():
    """检查本地是否已存在ChromeDriver"""
    system = platform.system().lower()
    if system == "windows":
        chromedriver_name = "chromedriver.exe"
    else:
        chromedriver_name = "chromedriver"
    
    local_paths = [
        Path("chromedriver") / chromedriver_name,
        Path(chromedriver_name),
        Path(f"./chromedriver/{chromedriver_name}")
    ]
    
    for path in local_paths:
        if path.exists():
            return str(path)
    
    return None

def download_chromedriver(version=None):
    """下载ChromeDriver"""
    if not version:
        version = get_chrome_version()
        if not version:
            print("❌ 无法获取Chrome版本，请手动指定版本号")
            return False
    
    # 提取主版本号
    major_version = version.split('.')[0]
    
    print(f"🔍 检测到Chrome版本: {version}")
    
    # 创建下载目录
    download_dir = Path("chromedriver")
    download_dir.mkdir(exist_ok=True)
    
    # 检查本地是否已存在ChromeDriver
    existing_path = check_chromedriver_exists()
    if existing_path:
        print(f"✅ 找到本地ChromeDriver: {existing_path}")
        return True
    
    print(f"📥 未找到本地ChromeDriver，开始下载版本: {major_version}")
    
    # 获取系统类型
    system = platform.system().lower()
    
    # 国内镜像源
    mirrors = [
        f"https://npm.taobao.org/mirrors/chromedriver/{major_version}/chromedriver_win32.zip",
        f"https://cdn.npmmirror.com/binaries/chromedriver/{major_version}/chromedriver_win32.zip",
        f"https://registry.npmmirror.com/-/binary/chromedriver/{major_version}/chromedriver_win32.zip",
        f"https://mirrors.huaweicloud.com/chromedriver/{major_version}/chromedriver_win32.zip",
        f"https://mirrors.huaweicloud.com/chromedriver/{version}/chromedriver_win32.zip"
    ]
    
    if system == "darwin":  # macOS
        mirrors = [url.replace("win32", "mac64") for url in mirrors]
    elif system == "linux":
        mirrors = [url.replace("win32", "linux64") for url in mirrors]
    
    for mirror in mirrors:
        try:
            print(f"🔄 尝试从镜像下载: {mirror}")
            
            # 下载文件
            zip_path = download_dir / "chromedriver.zip"
            urllib.request.urlretrieve(mirror, zip_path)
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            
            # 删除zip文件
            zip_path.unlink()
            
            # 设置执行权限（Linux/macOS）
            if system != "windows":
                chromedriver_path = download_dir / "chromedriver"
                chromedriver_path.chmod(0o755)
            
            print(f"✅ ChromeDriver下载成功: {download_dir}")
            return True
            
        except Exception as e:
            print(f"❌ 从 {mirror} 下载失败: {e}")
            continue
    
    print("❌ 所有镜像源都下载失败")
    return False

def setup_environment():
    """设置环境变量"""
    chromedriver_path = Path("chromedriver/chromedriver.exe")
    if not chromedriver_path.exists():
        chromedriver_path = Path("chromedriver/chromedriver")
    
    if chromedriver_path.exists():
        # 添加到PATH环境变量
        current_path = os.environ.get('PATH', '')
        chromedriver_dir = str(chromedriver_path.parent.absolute())
        
        if chromedriver_dir not in current_path:
            os.environ['PATH'] = f"{chromedriver_dir};{current_path}"
            print(f"✅ 已添加ChromeDriver到PATH: {chromedriver_dir}")
        
        return True
    return False

def test_chromedriver():
    """测试ChromeDriver"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        
        print("✅ ChromeDriver测试成功")
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("    ChromeDriver 配置工具")
    print("=" * 50)
    
    # 下载ChromeDriver
    if not download_chromedriver():
        print("\n💡 手动下载方案:")
        print("1. 访问: https://chromedriver.chromium.org/")
        print("2. 下载对应版本的ChromeDriver")
        print("3. 解压到项目根目录的chromedriver文件夹")
        return False
    
    # 设置环境
    if not setup_environment():
        print("❌ 环境设置失败")
        return False
    
    # 测试
    if not test_chromedriver():
        print("❌ ChromeDriver测试失败")
        return False
    
    print("\n🎉 ChromeDriver配置完成！")
    return True

def setup_chromedriver_auto():
    """自动配置ChromeDriver（供其他脚本调用）"""
    try:
        # 检查本地是否已存在ChromeDriver;本地没有，尝试下载
        return check_chromedriver_exists() or download_chromedriver()

    except Exception as e:
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 可以开始使用爬虫了！")
        else:
            print("\n❌ 配置失败，请手动下载ChromeDriver")
    except KeyboardInterrupt:
        print("\n\n⚠️  配置被用户中断")
    except Exception as e:
        print(f"\n❌ 配置过程中出现错误: {e}") 