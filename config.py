# -*- coding: utf-8 -*-
"""
亚马逊爬虫配置文件
"""

# 浏览器设置
BROWSER_CONFIG = {
    "headless": True,  # 是否使用无头模式
    "user_agent": None,  # 自定义User-Agent，None表示随机
    "window_size": (1920, 1080),  # 浏览器窗口大小
    "timeout": 30,  # 页面加载超时时间（秒）
}

# 爬取设置
CRAWLER_CONFIG = {
    "delay_min": 2,  # 页面间最小延迟（秒）
    "delay_max": 4,  # 页面间最大延迟（秒）
    "max_retries": 3,  # 最大重试次数
    "default_max_pages": 5,  # 默认最大爬取页数
}

# 筛选条件默认值
DEFAULT_FILTERS = {
    "min_price": None,  # 最低价格
    "max_price": None,  # 最高价格
    "min_store_rating": None,  # 最低店铺评分
    "min_rating": None,  # 最低商品评分
    "min_reviews": None,  # 最少评论数
}

# 输出设置
OUTPUT_CONFIG = {
    "excel_filename_template": "amazon_{keyword}_{timestamp}.xlsx",  # Excel文件名模板
    "include_timestamp": True,  # 是否在文件名中包含时间戳
    "encoding": "utf-8",  # 文件编码
}

# 日志设置
LOGGING_CONFIG = {
    "level": "INFO",  # 日志级别：DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "crawler.log",  # 日志文件名，None表示不保存到文件
}

# 反检测设置
ANTI_DETECTION_CONFIG = {
    "enable_random_delay": True,  # 启用随机延迟
    "enable_user_agent_rotation": True,  # 启用User-Agent轮换
    "enable_proxy": False,  # 启用代理（需要配置代理列表）
    "proxies": [],  # 代理列表
}

# 数据提取设置
EXTRACTION_CONFIG = {
    "extract_price": True,  # 是否提取价格
    "extract_rating": True,  # 是否提取评分
    "extract_reviews": True,  # 是否提取评论数
    "extract_store_name": True,  # 是否提取店铺名称
    "extract_store_rating": True,  # 是否提取店铺评分
    "extract_availability": False,  # 是否提取库存状态
    "extract_shipping": False,  # 是否提取配送信息
}

# 错误处理设置
ERROR_HANDLING_CONFIG = {
    "continue_on_error": True,  # 遇到错误时是否继续
    "log_errors": True,  # 是否记录错误
    "retry_failed_pages": True,  # 是否重试失败的页面
    "max_consecutive_errors": 3,  # 最大连续错误次数
} 