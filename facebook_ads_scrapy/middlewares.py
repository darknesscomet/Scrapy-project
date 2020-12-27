# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import json


class BlockDetectionMiddleware(object):
    #block_str1 = 'blocked from searching or viewing the ad archive'
    #block_str2 = 'you have been temporarily blocked from searching or viewing the ad archive due to too many requests'
    # text = response.text.lower()
    # if self.block_str1 in text or self.block_str2 in text:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        pass

    def process_response(self, request, response, spider):
        ct = response.headers['Content-Type'].decode('utf-8')
        if 'javascript' in ct or 'json' in ct:
            idx = response.text.index('{')
            jbody = response.text[idx:]
            jdata = json.loads(jbody)
            request.meta['jdata'] = jdata
            if 'errorSummary' in jdata and 'blocked' in jdata['errorSummary'].lower() or \
                                    'errorDescription' in jdata and 'blocked' in jdata['errorDescription'].lower():
                new_request = request.copy()
                new_request.dont_filter = True
                spider.logger.debug('Blocked. Repeat %s', request.url)
                return new_request
        return response

    #def process_exception(self, request, exception, spider):
        #if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
        #        and not request.meta.get('dont_retry', False):
        #    return self._retry(request, exception, spider)
        #print('>>>>>>>>>>>>>>>>>', exception)


class ProxyRandomDownloaderMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        ProxyRandomDownloaderMiddleware.logger = crawler.spider.logger
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def __init__(self):
        self.proxies = self.get_proxies()

    def get_proxies(self):
        l = []
        try:
            with open('proxies.txt') as f:
                for line in f. readlines():
                     p = 'https://' + line.strip()
                     l.append(p)
        except Exception as e:
            ProxyRandomDownloaderMiddleware.logger.warn('{}. Continue without proxies'.format(e))
        ProxyRandomDownloaderMiddleware.logger.info('Found proxies: {}'.format(len(l)))
        ProxyRandomDownloaderMiddleware.logger.info(l[:5])
        if len(l) > 0:
            return l
        else:
            return None

    def process_request(self, request, spider):
        if self.proxies is not None:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        pass


class ProxyRoundRobinDownloaderMiddleware(ProxyRandomDownloaderMiddleware):
    def __init__(self):
        super(ProxyRoundRobinDownloaderMiddleware, self).__init__()
        self.counter = 0

    def process_request(self, request, spider):
        if self.proxies is not None:
            if self.counter > len(self.proxies) - 1:
                self.counter = 0
            proxy = self.proxies[self.counter]
            self.counter += 1
            request.meta['proxy'] = proxy
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        pass


class RandomUserAgentMiddleware(object):

    browsers = ['ff', 'chrome']
    ff = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:{}.0) Gecko/20100101 Firefox/{}.0'
    chrome = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.3770.100 Safari/537.36'

    def __init__(self, user_agent='Scrapy'):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings['USER_AGENT'])
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agent = getattr(spider, 'user_agent', self.user_agent)

    def process_request(self, request, spider):
        ua = self.user_agent
        version = random.randrange(70, 77)
        browser = random.choice(self.browsers)
        if browser == 'ff':
            ua = self.ff.format(version, version)
        elif browser == 'chrome':
            ua = self.chrome.format(version)
        request.headers.setdefault(b'User-Agent', ua)


class FacebookAdsScrapySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class FacebookAdsScrapyDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
