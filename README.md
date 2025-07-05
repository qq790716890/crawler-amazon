# 亚马逊商品爬虫工具

一个功能强大的亚马逊商品爬虫工具，支持关键词搜索、多条件筛选和数据导出功能。

## 功能特性

### 🔍 搜索功能
- 根据关键词搜索亚马逊商品
- 支持多页爬取
- 自动处理分页和翻页
- 智能重试机制

### 🎯 筛选条件
- **价格筛选**: 最低价格、最高价格
- **店铺评分**: 最低店铺评分
- **商品评分**: 最低商品评分
- **评论数**: 最少评论数
- **店铺名称**: 包含特定关键词的店铺
- **商品名称**: 包含特定关键词的商品

### 📊 数据导出
- 导出为Excel格式
- 包含商品详细信息
- 自动生成统计信息
- 支持自定义文件名

### 🛡️ 反检测功能
- 随机User-Agent
- 随机延迟
- 浏览器指纹隐藏
- 智能重试机制

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 基础使用

```python
from amazon_crawler import AmazonCrawler

# 创建爬虫实例
crawler = AmazonCrawler(headless=True)

try:
    # 搜索商品
    products = crawler.search_products("laptop", max_pages=5)
    
    # 设置筛选条件
    filters = {
        "min_price": 500,
        "max_price": 2000,
        "min_rating": 4.0,
        "min_reviews": 100
    }
    
    # 筛选商品
    filtered_products = crawler.filter_products(products, filters)
    
    # 保存到Excel
    crawler.save_to_excel(filtered_products, "laptops.xlsx")
    
finally:
    crawler.close()
```

### 2. 高级使用

```python
from advanced_crawler import AdvancedAmazonCrawler

# 自定义配置
config = {
    "browser": {"headless": True, "timeout": 30},
    "crawler": {"delay_min": 1, "delay_max": 3, "max_retries": 2},
    "extraction": {
        "extract_price": True,
        "extract_rating": True,
        "extract_reviews": True,
        "extract_store_name": True,
        "extract_store_rating": True
    }
}

# 创建高级爬虫实例
crawler = AdvancedAmazonCrawler(config)

try:
    # 高级搜索（按评分排序）
    products = crawler.search_products_advanced(
        keyword="wireless headphones",
        filters={"min_price": 50, "max_price": 300, "min_rating": 4.2},
        max_pages=3,
        sort_by="rating"
    )
    
    # 高级筛选
    filtered_products = crawler.filter_products_advanced(products, filters)
    
    # 高级保存（包含统计信息）
    crawler.save_to_excel_advanced(filtered_products, "headphones.xlsx")
    
finally:
    crawler.close()
```

### 3. 交互式使用

```bash
python main.py
```

按照提示输入搜索关键词和筛选条件即可。

## 筛选条件说明

| 条件 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `min_price` | float | 最低价格（美元） | 100.0 |
| `max_price` | float | 最高价格（美元） | 500.0 |
| `min_store_rating` | float | 最低店铺评分（1-5） | 4.0 |
| `min_rating` | float | 最低商品评分（1-5） | 4.2 |
| `min_reviews` | int | 最少评论数 | 100 |
| `store_name_contains` | str | 店铺名称包含关键词 | "Amazon" |
| `product_name_contains` | str | 商品名称包含关键词 | "bluetooth" |

## 排序选项

高级爬虫支持以下排序方式：

- `relevance`: 相关性排序（默认）
- `price_low`: 价格从低到高
- `price_high`: 价格从高到低
- `rating`: 按评分排序
- `newest`: 按最新排序

## 配置文件

可以通过修改 `config.py` 文件来自定义爬虫行为：

```python
# 浏览器设置
BROWSER_CONFIG = {
    "headless": True,  # 无头模式
    "timeout": 30,     # 超时时间
}

# 爬取设置
CRAWLER_CONFIG = {
    "delay_min": 2,    # 最小延迟
    "delay_max": 4,    # 最大延迟
    "max_retries": 3,  # 最大重试次数
}

# 筛选条件默认值
DEFAULT_FILTERS = {
    "min_price": None,
    "max_price": None,
    "min_rating": None,
}
```

## 输出格式

Excel文件包含以下列：

- **商品名称**: 商品的完整名称
- **商品链接**: 商品详情页链接
- **价格**: 商品价格
- **评分**: 商品评分（1-5星）
- **评论数**: 评论数量
- **店铺名称**: 卖家店铺名称
- **店铺评分**: 店铺评分（1-5星）

高级版本还会生成统计信息表，包含价格统计、评分统计和热门店铺信息。

## 使用示例

查看 `example.py` 文件了解更多使用示例：

- 基础爬虫使用
- 高级爬虫使用
- 批量搜索
- 价格监控

## 注意事项

1. **遵守网站规则**: 请合理使用爬虫，避免对网站造成过大压力
2. **延迟设置**: 建议设置适当的延迟时间，避免被反爬虫机制检测
3. **数据准确性**: 爬取的数据仅供参考，实际购买时请以网站显示为准
4. **法律合规**: 请确保您的使用符合当地法律法规

## 故障排除

### 常见问题

1. **Chrome驱动问题**
   ```bash
   # 确保已安装Chrome浏览器
   # 程序会自动下载ChromeDriver
   ```

2. **网络连接问题**
   - 检查网络连接
   - 尝试使用代理
   - 增加超时时间

3. **反爬虫检测**
   - 增加延迟时间
   - 使用代理IP
   - 减少爬取页数

### 日志查看

程序会生成详细的日志信息，可以通过修改 `config.py` 中的日志设置来调整日志级别：

```python
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "file": "crawler.log",
}
```

## 许可证

本项目仅供学习和研究使用，请勿用于商业用途。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。