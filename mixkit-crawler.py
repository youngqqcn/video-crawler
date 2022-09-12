# coding:utf8
# date: 2022-09-04
# author: yqq
# description: 爬取视频 mixkit.co 上的视频


import time
import requests
from bs4 import BeautifulSoup
import os
from clint.textui import progress
import json
from mylocaldb import MyLocalKVDb


search_domain_name = "https://mixkit.co/"
asset_domain_name = "https://assets.mixkit.co/"
search_name = search_domain_name+"free-stock-video/"
preview_name = asset_domain_name+"videos/preview"
original_name = asset_domain_name+"videos/download"
extention = ".mp4"


class MixkitCrawler:

    def __init__(self):
        pass

    def download_file(self, url, dst_file):
        print('开始下载视频:{}'.format(dst_file))
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            raise RuntimeError("视频链接链接失效")
        if os.path.exists(dst_file):
            print('视频文件:{},已经存在，跳过'.format(dst_file))
        
        
        start = int(time.time())
        r = requests.get(url, allow_redirects=True)
        if (r.status_code != 200):
            raise ValueError('Pixabay return status code != 200 for uri', url, 'Invalid parameters?')
        print('视频{}下载完成，开始保存...'.format(dst_file))
        with open(dst_file, 'wb') as handler:
            handler.write(r.content)
        print('视频{}保存成功!'.format(dst_file))
        end = int(time.time())
        print('耗时{}秒'.format(end - start))
       


    def get_page_count(self, search_key):
        """
        获取分页数
        """

        url = search_name+search_key+"/?page="+str(1)
        print(url)
        x = requests.get(url)
        soup = BeautifulSoup(x.content, 'lxml')
        page_urls = soup.findAll('a', attrs = {'class':'pagination__link'})
        if page_urls is None or len(page_urls) == 0:
            print('警告:没有匹配关键词的视频,当前关键词:{}'.format(search_key))
            return 0
        return len(page_urls) + 1


    def fetch_all_pages_a_tags(self, page_no, search_topic ):
        url = search_name+search_topic+"/?page="+str(page_no)
        print("获取第{}页上的视频链接,当前页面链接:{}".format(page_no, url)) 
        x = requests.get(url)
        soup = BeautifulSoup(x.content, 'lxml')
        cur_page_labels = soup.findAll('a', attrs = {'class':'item-grid-video-player__overlay-link'})
        return cur_page_labels
        

def main():

    kv = MyLocalKVDb(path='mixkit.db')

    mix =  MixkitCrawler() 

    keyfile = json.load(open('keywords.json'))
    keywords =  keyfile['keywords']
    print('一共{}组关键词'.format( len(keywords)))

    for n in range(1, len(keywords)+1):
        search_key = '+'.join(keywords[str(n)])
        print('关键词组合：{}'.format(search_key))

        subdir = search_key[:30]
        download_dir = os.path.join('./videos/sub/', subdir)
        if not os.path.exists( download_dir ):
            # 类似 make -p
            os.makedirs(download_dir, mode=0o777, exist_ok=True)

        # 获取分页数
        pages_count = mix.get_page_count(search_key)
        if pages_count == 0:
            continue

        videos_a_labels = []
        for p in range(1, pages_count+1):
            ret_a = mix.fetch_all_pages_a_tags(p, search_key)
            if ret_a is not None:
                videos_a_labels.extend(ret_a)

        print("关键词{},共有{}个视频".format(search_key[:30], len(videos_a_labels)))

        # 解析a标签，获取视频链接
        for x in range(len(videos_a_labels)):
            a = videos_a_labels[x]
            print()
            part_link = a.get("href").replace("free-stock-video/","mixkit-").rstrip("/")
            temp_arr = part_link.split("-")
            video_number = temp_arr[-1]
            original_link = original_name + part_link + extention

            if kv.exists(original_link): 
                continue

            print("=======================================================================")
            print('开始下载视频({}/{}):{}'.format(x+1, len(videos_a_labels), original_link))
            filepath = os.path.join(download_dir,  video_number+extention)

            try:
                mix.download_file(original_link,filepath)
                kv.put(original_link, 'ok')
            except Exception as e:
                # 如果下载存在删除没有完成的视频文件
                if os.path.exists(filepath):
                    os.remove(filepath)
                print("下载异常:{}, 继续其他任务".format(e))


    pass


if __name__ == '__main__':
    main()