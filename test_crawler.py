#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
亚马逊爬虫测试脚本
"""

import logging
from amazon_crawler import AmazonCrawler

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_amazon_crawler():
    """测试亚马逊爬虫功能"""
    crawler = None
    try:
        # 创建爬虫实例
        crawler = AmazonCrawler(headless=True)
        
        # 搜索商品
        keyword = "laptop"
        print(f"搜索关键词: {keyword}")
        
        # 爬取商品
        products = crawler.search_products(keyword, max_pages=1)
        
        if not products:
            print("❌ 未找到商品")
            return
        
        print(f"✅ 成功找到 {len(products)} 个商品")
        
        # 显示前3个商品的详细信息
        print("\n前3个商品详情:")
        for i, product in enumerate(products[:3]):
            print(f"\n--- 商品 {i+1} ---")
            for key, value in product.items():
                if value and value != "N/A":
                    print(f"{key}: {value}")
        
        # 保存到Excel
        crawler.save_to_excel(products, "test_amazon_products.xlsx")
        print(f"\n✅ 商品数据已保存到 test_amazon_products.xlsx")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    test_amazon_crawler() 