import time
import sys

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from trio import sleep
from webdriver_manager.chrome import ChromeDriverManager

import logging
import os
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Test1:
    def __init__(self, headless: bool = True):
        """
        初始化亚马逊爬虫

        Args:
            headless: 是否使用无头模式
        """
        self.driver = None
        self.headless = headless
        self.ua = UserAgent()
        self.setup_driver()

    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument("--headless")

            # 添加反检测参数
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f"--user-agent={self.ua.random}")
            driver_path = None  # 初始化路径变量
            # 尝试运行ChromeDriver配置脚本
            try:
                from setup_chromedriver import setup_chromedriver_auto, check_chromedriver_exists

                if setup_chromedriver_auto():
                    logger.info("ChromeDriver配置成功")
                    # 配置成功后再次检查本地路径
                    existing_path = check_chromedriver_exists()
                    driver_path = existing_path
                else:
                    driver_path = ChromeDriverManager().install()
            except Exception as e:
                logger.error(f"运行ChromeDriver配置脚本时出错: {e}")
                raise Exception("ChromeDriver配置失败")

            # 修复ChromeDriver路径问题 - 更精确的修复
            if driver_path and os.path.isdir(driver_path):
                # 如果是目录，查找chromedriver可执行文件
                possible_paths = [
                    os.path.join(driver_path, "chromedriver"),
                    os.path.join(driver_path, "chromedriver-linux64", "chromedriver"),
                    os.path.join(driver_path, "chromedriver.exe"),
                    os.path.join(driver_path, "chromedriver-linux64", "chromedriver-linux64")
                ]

                for path in possible_paths:
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        driver_path = path
                        break
                    
            # 确保driver_path不为None
            if not driver_path:
                raise Exception("无法找到有效的ChromeDriver路径")

            logger.info(f"使用ChromeDriver路径: {driver_path}")

            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.info("Chrome驱动设置成功")

        except Exception as e:
            logger.error(f"设置Chrome驱动失败: {e}")
            raise

    def open(self, url):
        self.driver.get(url)

    def get_driver(self):
        return self.driver

if __name__ == '__main__':
    test_instance = Test1(False)
    driver = test_instance.get_driver()
    driver.get("https://www.baidu.com")
    time.sleep(5)
    driver.maximize_window()

    time.sleep(100000)