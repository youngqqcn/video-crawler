# coding:utf8
# date: 2022-09-03
# author: yqq
# description: 爬取视频 pixabay.com上的视频

import os
from pixabay import core
import json
from mylocaldb import MyLocalKVDb


API_KEY = '29680557-bb8a14e2a8f66d56426d64cd3'

def main():

    kv = MyLocalKVDb()

    keyfile = json.load(open('keywords.json'))
    keywords =  keyfile['keywords']
    print('一共{}组关键词'.format( len(keywords)))

    px = core(API_KEY, host='https://pixabay.com/api/videos/')
    for n in range(1, len(keywords)+1):
        search_key = '+'.join(keywords[str(n)])
        print('关键词组合：{}'.format(search_key))
        space = px.query(search_key)
        print("匹配关键词的视频共有：{} 个".format(len(space)))
        for i in range(len(space)):
            v = space[i]
            vurl =v.getVideoURL()
            print('================================================================')
            print('当前正在爬第{}组关键词:{},开始下载视频({}/{}):{}'.format(n, search_key[:30] ,i+1, len(space) , vurl))
            if kv.exists(vurl): 
                continue
            try:
                subdir = search_key[:30]
                download_dir = os.path.join('./videos/sub/', subdir)
                if not os.path.exists( download_dir ):
                    # 类似 make -p
                    os.makedirs(download_dir, mode=0o777, exist_ok=True)
                v.downloadVideo(dst_dir=download_dir)
                kv.put(vurl, 'ok')
            except Exception as e:
                print("异常：{}".format(e))
                print("继续下一个视频")

    pass

if __name__ == '__main__':
    main()
    