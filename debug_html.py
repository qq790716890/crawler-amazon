#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from amazon_crawler import AmazonCrawler
from selenium.webdriver.common.by import By

# 设置日志
logging.basicConfig(level=logging.WARNING)  # 减少日志输出

def debug_html_structure():
    """调试HTML结构"""
    crawler = None
    try:
        crawler = AmazonCrawler(headless=False)
        
        # 搜索商品
        keyword = "laptop"
        print(f"搜索关键词: {keyword}")
        
        # 访问搜索页面
        search_url = f"https://www.amazon.sg/s?k={keyword}"
        crawler.driver.get(search_url)
        
        # 等待页面加载
        import time
        time.sleep(5)
        
        # 查找第一个商品容器
        containers = crawler.driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")
        
        if containers:
            first_container = containers[0]
            print(f"\n找到 {len(containers)} 个商品容器")
            
            print("\n" + "="*60)
            print("测试商品名称提取:")
            print("="*60)
            
            # 测试商品名称选择器
            try:
                title_element = first_container.find_element(By.CSS_SELECTOR, ".a-link-normal.s-line-clamp-4")
                print(f"✅ 找到商品名称元素")
                print(f"文本内容: {title_element.text.strip()}")
                print(f"链接: {title_element.get_attribute('href')}")
                
                # 尝试其他选择器
                print("\n尝试其他商品名称选择器:")
                title_selectors = [
                    "h2 a",
                    ".a-link-normal[href*='/dp/']",
                    "a[href*='/dp/']",
                    ".a-text-normal"
                ]
                
                for selector in title_selectors:
                    try:
                        elem = first_container.find_element(By.CSS_SELECTOR, selector)
                        print(f"✅ {selector}: '{elem.text.strip()[:50]}...'")
                    except Exception as e:
                        print(f"❌ {selector}: {e}")
                        
            except Exception as e:
                print(f"❌ 商品名称提取失败: {e}")
            
            print("\n" + "="*60)
            print("测试价格提取:")
            print("="*60)
            
            # 测试价格选择器
            try:
                price_element = first_container.find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
                print(f"✅ 找到价格元素")
                print(f"价格内容: '{price_element.text.strip()}'")
                print(f"价格innerHTML: '{price_element.get_attribute('innerHTML')}'")
                print(f"价格outerHTML: '{price_element.get_attribute('outerHTML')}'")
                
                # 尝试其他价格选择器
                print("\n尝试其他价格选择器:")
                price_selectors = [
                    ".a-price-whole",
                    ".a-price-fraction", 
                    ".a-price-symbol",
                    ".a-price[data-a-size='xl'] .a-offscreen",
                    ".a-price[data-a-color='base'] .a-offscreen"
                ]
                
                for selector in price_selectors:
                    try:
                        elem = first_container.find_element(By.CSS_SELECTOR, selector)
                        print(f"✅ {selector}: '{elem.text.strip()}'")
                    except Exception as e:
                        print(f"❌ {selector}: {e}")
                        
            except Exception as e:
                print(f"❌ 价格提取失败: {e}")
            
            print("\n" + "="*60)
            print("测试评分提取:")
            print("="*60)
            
            # 测试评分选择器
            try:
                rating_element = first_container.find_element(By.CSS_SELECTOR, "i.a-icon-star-small .a-icon-alt")
                print(f"✅ 找到评分元素")
                print(f"评分内容: {rating_element.get_attribute('innerHTML')}")
            except Exception as e:
                print(f"❌ 评分提取失败: {e}")
            
            print("\n" + "="*60)
            print("测试评论数提取:")
            print("="*60)
            
            # 测试评论数选择器
            try:
                reviews_element = first_container.find_element(By.CSS_SELECTOR, "a[aria-label*='ratings'] span")
                print(f"✅ 找到评论数元素")
                print(f"评论数内容: {reviews_element.text.strip()}")
            except Exception as e:
                print(f"❌ 评论数提取失败: {e}")
            
        else:
            print("未找到商品容器")
            
    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    debug_html_structure() 