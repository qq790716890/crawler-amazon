import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import re
from typing import List, Dict, Optional
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AmazonCrawler:
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
    
    def search_products(self, keyword: str, max_pages: int = 5) -> List[Dict]:
        """
        根据关键词搜索商品
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大爬取页数
            
        Returns:
            商品信息列表
        """
        products = []
        base_url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
        
        try:
            for page in range(1, max_pages + 1):
                logger.info(f"正在爬取第 {page} 页...")
                
                if page == 1:
                    url = base_url
                else:
                    url = f"{base_url}&page={page}"
                
                self.driver.get(url)
                time.sleep(random.uniform(2, 4))  # 随机延迟
                
                # 等待页面加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
                )
                
                # 解析商品信息
                page_products = self._parse_products()
                products.extend(page_products)
                
                logger.info(f"第 {page} 页爬取完成，获取到 {len(page_products)} 个商品")
                
                # 检查是否有下一页
                if not self._has_next_page():
                    logger.info("已到达最后一页")
                    break
                    
        except Exception as e:
            logger.error(f"搜索商品时出错: {e}")
        
        return products
    
    def _parse_products(self) -> List[Dict]:
        """解析页面中的商品信息"""
        products = []
        
        try:
            # 查找所有商品容器 - 使用新的选择器
            product_containers = self.driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")

            logger.info(f"找到 {len(product_containers)} 个商品容器")
            
            for i, container in enumerate(product_containers):
                try:
                    product_info = self._extract_product_info(container)
                    if product_info:
                        products.append(product_info)
                        logger.debug(f"成功解析第 {i+1} 个商品: {product_info.get('商品名称', 'N/A')[:50]}...")
                except Exception as e:
                    logger.warning(f"解析第 {i+1} 个商品时出错: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"解析商品列表时出错: {e}")
        
        logger.info(f"成功解析 {len(products)} 个商品")
        return products
    
    def _extract_product_info(self, container) -> Optional[Dict]:
        """从商品容器中提取商品信息"""
        try:
            # 商品名称和链接
            product_name = "N/A"
            product_url = "N/A"
            try:
                # 优先用 data-cy="title-recipe" 下的 a 标签
                title_elem = container.find_element(By.CSS_SELECTOR, '[data-cy="title-recipe"] a.a-link-normal')
                if title_elem:
                    product_url = title_elem.get_attribute("href") or "N/A"
                    # 补全相对链接
                    if product_url.startswith("/"):
                        product_url = "https://www.amazon.sg" + product_url
                    product_name = title_elem.text.strip()
            except Exception as e:
                logger.debug(f"提取商品名称时出错: {e}")
                # 备选方案：使用.a-text-normal选择器
                try:
                    title_element = container.find_element(By.CSS_SELECTOR, ".a-text-normal")
                    if title_element:
                        product_name = title_element.text.strip()
                except:
                    pass

            # 价格
            price = "N/A"
            try:
                price_elem = container.find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
                if price_elem:
                    price = price_elem.text.strip()
            except Exception as e:
                logger.debug(f"提取价格时出错: {e}")

            # 评分
            rating = "N/A"
            try:
                rating_elem = container.find_element(By.CSS_SELECTOR, "i.a-icon-star-small span.a-icon-alt")
                if rating_elem:
                    rating_text = rating_elem.get_attribute("innerHTML") or rating_elem.text
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = rating_match.group(1)
            except Exception as e:
                logger.debug(f"提取评分时出错: {e}")

            # 评论数
            reviews = "N/A"
            try:
                review_elem = container.find_element(By.CSS_SELECTOR, 'span.a-size-base.s-underline-text')
                if review_elem:
                    reviews = review_elem.text.strip().replace(',', '')
            except Exception as e:
                logger.debug(f"提取评论数时出错: {e}")

            # ASIN
            asin = "N/A"
            try:
                asin = container.get_attribute("data-asin")
            except:
                pass

            # 商品图片URL
            image_url = "N/A"
            try:
                img_elem = container.find_element(By.CSS_SELECTOR, "img.s-image")
                if img_elem:
                    image_url = img_elem.get_attribute("src")
            except Exception as e:
                logger.debug(f"提取图片URL时出错: {e}")

            # 促销信息
            promotion = "N/A"
            try:
                # 优先找价格下方的 strike-through 价格（如标准价、市场价等）
                promo_elem = container.find_element(By.CSS_SELECTOR, ".a-price.a-text-price .a-offscreen")
                if promo_elem:
                    promotion = promo_elem.text.strip()
                else:
                    # 备选：找促销相关的span
                    promo_span = container.find_element(By.CSS_SELECTOR, ".a-size-base.a-color-secondary")
                    if promo_span:
                        promotion = promo_span.text.strip()
            except Exception as e:
                logger.debug(f"提取促销信息时出错: {e}")

            # 配送信息
            delivery = "N/A"
            try:
                # 优先找data-cy="delivery-recipe"下的内容
                delivery_elem = container.find_element(By.CSS_SELECTOR, '[data-cy="delivery-recipe"] .a-row.a-size-base.a-color-secondary')
                if delivery_elem:
                    delivery = delivery_elem.text.strip()
                else:
                    # 备选：找包含“配送”字样的span
                    delivery_spans = container.find_elements(By.CSS_SELECTOR, 'span')
                    for span in delivery_spans:
                        text = span.text.strip()
                        if "配送" in text or "送达" in text:
                            delivery = text
                            break
            except Exception as e:
                logger.debug(f"提取配送信息时出错: {e}")

            # 店铺名称、店铺评分保持原样
            store_name = "Amazon"
            store_rating = "N/A"

            return {
                "商品名称": product_name,
                "商品链接": product_url,
                "价格": price,
                "评分": rating,
                "评论数": reviews,
                "ASIN": asin,
                "图片URL": image_url,
                "促销信息": promotion,
                "配送信息": delivery,
                "店铺名称": store_name,
                "店铺评分": store_rating
            }
        except Exception as e:
            logger.warning(f"提取商品信息时出错: {e}")
            return None
    
    def _has_next_page(self) -> bool:
        """检查是否有下一页"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, ".s-pagination-next:not(.s-pagination-disabled)")
            return True
        except:
            return False
    
    def filter_products(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """
        根据筛选条件过滤商品
        
        Args:
            products: 商品列表
            filters: 筛选条件字典
            
        Returns:
            过滤后的商品列表
        """
        filtered_products = []
        
        for product in products:
            if self._meets_criteria(product, filters):
                filtered_products.append(product)
        
        logger.info(f"筛选完成，从 {len(products)} 个商品中筛选出 {len(filtered_products)} 个")
        return filtered_products
    
    def _meets_criteria(self, product: Dict, filters: Dict) -> bool:
        """检查商品是否满足筛选条件"""
        try:
            # 价格筛选
            if "min_price" in filters and filters["min_price"]:
                try:
                    product_price = float(product["价格"].replace("$", "").replace(",", ""))
                    if product_price < filters["min_price"]:
                        return False
                except:
                    pass
            
            if "max_price" in filters and filters["max_price"]:
                try:
                    product_price = float(product["价格"].replace("$", "").replace(",", ""))
                    if product_price > filters["max_price"]:
                        return False
                except:
                    pass
            
            # 店铺评分筛选
            if "min_store_rating" in filters and filters["min_store_rating"]:
                try:
                    store_rating = float(product["店铺评分"])
                    if store_rating < filters["min_store_rating"]:
                        return False
                except:
                    pass
            
            # 商品评分筛选
            if "min_rating" in filters and filters["min_rating"]:
                try:
                    rating = float(product["评分"])
                    if rating < filters["min_rating"]:
                        return False
                except:
                    pass
            
            # 评论数筛选
            if "min_reviews" in filters and filters["min_reviews"]:
                try:
                    reviews = int(product["评论数"])
                    if reviews < filters["min_reviews"]:
                        return False
                except:
                    pass
            
            return True
            
        except Exception as e:
            logger.warning(f"检查筛选条件时出错: {e}")
            return True
    
    def save_to_excel(self, products: List[Dict], filename: str = "amazon_products.xlsx"):
        """
        保存商品信息到Excel文件
        
        Args:
            products: 商品列表
            filename: 文件名
        """
        try:
            if not products:
                logger.warning("没有商品数据可保存")
                return
            
            df = pd.DataFrame(products)
            df.to_excel(filename, index=False, engine='openpyxl')
            logger.info(f"成功保存 {len(products)} 个商品信息到 {filename}")
            
        except Exception as e:
            logger.error(f"保存Excel文件时出错: {e}")
    
    def close(self):
        """关闭浏览器驱动"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器驱动已关闭") 