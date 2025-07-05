import time

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

            # 自动下载并设置ChromeDriver
            driver_path = ChromeDriverManager().install()

            # 修复ChromeDriver路径问题 - 更精确的修复
            if os.path.isdir(driver_path):
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
                else:
                    # 如果找不到可执行文件，尝试在目录中查找
                    for root, dirs, files in os.walk(driver_path):
                        for file in files:
                            if file.startswith("chromedriver") and not file.endswith(".txt") and not file.endswith(
                                    ".chromedriver"):
                                full_path = os.path.join(root, file)
                                if os.access(full_path, os.X_OK):
                                    driver_path = full_path
                                    break
                        if driver_path != ChromeDriverManager().install():
                            break

            # 额外的检查：如果路径仍然指向THIRD_PARTY_NOTICES文件，手动修复
            if "THIRD_PARTY_NOTICES" in driver_path:
                # 尝试找到正确的chromedriver文件
                base_dir = os.path.dirname(driver_path)
                correct_path = os.path.join(base_dir, "chromedriver")
                if os.path.exists(correct_path) and os.access(correct_path, os.X_OK):
                    driver_path = correct_path
                    logger.info(f"修复ChromeDriver路径: {driver_path}")

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
    driver = Test1(False).get_driver()
    driver.get("https://www.baidu.com")
    time.sleep(5)
    driver.maximize_window()

    time.sleep(100000)