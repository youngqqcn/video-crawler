##
# Pixabay API (unofficial)
# @author Luk� Pleva� <lukas@plevac.eu>
# @date 3.2.2022

import math
import requests
from .image import image
import urllib.parse

class query:

    ##
    # Init query on API
    # @params params params of query instance of class params
    # @return query object 
    def __init__(self, params):
        self.params = params
        self.cache = []
        self._getPage(0)

    ##
    # Get lenght of fonded images
    # @return len of fonded images
    def __len__(self):
        return self.info['totalHits']

    ##
    # Get item on index from result
    # @praram index index of item
    # return image object of item
    def __getitem__(self, index):
        if (index < 0):
            index += self.__len__()

        if not(self._inCache(index)):
            self._addToChache(index)

        return image(self.cache[index])

    ##
    # Check if is image with index in chace
    # @param index index of image
    # @return bool
    def _inCache(self, index):
        return len(self.cache) > index and self.cache[index] != None

    ##
    # Insert image in cache
    # @param index index of image
    # @param data data of image 
    def _cacheInsert(self, index, data):
        
        for i in range(len(self.cache) - 1, index - 1):
            self.cache.insert(i, None)

        self.cache.insert(index, data)

    ##
    # Download page from API and save to cache
    # @param page index of page (from 0)
    def _getPage(self, page, is_recursive = False):
        print("获取第{}页的视频链接".format(page))
        uri = "{host}?key={api}&q={query}&lang={lang}&orientation={orient}&per_page={per}&page={page}&order={order}&safesearch={safe}&min_width={width}&min_height={height}&editors_choice={editors}&category={cat}&colors={colors}".format(
            host    = self.params.host,
            query   = urllib.parse.quote(self.params.query, safe=''),
            api     = self.params.apiKey,
            lang    = self.params.lang,
            orient  = self.params.orientation,
            per     = self.params.perPage,
            page    = page + 1,
            order   = self.params.order,
            safe    = self.params.safeSearch,
            width   = self.params.minWidth,
            height  = self.params.minHeight,
            editors = self.params.editorsChoice,
            cat     = self.params.category,
            colors  = self.params.colors
        )

        r = requests.get(uri)

        if r.status_code == 200:
            pass
        elif r.status_code == 400 and '"page" is out of valid range' in r.text:
            return
        else:
            raise ValueError('Pixabay return status code != 200 for uri', uri, 'Invalid parameters?')
        

        data = r.json()

        # Update info
        self.info              = {}
        self.info['total']     = data['total']
        self.info['totalHits'] = data['totalHits'] # 通过API能够访问视频的数量, 最多500个

        # copy data
        for i in range(len(data['hits'])):
            self._cacheInsert(page * self.params.perPage + i, data['hits'][i])
        

        # 如果是递归进来的，则不再递归
        if not is_recursive:
            totalHits = data['totalHits']
            if totalHits >= 200:
                pages_count = math.ceil( totalHits / 200)
                for next in range(2, pages_count+1):
                    self._getPage(next, is_recursive=True)
                pass
        
    
    ##
    # Download image with index to cache
    # @param index index of image
    def _addToChache(self, index):
        page = index // self.params.perPage
        self._getPage(page)