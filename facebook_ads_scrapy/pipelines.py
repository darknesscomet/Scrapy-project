# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import os
from urllib.parse import urlparse
from scrapy.pipelines.files import FilesPipeline
from facebook_ads_scrapy.settings import IMAGES_COUNT, VIDEOS_COUNT
import pathlib


class MyFilesPipeline(FilesPipeline):
    path_profile_pictures = 'profile_pictures/'
    path_images = 'images/'
    path_videos = 'videos/'

    type_profile_picture = 1
    type_image = 2
    type_video = 3

    def generate_file_path(self, file_type, url, page_id='noPageId'):
        path = None
        orig_filename = os.path.basename(urlparse(url).path)
        if file_type == self.type_image:
            path = self.path_images + orig_filename
        elif file_type == self.type_video:
            path = self.path_videos + page_id + '/' + orig_filename
        elif file_type == self.type_profile_picture:
            ext = '.jpg'
            try:
                suffix = pathlib.Path(orig_filename).suffix
                if suffix:
                    ext = suffix
            except:
                pass
            path = '{}{}{}'.format(self.path_profile_pictures, page_id, ext)
        return path

    def file_path(self, request, response=None, info=None):
        file_type = request.meta['file_type']
        page_id = None
        if 'page_id' in request.meta:
            page_id = request.meta['page_id']
        return self.generate_file_path(file_type, request.url, page_id)

    def get_media_requests(self, item, info):
        for i in range(1, IMAGES_COUNT+1):
            key = 'image_url{}'.format(i)
            if key in item and item[key]:
                yield scrapy.Request(url=item[key], meta={"file_type":self.type_image})

        for i in range(1, VIDEOS_COUNT+1):
            key = 'video_url{}'.format(i)
            if key in item and item[key]:
                yield scrapy.Request(url=item[key], meta={"file_type":self.type_video})

        if 'page_profile_picture_url' in item and item['page_profile_picture_url']:
            yield scrapy.Request(url=item['page_profile_picture_url'], meta={"file_type":self.type_profile_picture, 'page_id': item['page_id']})

    def item_completed(self, results, item, info):
        file_paths = set()
        for ok, x in results:
            if ok:
                file_paths.add(x['path'])

        for i in range(1, IMAGES_COUNT+1):
            key = 'image_url{}'.format(i)
            if key in item and item[key]:
                r = self.generate_file_path(self.type_image, item[key])
                if r in file_paths:
                    item[key] = r

        for i in range(1, VIDEOS_COUNT+1):
            key = 'video_url{}'.format(i)
            if key in item and item[key]:
                r = self.generate_file_path(self.type_video, item[key])
                if r in file_paths:
                    item[key] = r

        if 'page_profile_picture_url' in item and item['page_profile_picture_url']:
            #r = self.generate_file_path('profile_picture', item['page_profile_picture_url'])
            #if r in file_paths:
            for file_path in file_paths:
                if file_path.startswith(self.path_profile_pictures):
                    item['page_profile_picture_url'] = file_path #r
            pass

        return item


'''
from scrapy.pipelines.media import MediaPipeline
ITEMS_DIR = "downloads"
class MyFilePipeline(MediaPipeline):

    def get_media_requests(self, item, info):
        if 'image_url1' in item and item['image_url1']:
            video_url = item['image_url1']
            print("MyFilePipeline downloading %s " % (video_url))
            request = scrapy.Request(
                url=video_url,
                meta={ "item":item, },
            )
            return request

    def media_downloaded(self, response, request, info):
        p = os.path.basename(urlparse(request.url).path)
        with open(p, "wb") as f:
            f.write(response.body)
        return
        (vpath, vname) = os.path.split(request.url)
        print('>>>',vpath, vname)
        item = response.meta['item']
        with open(os.path.join(ITEMS_DIR, vname), "wb") as f:
            f.write(response.body)

        #print( "MyFilePipeline download complete %s for %s" % (request.url, item['name']))

    def media_failed(self, failure, request, info):
        item = request.meta['item']
        print('>>>>>>>FAILED', failure, info)
        #print("MyFilePipeline download failed %s for %s" % (request.url, item['name']))'''
