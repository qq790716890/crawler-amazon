#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
亚马逊商品爬虫使用示例
"""

from amazon_crawler import AmazonCrawler
from advanced_crawler import AdvancedAmazonCrawler
import logging

def basic_example():
    """基础使用示例"""
    print("=== 基础爬虫使用示例 ===")
    
    # 创建爬虫实例
    crawler = AmazonCrawler(headless=True)
    
    try:
        # 搜索商品
        keyword = "laptop"
        print(f"搜索关键词: {keyword}")
        products = crawler.search_products(keyword, max_pages=2)
        
        print(f"找到 {len(products)} 个商品")
        
        # 设置筛选条件
        filters = {
            "min_price": 500,  # 最低价格 $500
            "max_price": 2000,  # 最高价格 $2000
            "min_rating": 4.0,  # 最低评分 4.0
            "min_reviews": 100  # 最少评论数 100
        }
        
        # 筛选商品
        filtered_products = crawler.filter_products(products, filters)
        print(f"筛选后剩余 {len(filtered_products)} 个商品")
        
        # 保存到Excel
        crawler.save_to_excel(filtered_products, "basic_example.xlsx")
        print("数据已保存到 basic_example.xlsx")
        
    finally:
        crawler.close()

def advanced_example():
    """高级使用示例"""
    print("\n=== 高级爬虫使用示例 ===")
    
    # 自定义配置
    config = {
        "browser": {
            "headless": True,
            "timeout": 30
        },
        "crawler": {
            "delay_min": 1,
            "delay_max": 3,
            "max_retries": 2,
            "default_max_pages": 3
        },
        "extraction": {
            "extract_price": True,
            "extract_rating": True,
            "extract_reviews": True,
            "extract_store_name": True,
            "extract_store_rating": True,
            "extract_availability": True,
            "extract_shipping": True
        }
    }
    
    # 创建高级爬虫实例
    crawler = AdvancedAmazonCrawler(config)
    
    try:
        # 高级搜索
        keyword = "wireless headphones"
        print(f"搜索关键词: {keyword}")
        
        # 高级筛选条件
        filters = {
            "min_price": 50,
            "max_price": 300,
            "min_rating": 4.2,
            "min_reviews": 500,
            "store_name_contains": "Amazon",  # 只包含Amazon店铺
            "product_name_contains": "bluetooth"  # 商品名称包含bluetooth
        }
        
        # 按评分排序搜索
        products = crawler.search_products_advanced(
            keyword=keyword,
            filters=filters,
            max_pages=3,
            sort_by="rating"  # 按评分排序
        )
        
        print(f"找到 {len(products)} 个商品")
        
        # 高级筛选
        filtered_products = crawler.filter_products_advanced(products, filters)
        print(f"筛选后剩余 {len(filtered_products)} 个商品")
        
        # 高级保存（包含统计信息）
        crawler.save_to_excel_advanced(filtered_products, "advanced_example.xlsx")
        print("数据已保存到 advanced_example.xlsx")
        
    finally:
        crawler.close()

def batch_search_example():
    """批量搜索示例"""
    print("\n=== 批量搜索示例 ===")
    
    # 多个关键词
    keywords = ["smartphone", "tablet", "laptop"]
    
    # 通用筛选条件
    filters = {
        "min_price": 200,
        "max_price": 1000,
        "min_rating": 4.0
    }
    
    crawler = AmazonCrawler(headless=True)
    
    try:
        all_products = []
        
        for keyword in keywords:
            print(f"\n搜索关键词: {keyword}")
            products = crawler.search_products(keyword, max_pages=2)
            
            # 筛选
            filtered_products = crawler.filter_products(products, filters)
            print(f"找到 {len(filtered_products)} 个符合条件的商品")
            
            # 添加关键词标签
            for product in filtered_products:
                product["搜索关键词"] = keyword
            
            all_products.extend(filtered_products)
        
        # 保存所有结果
        crawler.save_to_excel(all_products, "batch_search_results.xlsx")
        print(f"\n批量搜索完成，总共保存 {len(all_products)} 个商品")
        
    finally:
        crawler.close()

def price_monitoring_example():
    """价格监控示例"""
    print("\n=== 价格监控示例 ===")
    
    # 监控特定商品的价格变化
    target_products = [
        "MacBook Pro",
        "iPhone 15",
        "Samsung Galaxy S24"
    ]
    
    crawler = AmazonCrawler(headless=True)
    
    try:
        price_data = []
        
        for product_name in target_products:
            print(f"监控商品: {product_name}")
            
            # 搜索商品
            products = crawler.search_products(product_name, max_pages=1)
            
            if products:
                # 获取第一个（最相关）的商品
                product = products[0]
                price_data.append({
                    "商品名称": product["商品名称"],
                    "当前价格": product["价格"],
                    "评分": product["评分"],
                    "评论数": product["评论数"],
                    "商品链接": product["商品链接"],
                    "监控时间": "2024-01-01"  # 实际使用时应该是当前时间
                })
        
        # 保存价格数据
        crawler.save_to_excel(price_data, "price_monitoring.xlsx")
        print(f"价格监控数据已保存，监控了 {len(price_data)} 个商品")
        
    finally:
        crawler.close()

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 运行各种示例
        basic_example()
        advanced_example()
        batch_search_example()
        price_monitoring_example()
        
        print("\n所有示例运行完成！")
        
    except KeyboardInterrupt:
        print("\n用户中断了程序")
    except Exception as e:
        print(f"程序运行出错: {e}")
        logging.error(f"程序错误: {e}") 