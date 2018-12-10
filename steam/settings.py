#from smart_getenv import getenv

BOT_NAME = 'steam'

SPIDER_MODULES = ['steam.spiders']
NEWSPIDER_MODULE = 'steam.spiders'

USER_AGENT = 'Steam Scraper'

ROBOTSTXT_OBEY = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'steam.middlewares.CircumventAgeCheckMiddleware': 600,
}

AUTOTHROTTLE_ENABLED = True

DUPEFILTER_CLASS = 'steam.middlewares.SteamDupeFilter'
#DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 0  # Never expire.
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [301, 302, 303, 306, 307, 308]
HTTPCACHE_STORAGE = 'steam.middlewares.SteamCacheStorage'

#AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID', type=str, default=None)
#AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY', type=str, default=None)

FEED_EXPORT_ENCODING = 'utf-8'

COOKIES_ENABLED = True

ITEM_PIPELINES = {
    'steam.pipelines.SteamPipeline': 300,
# 'myproject.pipelines.JsonWriterPipeline': 800 #another pipline
}
