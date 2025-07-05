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
                            if file.startswith("chromedriver") and not file.endswith(".txt") and not file.endswith(".chromedriver"):
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
                # 使用正确的选择器获取商品名称和链接
                title_element = container.find_element(By.CSS_SELECTOR, ".a-link-normal.s-line-clamp-4")
                if title_element:
                    product_url = title_element.get_attribute("href") or "N/A"
                    product_name = title_element.text.strip()
                else:
                    # 备选方案：使用.a-text-normal选择器
                    try:
                        title_element = container.find_element(By.CSS_SELECTOR, ".a-text-normal")
                        if title_element:
                            product_name = title_element.text.strip()
                    except:
                        pass
                        
            except Exception as e:
                logger.debug(f"提取商品名称时出错: {e}")
                # 备选方案：使用.a-text-normal选择器
                try:
                    title_element = container.find_element(By.CSS_SELECTOR, ".a-text-normal")
                    if title_element:
                        product_name = title_element.text.strip()
                except:
                    pass
            
            # 价格 - 使用正确的选择器组合
            price = "N/A"
            try:
                # 尝试获取完整价格
                price_element = container.find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
                if price_element:
                    price = price_element.get_attribute("innerHTML").strip()
                else:
                    # 如果无法获取完整价格，尝试组合整数和小数部分
                    try:
                        whole_element = container.find_element(By.CSS_SELECTOR, ".a-price-whole")
                        fraction_element = container.find_element(By.CSS_SELECTOR, ".a-price-fraction")
                        symbol_element = container.find_element(By.CSS_SELECTOR, ".a-price-symbol")
                        
                        whole = whole_element.text.strip() if whole_element else ""
                        fraction = fraction_element.text.strip() if fraction_element else ""
                        symbol = symbol_element.text.strip() if symbol_element else ""
                        
                        if whole:
                            price = f"{symbol}{whole}"
                            if fraction:
                                price += f".{fraction}"
                    except:
                        pass
                        
            except Exception as e:
                logger.debug(f"提取价格时出错: {e}")
            
            # 评分 - 使用正确的评分结构
            rating = "N/A"
            try:
                rating_element = container.find_element(By.CSS_SELECTOR, "i.a-icon-star-small .a-icon-alt")
                if rating_element:
                    rating_text = rating_element.get_attribute("innerHTML")
                    # 提取评分数字，如 "4.3 out of 5 stars"
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = rating_match.group(1)
                        
            except Exception as e:
                logger.debug(f"提取评分时出错: {e}")
            
            # 评论数 - 使用正确的评论结构
            reviews = "N/A"
            try:
                reviews_element = container.find_element(By.CSS_SELECTOR, "a[aria-label*='ratings'] span")
                if reviews_element:
                    reviews_text = reviews_element.text.strip()
                    # 提取数字，处理逗号分隔符
                    reviews_match = re.search(r'([\d,]+)', reviews_text)
                    if reviews_match:
                        reviews = reviews_match.group(1).replace(',', '')
                        
            except Exception as e:
                logger.debug(f"提取评论数时出错: {e}")
            
            # ASIN (Amazon Standard Identification Number)
            asin = "N/A"
            try:
                asin = container.get_attribute("data-asin")
            except:
                pass
            
            # 商品图片URL
            image_url = "N/A"
            try:
                img_selectors = [
                    ".s-image",
                    "img[data-image-index]",
                    "img[src*='media-amazon']"
                ]
                
                for selector in img_selectors:
                    try:
                        img_element = container.find_element(By.CSS_SELECTOR, selector)
                        if img_element:
                            image_url = img_element.get_attribute("src")
                            if image_url:
                                break
                    except:
                        continue
                        
            except Exception as e:
                logger.debug(f"提取图片URL时出错: {e}")
            
            # 促销信息
            promotion = "N/A"
            try:
                promotion_selectors = [
                    ".a-row.a-size-base.a-color-secondary span",
                    ".a-color-secondary span",
                    "[class*='promotion']"
                ]
                
                for selector in promotion_selectors:
                    try:
                        promotion_element = container.find_element(By.CSS_SELECTOR, selector)
                        if promotion_element:
                            promotion = promotion_element.text.strip()
                            if promotion and promotion != "N/A":
                                break
                    except:
                        continue
                        
            except Exception as e:
                logger.debug(f"提取促销信息时出错: {e}")
            
            # 配送信息
            delivery = "N/A"
            try:
                delivery_selectors = [
                    ".udm-primary-delivery-message",
                    ".a-color-base.udm-primary-delivery-message",
                    "[class*='delivery']"
                ]
                
                for selector in delivery_selectors:
                    try:
                        delivery_element = container.find_element(By.CSS_SELECTOR, selector)
                        if delivery_element:
                            delivery = delivery_element.text.strip()
                            if delivery and delivery != "N/A":
                                break
                    except:
                        continue
                        
            except Exception as e:
                logger.debug(f"提取配送信息时出错: {e}")
            
            # 店铺名称 - 亚马逊自营商品可能没有店铺信息
            store_name = "Amazon"
            
            # 店铺评分 - 亚马逊自营商品可能没有店铺评分
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