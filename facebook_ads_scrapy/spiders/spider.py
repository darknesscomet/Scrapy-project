# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from facebook_ads_scrapy.items import Item
from facebook_ads_scrapy.settings import IMAGES_COUNT, VIDEOS_COUNT, INPUT_FILENAME
from urllib.parse import urlsplit, parse_qs, urlencode
import lxml.html
from lxml import etree
import datetime


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    api_search = 'https://www.facebook.com/ads/library/async/search_ads/?{}'
    referrer = 'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&impression_search_field=has_impressions_lifetime&view_all_page_id={}'
    data = {
        '__user': '0',
        '__a': '1',
        '__csr': '',
        '__req': 'n',
        '__beoa': '0',
        '__pc': 'PHASED:DEFAULT',
        'dpr': '1',
        '__ccg': 'EXCELLENT'
    }
    urls_count = 0

    def search_request(self, page_id, forward_cursor=None, page_profile_picture_url=None, ad_ids=set()):
        params = {
            'session_id': '',
            'count': '30',
            'active_status': 'all',
            'ad_type': 'all',
            'countries[0]': 'ALL',
            'impression_search_field': 'has_impressions_lifetime',
            'view_all_page_id': page_id
        }
        if forward_cursor:
            params['forward_cursor'] = forward_cursor
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': self.referrer.format(page_id),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        print("003 Referer", self.referrer.format(page_id))
        print("004 url", self.api_search.format(urlencode(params)))
        print("005 urlencode(self.data)", urlencode(self.data))
        return Request(url=self.api_search.format(urlencode(params)),
                    #   url=self.referrer.format(page_id),
                      method="POST",
                      body=urlencode(self.data),
                      headers=headers,
                      meta={'page_id': page_id,
                            'page_profile_picture_url': page_profile_picture_url,
                            'ad_ids': ad_ids,
                            'download_fail_on_dataloss': True,
                            'download_timeout': 300},
                      callback=self.parse)

    def start_requests(self):
        with open(INPUT_FILENAME, encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url:
                    try:
                        query = urlsplit(url).query
                        print("001 urlsplited url", query)
                        page_id = parse_qs(query)['view_all_page_id'][0].strip()
                        print("002 page_id", page_id)
                        if page_id.isdigit():
                            yield self.search_request(page_id)
                        else:
                            self.logger.warning(
                                'Parameter "view_all_page_id" must contain only digits in url {}'.format(url))
                    except Exception as e:
                        self.logger.warning('Parameter "view_all_page_id" not found {} in url {}'.format(e, url))

    def parse(self, response):
        try:
            ad_ids = response.meta['ad_ids']
            print("006 ad_ids=response.meta['ad_ids]", ad_ids)
        except:
            pass
        page_id = response.meta['page_id']
        print("007 page_id=response.meta['page_id']", page_id)
        jdata = response.meta['jdata']
        try:
            page_profile_picture_url = response.meta['page_profile_picture_url']
        except:
            page_profile_picture_url = None
        print("008 response.meta['page_profile_picture_url']", page_profile_picture_url)
        print("009 response.meta['jdata']", jdata)
        forwardCursor = jdata['payload']['forwardCursor']
        print("010 jdata['payload']['forwardCursor']", forwardCursor)

        for r in jdata['payload']['results']:
            for r2 in r:
                item = Item()
                item['sponsored'] = 'Sponsored'
                item['page_id'] = page_id

                ad_id = None
                try:
                    ad_id = r2['adArchiveID']
                    item['id'] = ad_id
                except Exception as e:
                    self.logger.debug('Missing field: {} [{}]'.format(e, page_id))
                try:
                    item['page_name'] = r2['pageName']
                except:
                    pass

                try:
                    if not page_profile_picture_url: # get only first profile pic, because they are different
                        page_profile_picture_url = r2['snapshot']['page_profile_picture_url']
                    item['page_profile_picture_url'] = page_profile_picture_url
                except:
                    pass

                try:
                    item['page_profile_uri'] = r2['snapshot']['page_profile_uri']
                except:
                    pass

                try:
                    page_categories = []
                    for k, v in r2['snapshot']['page_categories'].items():
                        page_categories.append(v)
                    item['page_categories'] = ','.join(page_categories)
                except:
                    pass

                try:
                    item['isActive'] = r2['isActive']
                except:
                    pass

                try:
                    timestamp = r2['startDate']
                    item['startDate'] = datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y @%I:%M%p')
                except:
                    pass

                try:
                    pp = r2['publisherPlatform']
                    item['ppFacebook'] = True if 'facebook' in pp else False
                    item['ppInstagram'] = True if 'instagram' in pp else False
                    item['ppAudienceNetwork'] = True if 'audience_network' in pp else False
                    item['ppMessenger'] = True if 'messenger' in pp else False
                except:
                    pass

                try:
                    display_format = r2['snapshot']['display_format']
                    item['display_format'] = display_format
                except Exception as e:
                    self.logger.debug('Missing field: {} [{},{}]'.format(e, page_id, ad_id))

                try:
                    body_html = r2['snapshot']['body']['markup']['__html']
                    item['body_html'] = body_html
                    doc = lxml.html.document_fromstring(item['body_html'])
                    item['body_text'] = "\n".join(x.strip() for x in etree.XPath("//text()")(doc))
                except:
                    pass

                item['learn_more_link'] = None
                try:
                    item['learn_more_link'] = r2['snapshot']['link_url']
                except:
                    pass
                try:
                    for card in r2['snapshot']['cards']:
                        try:
                            val = card['link_url']
                            item['learn_more_link'] = val
                            if val:
                                break
                        except:
                            pass
                except Exception as e:
                    self.logger.debug('Missing field: {} [{},{}]'.format(e, page_id, ad_id))

                ii = 1  #card images
                try:
                    for card in r2['snapshot']['cards']:
                        try:
                            image_url = None
                            try:
                                image_url = card['original_image_url']
                            except:
                                pass
                            if not image_url:
                                try:
                                    image_url = card['resized_image_url']
                                except:
                                    pass
                            if image_url:
                                item['image_url{}'.format(ii)] = image_url
                                ii += 1
                        except Exception as e:
                            self.logger.warning('CardImages {}'.format(e))
                except:
                    pass


                iv = 1 #card videos
                try:
                    for card in r2['snapshot']['cards']:
                        try:
                            video_url = None
                            try:
                                video_url = card['video_hd_url']
                            except:
                                pass
                            if not video_url:
                                try:
                                    video_url = card['video_sd_url']
                                except:
                                    pass
                            if video_url:
                                item['video_url{}'.format(iv)] = video_url
                                iv += 1
                        except Exception as e:
                            self.logger.warning('CardVideos {}'.format(e))
                except:
                    pass

                try:
                    for image in r2['snapshot']['images']:  # images
                        try:
                            image_url = None
                            try:
                                image_url = image['original_image_url']
                            except:
                                pass
                            if not image_url:
                                try:
                                    image_url = image['resized_image_url']
                                except:
                                    pass
                            if image_url:
                                item['image_url{}'.format(ii)] = image_url
                                ii += 1
                        except Exception as e:
                            self.logger.warning('Images {}'.format(e))
                except:
                    pass

                try:
                    for video in r2['snapshot']['videos']:  # videos
                        try:
                            video_url = None
                            try:
                                video_url = video['video_hd_url']
                            except:
                                pass
                            if not video_url:
                                try:
                                    video_url = video['video_sd_url']
                                except:
                                    pass
                            if video_url:
                                item['video_url{}'.format(ii)] = video_url
                                iv += 1
                        except Exception as e:
                            self.logger.warning('Videos {}'.format(e))
                except:
                    pass

                if ad_id and ad_id not in ad_ids:
                    ad_ids.add(ad_id)
                    yield item

        if forwardCursor:
            yield self.search_request(page_id, forwardCursor, page_profile_picture_url, ad_ids)
        else:
            self.urls_count += 1
            if self.urls_count % 100 == 0:
                self.logger.info('Done pages {}'.format(self.urls_count))
