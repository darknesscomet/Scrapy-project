# -*- coding: utf-8 -*-

# Scrapy settings for facebook_ads_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'facebook_ads_scrapy'

SPIDER_MODULES = ['facebook_ads_scrapy.spiders']
NEWSPIDER_MODULE = 'facebook_ads_scrapy.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
URLLENGTH_LIMIT = 32768

# Input filename
INPUT_FILENAME = 'fbadslib.txt'

# Folder where to save files ('files' or 'c:/files' or '/usr/files')
FILES_STORE = 'files'

#Download file timeout (increase if there will be warnings took longer than 3600.0 seconds)
DOWNLOAD_TIMEOUT = 3600
# Retry count
RETRY_TIMES = 3
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 150
CONCURRENT_REQUESTS_PER_IP = 150

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 0.5  #must be commented when used with proxies


#To change count of downloaded files need also add new fields to items.py
IMAGES_COUNT = 20
VIDEOS_COUNT = 15

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    #'facebook_ads_scrapy.middlewares.ProxyRandomDownloaderMiddleware': 490,
    'facebook_ads_scrapy.middlewares.ProxyRoundRobinDownloaderMiddleware': 490,
    'facebook_ads_scrapy.middlewares.BlockDetectionMiddleware': 585,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'facebook_ads_scrapy.middlewares.RandomUserAgentMiddleware': 500
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'facebook_ads_scrapy.pipelines.MyFilesPipeline': 300,
}

# Uncomment to disable DOWNLOAD_FAIL_ON_DATALOSS responses
DOWNLOAD_FAIL_ON_DATALOSS = False

# Must be enabled to allow download redirected files
MEDIA_ALLOW_REDIRECTS = True

#Warnings about file size limit 128MB
DOWNLOAD_WARNSIZE = 134217728

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'facebook_ads_scrapy.middlewares.FacebookAdsScrapySpiderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
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
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
