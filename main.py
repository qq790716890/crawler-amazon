#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from amazon_crawler import AmazonCrawler
import logging

def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("          亚马逊商品爬虫工具")
    print("=" * 60)
    print("功能：")
    print("1. 根据关键词搜索商品")
    print("2. 支持多种筛选条件")
    print("3. 导出商品链接到Excel")
    print("=" * 60)

def get_user_input():
    """获取用户输入"""
    print("\n请输入搜索关键词：")
    keyword = input("关键词: ").strip()
    
    if not keyword:
        print("错误：关键词不能为空！")
        return None
    
    print("\n请输入最大爬取页数（建议1-10页）：")
    try:
        max_pages = int(input("页数: ").strip())
        if max_pages <= 0:
            max_pages = 5
    except ValueError:
        max_pages = 5
        print("使用默认值：5页")
    
    return keyword, max_pages

def get_filter_options():
    """获取筛选条件"""
    print("\n" + "=" * 40)
    print("筛选条件设置（直接回车跳过）：")
    print("=" * 40)
    
    filters = {}
    
    # 价格筛选
    print("\n价格筛选：")
    try:
        min_price_input = input("最低价格（美元）: ").strip()
        if min_price_input:
            filters["min_price"] = float(min_price_input)
    except ValueError:
        print("价格格式错误，跳过最低价格筛选")
    
    try:
        max_price_input = input("最高价格（美元）: ").strip()
        if max_price_input:
            filters["max_price"] = float(max_price_input)
    except ValueError:
        print("价格格式错误，跳过最高价格筛选")
    
    # 店铺评分筛选
    print("\n店铺评分筛选：")
    try:
        min_store_rating_input = input("最低店铺评分（1-5）: ").strip()
        if min_store_rating_input:
            store_rating = float(min_store_rating_input)
            if 1 <= store_rating <= 5:
                filters["min_store_rating"] = store_rating
            else:
                print("店铺评分应在1-5之间，跳过此筛选")
    except ValueError:
        print("评分格式错误，跳过店铺评分筛选")
    
    # 商品评分筛选
    print("\n商品评分筛选：")
    try:
        min_rating_input = input("最低商品评分（1-5）: ").strip()
        if min_rating_input:
            rating = float(min_rating_input)
            if 1 <= rating <= 5:
                filters["min_rating"] = rating
            else:
                print("商品评分应在1-5之间，跳过此筛选")
    except ValueError:
        print("评分格式错误，跳过商品评分筛选")
    
    # 评论数筛选
    print("\n评论数筛选：")
    try:
        min_reviews_input = input("最少评论数: ").strip()
        if min_reviews_input:
            filters["min_reviews"] = int(min_reviews_input)
    except ValueError:
        print("评论数格式错误，跳过评论数筛选")
    
    return filters

def main():
    """主函数"""
    print_banner()
    
    # 获取用户输入
    user_input = get_user_input()
    if not user_input:
        return
    
    keyword, max_pages = user_input
    
    # 获取筛选条件
    filters = get_filter_options()
    
    # 确认开始爬取
    print(f"\n准备开始爬取：")
    print(f"关键词: {keyword}")
    print(f"最大页数: {max_pages}")
    print(f"筛选条件: {filters if filters else '无'}")
    
    confirm = input("\n确认开始爬取？(y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("已取消爬取")
        return
    
    # 创建爬虫实例
    crawler = None
    try:
        print("\n正在初始化爬虫...")
        crawler = AmazonCrawler(headless=True)
        
        # 搜索商品
        print(f"\n开始搜索关键词: {keyword}")
        products = crawler.search_products(keyword, max_pages)
        
        if not products:
            print("未找到任何商品")
            return
        
        print(f"\n搜索完成，共找到 {len(products)} 个商品")
        
        # 应用筛选条件
        if filters:
            print("正在应用筛选条件...")
            filtered_products = crawler.filter_products(products, filters)
            products = filtered_products
        
        if not products:
            print("筛选后没有符合条件的商品")
            return
        
        # 保存到Excel
        filename = f"amazon_{keyword.replace(' ', '_')}.xlsx"
        print(f"\n正在保存到文件: {filename}")
        crawler.save_to_excel(products, filename)
        
        print(f"\n爬取完成！")
        print(f"共获取 {len(products)} 个商品")
        print(f"文件已保存为: {filename}")
        
        # 显示前几个商品信息
        print(f"\n前5个商品预览：")
        for i, product in enumerate(products[:5], 1):
            print(f"{i}. {product['商品名称'][:50]}...")
            print(f"   价格: {product['价格']} | 评分: {product['评分']} | 店铺: {product['店铺名称']}")
            print(f"   链接: {product['商品链接']}")
            print()
        
    except KeyboardInterrupt:
        print("\n用户中断了爬取过程")
    except Exception as e:
        print(f"\n爬取过程中出现错误: {e}")
        logging.error(f"爬取错误: {e}")
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    main() 