# coding:utf8
# author: yqq
# description: 爬 pexels 上的视频

import json
import os
from pypexels import PyPexels
from mylocaldb import MyLocalKVDb
import requests
import time


API_KEY = '563492ad6f917000010000014e4789b693f640b9b998681c580f4adc'


def download_file( url, dst_file):
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


def main():

    kv = MyLocalKVDb()

    keyfile = json.load(open('keywords.json'))
    keywords =  keyfile['keywords']
    print('一共{}组关键词'.format( len(keywords)))

  
    # instantiate PyPexels object
    py_pexel = PyPexels(api_key=API_KEY)

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
        search_videos_page = py_pexel.videos_search(query=search_key, per_page=80)
        pages = 1
        while True:
            try:
                print(f'获取第{pages}页上的视频链接')
                for video in search_videos_page.entries:
                    # print(video.id, video.user.get('name'), video.url)
                    # v = py_pexel.single_video(video_id=video.id)
                    max_hd_link = ''
                    for item in video.video_files:
                        print(item['link'])
                        if item['height'] >= 1920  and 'videon/mp4' in item['file_type']:
                            max_hd_link = item['link']
                    
                    if max_hd_link != '':
                        videos_urls.append((max_hd_link, video.id))

                if not search_videos_page.has_next:
                    break

                #只获取1页的
                break

                search_videos_page = search_videos_page.get_next_page()
                pages += 1
            except Exception as e:
                print('获取页面上的视频URL异常:{}'.format(e))
                break
        
        # return
        print(f'共{len(videos_urls)}视频链接')
        
        for x in range(0, len(videos_urls)):
            v = videos_urls[x]
            url = v[0]
            vid = v[1]

            if kv.exists(url): 
                continue

            print("=======================================================================")
            print('开始下载视频({}/{}):{}'.format(x+1, len(videos_urls), url))
            dst_file = os.path.join(download_dir,  str(vid) + '.mp4')

            try:
                download_file(url, dst_file)
                kv.put(url, 'ok')
            except Exception as e:
                # 如果下载存在删除没有完成的视频文件
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                print("下载异常:{}, 继续其他任务".format(e))
        


if __name__ == '__main__':
    main()
    