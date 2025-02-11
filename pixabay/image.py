##
# Pixabay API (unofficial)
# @author Luk� Pleva� <lukas@plevac.eu>
# @date 3.2.2022

import requests
import os
import time

class image:
    ##
    # Init image object
    # @param data data of image in JSON format
    # @return image obj
    def __init__(self, data):
        self._raw_data = data

    ##
    # Get ID of image
    def getId(self):
        return self._raw_data['id']
    
    ##
    # Get page url of image
    def getPageURL(self):
        return self._raw_data['pageURL']

    ##
    # Get type of image
    def getType(self):
        return self._raw_data['type']
    
    ##
    # Get tags of image
    def getTags(self):
        return self._raw_data['tags']

    ##
    # Get url of Preview
    def getPreviewURL(self):
        return self._raw_data['previewURL']

    ##
    # Get width of Preview
    def getPreviewWidth(self):
        return self._raw_data['previewWidth']

    ##
    # Get Height of Preview
    def getPreviewHeight(self):
        return self._raw_data['previewHeight']

    ##
    # Get webformat URL
    def getWebformatURL(self):
        return self._raw_data['webformatURL']

    ##
    # Get width of webformat
    def getWebformatWidth(self):
        return self._raw_data['webformatWidth']

    ##
    # Get height of webformat
    def getWebformatHeight(self):
        return self._raw_data['webformatHeight']

    ##
    # Get large Image URL
    def getLargeImageURL(self):
        return self._raw_data['largeImageURL']

    ##
    # Get width of image
    def getImageWidth(self):
        return self._raw_data['imageWidth']

    ##
    # Get height of image
    def getImageHeight(self):
        return self._raw_data['imageHeight']
    
    ##
    # Get size of image
    def getImageSize(self):
        return self._raw_data['imageSize']
    
    ##
    # Get views of image
    def getViews(self):
        return self._raw_data['views']

    ##
    # Get downloads of image
    def getDownloads(self):
        return self._raw_data['downloads']

    ##
    # Get collections of image
    def getCollections(self):
        return self._raw_data['collections']

    ##
    # Get likes of image
    def getLikes(self):
        return self._raw_data['likes']

    ##
    # Get comments of image
    def getComments(self):
        return self._raw_data['comments']

    ##
    # Get author id of image
    def getUserId(self):
        return self._raw_data['user_id']
    
    ##
    # Get name of author of image
    def getUser(self):
        return self._raw_data['user']

    ##
    # Get url of image of author of image
    def getUserImageURL(self):
        return self._raw_data['userImageURL']


    ##
    # Download image to varaible
    # @param imtype type if image (webformat, preview, largeImage) (Default: webformat)
    # @return byte array of image
    def downloadRaw(self, imtype = 'webformat'):
        
        uri = None

        if (imtype == 'webformat'):
            uri = self.getWebformatURL()
        elif (imtype == 'largeImage'):
            uri = self.getLargeImageURL()
        elif (imtype == 'preview'):
            uri = self.getPreviewURL()
        else:
            raise ValueError('supported types is webformat, largeImage and preview.', imtype, 'unsupported')

        r = requests.get(uri, allow_redirects=True)

        if (r.status_code != 200):
            raise ValueError('Pixabay return status code != 200 for uri', uri, 'Invalid parameters?')

        return r.content
    
    def getVideoURL(self, vedioSize='large'):
        uri = self._raw_data['videos'][vedioSize]['url']
        return uri


    def downloadVideo(self, dst_dir = './', vedio_size='large', overwrite=True):
        uri = self._raw_data['videos'][vedio_size]['url']
        id = str(self.getId())
        ext = '.mp4' 
        dst_file = os.path.join(dst_dir, id+ext)
        if os.path.exists(dst_file) and overwrite:
            print('视频:{}已存在,跳过'.format(dst_file))
            return

        start = int(time.time())
        print('开始下载视频:{}'.format(dst_file))
        r = requests.get(uri, allow_redirects=True)
        if (r.status_code != 200):
            raise ValueError('Pixabay return status code != 200 for uri', uri, 'Invalid parameters?')
        print('视频{}下载完成，开始保存...'.format(dst_file))
        with open(dst_file, 'wb') as handler:
            handler.write(r.content)
        print('视频{}保存成功!'.format(dst_file))
        end = int(time.time())
        print('耗时{}秒'.format(end - start))


    ##
    # Download image to file
    # @param dst location of file to save
    # @param imtype type if image (webformat, preview, largeImage) (Default: webformat)
    def download(self, dst, imtype = 'webformat'):
        with open(dst, 'wb') as handler:
            handler.write(self.downloadRaw(imtype))

        