# -*- coding: utf-8 -*-

import time
import random
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import re
from typing import List, Dict, Optional, Tuple
import logging
import os
from config import *

class AdvancedAmazonCrawler:
    def __init__(self, config: Dict = None):
        """
        初始化高级亚马逊爬虫
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.driver = None
        self.ua = UserAgent()
        self.setup_logging()  # 先初始化日志
        self.setup_driver()   # 再初始化driver
    
    def setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', LOGGING_CONFIG)
        level = getattr(logging, log_config.get('level', 'INFO'))
        format_str = log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=level,
            format=format_str,
            filename=log_config.get('file'),
            filemode='a'
        )
        
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        try:
            browser_config = self.config.get('browser', BROWSER_CONFIG)
            chrome_options = Options()
            
            if browser_config.get('headless', True):
                chrome_options.add_argument("--headless")
            
            # 设置窗口大小
            window_size = browser_config.get('window_size', (1920, 1080))
            chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
            
            # 反检测设置
            anti_config = self.config.get('anti_detection', ANTI_DETECTION_CONFIG)
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User-Agent设置
            if anti_config.get('enable_user_agent_rotation', True):
                user_agent = self.ua.random
            else:
                user_agent = browser_config.get('user_agent', self.ua.random)
            
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # 自动下载并设置ChromeDriver
            driver_path = ChromeDriverManager().install()
            
            # 修复ChromeDriver路径问题
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
                    self.logger.info(f"修复ChromeDriver路径: {driver_path}")
            
            self.logger.info(f"使用ChromeDriver路径: {driver_path}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Chrome驱动设置成功")
            
        except Exception as e:
            self.logger.error(f"设置Chrome驱动失败: {e}")
            raise
    
    def search_products_advanced(self, keyword: str, filters: Dict = None, 
                               max_pages: int = None, sort_by: str = None) -> List[Dict]:
        """
        高级商品搜索功能
        
        Args:
            keyword: 搜索关键词
            filters: 筛选条件
            max_pages: 最大页数
            sort_by: 排序方式 ('relevance', 'price_low', 'price_high', 'rating', 'newest')
            
        Returns:
            商品信息列表
        """
        products = []
        max_pages = max_pages or self.config.get('crawler', CRAWLER_CONFIG).get('default_max_pages', 5)
        
        # 构建搜索URL
        base_url = self._build_search_url(keyword, sort_by)
        
        try:
            for page in range(1, max_pages + 1):
                self.logger.info(f"正在爬取第 {page} 页...")
                
                if page == 1:
                    url = base_url
                else:
                    url = f"{base_url}&page={page}"
                
                page_products = self._crawl_page(url, page)
                if not page_products:
                    self.logger.info("页面无商品数据，停止爬取")
                    break
                
                products.extend(page_products)
                self.logger.info(f"第 {page} 页爬取完成，获取到 {len(page_products)} 个商品")
                
                # 检查是否有下一页
                if not self._has_next_page():
                    self.logger.info("已到达最后一页")
                    break
                
                # 随机延迟
                if self.config.get('anti_detection', ANTI_DETECTION_CONFIG).get('enable_random_delay', True):
                    delay_config = self.config.get('crawler', CRAWLER_CONFIG)
                    delay = random.uniform(delay_config.get('delay_min', 2), delay_config.get('delay_max', 4))
                    time.sleep(delay)
                    
        except Exception as e:
            self.logger.error(f"搜索商品时出错: {e}")
        
        return products
    
    def _build_search_url(self, keyword: str, sort_by: str = None) -> str:
        """构建搜索URL"""
        base_url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
        
        # 添加排序参数
        if sort_by:
            sort_params = {
                'relevance': '',
                'price_low': '&s=price-asc-rank',
                'price_high': '&s=price-desc-rank',
                'rating': '&s=review-rank',
                'newest': '&s=date-desc-rank'
            }
            base_url += sort_params.get(sort_by, '')
        
        return base_url
    
    def _crawl_page(self, url: str, page_num: int) -> List[Dict]:
        """爬取单个页面"""
        retry_count = 0
        max_retries = self.config.get('crawler', CRAWLER_CONFIG).get('max_retries', 3)
        
        while retry_count < max_retries:
            try:
                self.driver.get(url)
                
                # 等待页面加载
                timeout = self.config.get('browser', BROWSER_CONFIG).get('timeout', 30)
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
                )
                
                # 解析商品信息
                return self._parse_products_advanced()
                
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"第 {page_num} 页爬取失败，重试 {retry_count}/{max_retries}: {e}")
                
                if retry_count >= max_retries:
                    self.logger.error(f"第 {page_num} 页爬取失败，已达到最大重试次数")
                    return []
                
                time.sleep(2)  # 重试前等待
        
        return []
    
    def _parse_products_advanced(self) -> List[Dict]:
        """高级商品信息解析"""
        products = []
        extraction_config = self.config.get('extraction', EXTRACTION_CONFIG)
        
        try:
            product_containers = self.driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")
            
            for container in product_containers:
                try:
                    product_info = self._extract_product_info_advanced(container, extraction_config)
                    if product_info:
                        products.append(product_info)
                except Exception as e:
                    self.logger.warning(f"解析单个商品时出错: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"解析商品列表时出错: {e}")
        
        return products
    
    def _extract_product_info_advanced(self, container, extraction_config: Dict) -> Optional[Dict]:
        """高级商品信息提取"""
        try:
            product_info = {}
            
            # 基本信息
            link_element = container.find_element(By.CSS_SELECTOR, "h2 a")
            product_info["商品名称"] = link_element.text.strip()
            product_info["商品链接"] = link_element.get_attribute("href")
            
            # 价格信息
            if extraction_config.get('extract_price', True):
                product_info["价格"] = self._extract_price(container)
            
            # 评分信息
            if extraction_config.get('extract_rating', True):
                product_info["评分"] = self._extract_rating(container)
            
            # 评论数
            if extraction_config.get('extract_reviews', True):
                product_info["评论数"] = self._extract_reviews(container)
            
            # 店铺信息
            if extraction_config.get('extract_store_name', True):
                product_info["店铺名称"] = self._extract_store_name(container)
            
            if extraction_config.get('extract_store_rating', True):
                product_info["店铺评分"] = self._extract_store_rating(container)
            
            # 库存状态
            if extraction_config.get('extract_availability', False):
                product_info["库存状态"] = self._extract_availability(container)
            
            # 配送信息
            if extraction_config.get('extract_shipping', False):
                product_info["配送信息"] = self._extract_shipping(container)
            
            return product_info
            
        except Exception as e:
            self.logger.warning(f"提取商品信息时出错: {e}")
            return None
    
    def _extract_price(self, container) -> str:
        """提取价格"""
        try:
            price_element = container.find_element(By.CSS_SELECTOR, ".a-price-whole")
            return price_element.text.strip()
        except:
            return "N/A"
    
    def _extract_rating(self, container) -> str:
        """提取评分"""
        try:
            rating_element = container.find_element(By.CSS_SELECTOR, "i.a-icon-star-small .a-icon-alt")
            rating_text = rating_element.get_attribute("innerHTML")
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            return rating_match.group(1) if rating_match else "N/A"
        except:
            return "N/A"
    
    def _extract_reviews(self, container) -> str:
        """提取评论数"""
        try:
            reviews_element = container.find_element(By.CSS_SELECTOR, "span[aria-label*='stars'] + span")
            reviews_text = reviews_element.text.strip()
            reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
            return reviews_match.group(1) if reviews_match else "N/A"
        except:
            return "N/A"
    
    def _extract_store_name(self, container) -> str:
        """提取店铺名称"""
        try:
            store_element = container.find_element(By.CSS_SELECTOR, ".a-row .a-size-base")
            return store_element.text.strip()
        except:
            return "N/A"
    
    def _extract_store_rating(self, container) -> str:
        """提取店铺评分"""
        try:
            store_rating_element = container.find_element(By.CSS_SELECTOR, ".a-row .a-icon-alt")
            store_rating_text = store_rating_element.get_attribute("innerHTML")
            store_rating_match = re.search(r'(\d+\.?\d*)', store_rating_text)
            return store_rating_match.group(1) if store_rating_match else "N/A"
        except:
            return "N/A"
    
    def _extract_availability(self, container) -> str:
        """提取库存状态"""
        try:
            availability_element = container.find_element(By.CSS_SELECTOR, ".a-color-success")
            return availability_element.text.strip()
        except:
            return "N/A"
    
    def _extract_shipping(self, container) -> str:
        """提取配送信息"""
        try:
            shipping_element = container.find_element(By.CSS_SELECTOR, ".a-color-secondary")
            return shipping_element.text.strip()
        except:
            return "N/A"
    
    def _has_next_page(self) -> bool:
        """检查是否有下一页"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, ".s-pagination-next:not(.s-pagination-disabled)")
            return True
        except:
            return False
    
    def filter_products_advanced(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """
        高级商品筛选功能
        
        Args:
            products: 商品列表
            filters: 筛选条件
            
        Returns:
            筛选后的商品列表
        """
        if not filters:
            return products
        
        filtered_products = []
        
        for product in products:
            if self._meets_advanced_criteria(product, filters):
                filtered_products.append(product)
        
        self.logger.info(f"筛选完成，从 {len(products)} 个商品中筛选出 {len(filtered_products)} 个")
        return filtered_products
    
    def _meets_advanced_criteria(self, product: Dict, filters: Dict) -> bool:
        """检查商品是否满足高级筛选条件"""
        try:
            # 价格筛选
            if "min_price" in filters and filters["min_price"]:
                try:
                    product_price = float(product.get("价格", "0").replace("$", "").replace(",", ""))
                    if product_price < filters["min_price"]:
                        return False
                except:
                    pass
            
            if "max_price" in filters and filters["max_price"]:
                try:
                    product_price = float(product.get("价格", "0").replace("$", "").replace(",", ""))
                    if product_price > filters["max_price"]:
                        return False
                except:
                    pass
            
            # 店铺评分筛选
            if "min_store_rating" in filters and filters["min_store_rating"]:
                try:
                    store_rating = float(product.get("店铺评分", "0"))
                    if store_rating < filters["min_store_rating"]:
                        return False
                except:
                    pass
            
            # 商品评分筛选
            if "min_rating" in filters and filters["min_rating"]:
                try:
                    rating = float(product.get("评分", "0"))
                    if rating < filters["min_rating"]:
                        return False
                except:
                    pass
            
            # 评论数筛选
            if "min_reviews" in filters and filters["min_reviews"]:
                try:
                    reviews = int(product.get("评论数", "0"))
                    if reviews < filters["min_reviews"]:
                        return False
                except:
                    pass
            
            # 店铺名称筛选
            if "store_name_contains" in filters and filters["store_name_contains"]:
                store_name = product.get("店铺名称", "").lower()
                if filters["store_name_contains"].lower() not in store_name:
                    return False
            
            # 商品名称关键词筛选
            if "product_name_contains" in filters and filters["product_name_contains"]:
                product_name = product.get("商品名称", "").lower()
                if filters["product_name_contains"].lower() not in product_name:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"检查筛选条件时出错: {e}")
            return True
    
    def save_to_excel_advanced(self, products: List[Dict], filename: str = None):
        """
        高级Excel保存功能
        
        Args:
            products: 商品列表
            filename: 文件名
        """
        try:
            if not products:
                self.logger.warning("没有商品数据可保存")
                return
            
            # 生成文件名
            if not filename:
                output_config = self.config.get('output', OUTPUT_CONFIG)
                template = output_config.get('excel_filename_template', 'amazon_products.xlsx')
                
                if output_config.get('include_timestamp', True):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = template.format(keyword="products", timestamp=timestamp)
                else:
                    filename = template.format(keyword="products", timestamp="")
            
            # 创建DataFrame
            df = pd.DataFrame(products)
            
            # 保存到Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='商品列表', index=False)
                
                # 添加统计信息
                stats_data = self._generate_statistics(products)
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='统计信息', index=False)
            
            self.logger.info(f"成功保存 {len(products)} 个商品信息到 {filename}")
            
        except Exception as e:
            self.logger.error(f"保存Excel文件时出错: {e}")
    
    def _generate_statistics(self, products: List[Dict]) -> List[Dict]:
        """生成统计信息"""
        stats = []
        
        # 价格统计
        prices = []
        for product in products:
            try:
                price = float(product.get("价格", "0").replace("$", "").replace(",", ""))
                if price > 0:
                    prices.append(price)
            except:
                pass
        
        if prices:
            stats.append({"统计项": "价格统计", "最小值": f"${min(prices):.2f}", "最大值": f"${max(prices):.2f}", "平均值": f"${sum(prices)/len(prices):.2f}"})
        
        # 评分统计
        ratings = []
        for product in products:
            try:
                rating = float(product.get("评分", "0"))
                if rating > 0:
                    ratings.append(rating)
            except:
                pass
        
        if ratings:
            stats.append({"统计项": "评分统计", "最小值": f"{min(ratings):.1f}", "最大值": f"{max(ratings):.1f}", "平均值": f"{sum(ratings)/len(ratings):.1f}"})
        
        # 店铺统计
        stores = {}
        for product in products:
            store = product.get("店铺名称", "未知")
            stores[store] = stores.get(store, 0) + 1
        
        for store, count in sorted(stores.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats.append({"统计项": "热门店铺", "店铺名称": store, "商品数量": count, "占比": f"{count/len(products)*100:.1f}%"})
        
        return stats
    
    def close(self):
        """关闭浏览器驱动"""
        if self.driver:
            self.driver.quit()
            self.logger.info("浏览器驱动已关闭") 