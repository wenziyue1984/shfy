# -*- coding: utf-8 -*-

# Scrapy settings for shfy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import shfy.ConnectMiddleware as connect
import random
import time
BOT_NAME = 'shfy'

SPIDER_MODULES = ['shfy.spiders']
NEWSPIDER_MODULE = 'shfy.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'shfy (+http://www.yourdomain.com)'


DOWNLOAD_TIMEOUT = 20
COOKIES_ENABLED = False

# DOWNLOAD_DELAY = random.choice([1,2,3,4])
DOWNLOAD_DELAY = 0.5
ITEM_PIPELINES = {
    'shfy.pipelines.ShfyPipeline':300
}

DOWNLOADER_MIDDLEWARES = {
    # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    'shfy.ConnectMiddleware.ProxyMiddlewareByAbu': 100,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 200,
    'shfy.ConnectMiddleware.RandomUserAgent':1
}

USER_AGENTS = connect.RandomUserAgent.USERAGENT

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
REDIRECT_ENABLED = False
HTTPERROR_ALLOWED_CODES = connect.UsedThing.HTTPERRORCODE

CONCURRENT_REQUESTS_PER_SPIDER = 5
####重试次数：超时，默认http code：500,502,503,504,408
RETRY_ENABLED = True
RETRY_TIMES =3



#########LOG
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FILE = connect.UsedThing.log_path+time.strftime("%Y%m%d", time.localtime())+"/"+BOT_NAME + '.log'
LOG_LEVEL = 'INFO'
LOG_STDOUT = False


# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'shfy.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'shfy.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'shfy.pipelines.SomePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
