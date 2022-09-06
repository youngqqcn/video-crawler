# coding:utf8
# author: yqq
# description: 爬 coverr 上的视频

import json
import os
# from pypexels import PyPexels
from mylocaldb import MyLocalKVDb
import requests
import time
import fake_useragent
import requests

HOST = 'https://api.coverr.co'
API_KEY = '89762043357f7844696176b9965a569d'

# ua = fake_useragent.UserAgent()



class Coverr():
    def __init__(self, api_key, host):
        self.api_key = api_key
        self.host =  host
        pass

    def search_videos(self, query, page, page_size=50):
        url = self.host + f'/videos?query={query}&urls=true&page={page}&page_size={page_size}&sort_by=date'
        header = {'Authorization' : f'Bearer {self.api_key}'}
        r = requests.get(url, headers=header)
        if r.status_code != 200:
            raise ValueError(r.text)
        return json.loads(r.content)
    

    def get_video(self, video_id):
        url = self.host + f'/videos/{video_id}'
        header = {'Authorization' : f'Bearer {self.api_key}'}
        r = requests.get(url, stream=True, headers=header)
        if r.status_code != 200:
            raise ValueError(r.text)
        return json.loads(r.content)


    def download_video(self, video_url, dst_file):

        print('开始下载视频:{}'.format(dst_file))
        # vinfo = self.get_video(video_id)
        # video_url = vinfo['urls']['mp4_download']
        # if not( video_url is not None and len(video_url) > 0):
        #     print('视频下载链接为空，跳过')
        #     return

        url = video_url
        if os.path.exists(dst_file):
            print('视频文件:{},已经存在，跳过'.format(dst_file))
        
        start = int(time.time())
        header = {'Authorization' : f'Bearer {self.api_key}'}
        r = requests.get(url, allow_redirects=True, timeout=15*60, headers=header)
        if (r.status_code != 200):
            raise ValueError('return status code != 200 for uri', url, 'Invalid parameters?')
        print('视频{}下载完成，开始保存...'.format(dst_file))
        with open(dst_file, 'wb') as handler:
            handler.write(r.content)
        print('视频{}保存成功!'.format(dst_file))
        end = int(time.time())
        print('耗时{}秒'.format(end - start))


def main():

    kv = MyLocalKVDb()

    keyfile = json.load(open('keywords.json'))
    keywords =  keyfile['keywords']
    print('一共{}组关键词'.format( len(keywords)))

  
    # instantiate PyPexels object
    cv = Coverr(api_key=API_KEY, host=HOST)

    for n in range(1, len(keywords)+1):
        search_key = '+'.join(keywords[str(n)])
        print('关键词组合：{}'.format(search_key))

        subdir = search_key[:30]
        download_dir = os.path.join('./videos/sub/', subdir)
        if not os.path.exists( download_dir ):
            # 类似 make -p
            os.makedirs(download_dir, mode=0o777, exist_ok=True)

        videos_urls = []

        # 获取所有视频链接
        print('开始查询视频')

        vs = cv.search_videos(search_key, page=0)
        for h in vs['hits']:
            mp4_download = h['urls']['mp4_download']
            mp4_download = mp4_download[ : mp4_download.find('&filename') ]
            videos_urls.append((h['id'], mp4_download))

        pages = vs['pages']
        for p in range(1, pages):
            vs = cv.search_videos(search_key, page=p)
            for h in vs['hits']:
                mp4_download = h['urls']['mp4_download']
                mp4_download = mp4_download[ : mp4_download.find('&filename') ]
                videos_urls.append((h['id'], mp4_download))
        
        # return
        print(f'共{len(videos_urls)}视频链接')
        
        for x in range(0, len(videos_urls)):
            v = videos_urls[x]
            vid = v[0]
            url = v[1]

            if kv.exists(url): 
                continue

            print("=======================================================================")
            print('开始下载视频({}/{}):{}'.format(x+1, len(videos_urls), url))
            dst_file = os.path.join(download_dir,  str(vid) + '.mp4')

            try:
                cv.download_video(url, dst_file)
                kv.put(url, 'ok')
            except Exception as e:
                # 如果下载存在删除没有完成的视频文件
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                print("下载异常:{}, 继续其他任务".format(e))
        

def test():
    cv = Coverr(API_KEY, HOST)
    # r = cv.search_videos('nature')
    # print(r)

    cv.download_video('S4s9rYwhbF', 'tmp.mp4')
    # print(cv.get_video('S4s9rYwhbF'))
    pass


if __name__ == '__main__':
    main()
    # test()
    