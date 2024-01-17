
BOT_NAME = 'shein'

SPIDER_MODULES = ['shein.spiders']
NEWSPIDER_MODULE = 'shein.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

#MAXIMUM depends on your proxy subscription
CONCURRENT_REQUESTS = 5
LOG_LEVEL = 'INFO'
LOG_FILE = 'log.txt'
LOG_FILE_APPEND = False

DOWNLOADER_MIDDLEWARES = {
   #'shein.middlewares.CustomRetryMiddleware': 90,
   'scrapy.downloadermiddlewares.retry.RetryMiddleware': 100,
}

RETRY_TIMES = 3 



TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
FEED_EXPORT_FIELDS=[
    
    'link',
    'main_image',
    'product_name_arabic',
    'product_name_eng',
    'category',
    'sku',
    'color',
    'column1',
    'desc_ar',
    'desc_en',
    'image1',
    'image2',
    'image3',
    'image4',
    'image5',
    'image6',
    'image7',
    'image8',
    'image9',
    'image10',
    
]