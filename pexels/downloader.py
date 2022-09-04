'''
This script downloads the video from pexels when pexels video URL is passed

Usage: python main.py "{pexels_url}"
'''


# from genericpath import exists
import json
import requests
import os
import uuid
import logging
import random
# from media_cache import MediaCache
import hashlib


class VideoDownloader:

    def __init__(self, log_path="pexels_downloader.log") -> None:
        self.resolution_width = 1080
        self.pexels_api_url = "https://api.pexels.com/videos/"
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY")
        self.timeout = 30
        self.max_resolution = 1440
        self.page = 1
        self.per_page = 20
        self.downloads_dir = "/tmp/"
        self.trace_id = str(uuid.uuid4())
        self.log_path = log_path
        logging.basicConfig(
            filename=self.log_path, format=f'%(asctime)s | %(levelname)s | {self.trace_id} | %(message)s', level=logging.INFO)
        # self.media_cache_dir = "/tmp/"
        # self.media_cache = MediaCache(self.media_cache_dir)

    def _check_env(self, key):
        # check if required environment variable is set
        if not os.environ.get(key):
            return False

        return True

    def _get_video_by_id(self, id):
        url = f"{self.pexels_api_url}videos/{id}"
        headers = {"Authorization": self.pexels_api_key}
        try:
            result = requests.get(url, headers=headers, timeout=self.timeout)
        except Exception as e:
            logging.warning(f"Error: unable to get video from video id")
            logging.error(f"{e}")
            exit()
        return result.text

    def _check_and_create_dir(self, dir):
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
            except Exception as e:
                logging.warning(
                    f"Unable to create required downloads directory: {dir}")
                logging.error(f"{e}")
                exit()
        return True

    def _download_video(self, video_url, downloads_dir, filename):
        self._check_and_create_dir(downloads_dir)
        try:
            r = requests.get(video_url, allow_redirects=True,
                             timeout=self.timeout)
        except Exception as e:
            logging.warning(f"Error: Unable to download video : {video_url}")
            logging.error(f"{e}")
            exit()

        open(os.path.join(downloads_dir, filename), 'wb').write(r.content)

        return os.path.join(downloads_dir, filename)

    def _select_video_type(self, video_data, req_resolution):
        # selects required resolution from various available resolutions
        if "video_files" not in video_data:
            logging.error(
                f"Error: Unexpected response when getting data from: {video_data}")
            exit()

        selected_video = {}
        highest_res = 0
        highest_res_selected = {}
        for video in video_data['video_files']:
            if video['height'] == req_resolution and "mp4" in video['file_type']:
                selected_video = video

            if video['height'] is not None and video['height'] > highest_res and "mp4" in video['file_type'] and video['height'] <= self.max_resolution:
                highest_res = video['height']
                highest_res_selected = video

        if not selected_video:
            # if no video with required resolution, then download highest resolution
            selected_video = highest_res_selected

        return selected_video

    def get_id_from_url(self, pexels_url):
        id = pexels_url.split("-")[-1].replace("/", "")

        if len(id) < 3 or len(id) > 10:
            logging.error(
                f"rror: unable to get valid id from url {pexels_url}")
            exit()
        return id

    def _run(self, id):
        try:
            video_data = json.loads(self._get_video_by_id(id))
        except Exception as e:
            logging.warning(f"Error: returned video data not in json format")
            logging.error(f"{e}")
            exit()

        logging.info(
            f"{self.trace_id} | got response from pexels : "+json.dumps(video_data))

        selected_video = self._select_video_type(
            video_data, self.resolution_width)
        logging.info(f"{self.trace_id} | selected video : " +
                     json.dumps(selected_video))

        if not selected_video:
            logging.info(f"{video_data}")
            logging.error(f"Unable to get required file, some error")
            exit()

        self._download_video(selected_video['link'], self.downloads_dir, f"{video_data['id']}.mp4")

        return selected_video['link']

    def download(self, pexels_id):
        # public function, to be called from
        if not self._check_env("PEXELS_API_KEY"):
            logging.error(
                f"Error: required Pexels API key is not set in environment variable")
            exit()

        logging.info(f"{self.trace_id} | got url: {pexels_id}")
        return self._run(pexels_id)

    def search_video(self, query):
        ''' search the video from pexels according to keyword '''
        cache_name = hashlib.md5(query.encode()).hexdigest()+"video"
        search_result = ''
        # search_result = self._search_from_cache(cache_name)

        if not search_result:
            logging.info("data not found in cache, making request to api")
            search_result = self._search_from_pexels(query, cache_name)
        else:
            logging.info("returning result from cache")

        if "videos" not in search_result or len(search_result['videos']) < 1:
            return False

        # randomly select video from search result until mateched requirement
        selected_video_data = {}
        for i in range(0, 9):
            index = random.randint(0, len(search_result['videos'])-1)
            selected_video = self._select_video_type(
                search_result['videos'][index], self.resolution_width)
            if selected_video:
                selected_video_data = search_result['videos'][index]
                break

        return search_result

    # def _search_from_cache(self, cache_name):
    #     result = ""
    #     try:
    #         result = self.media_cache.get(cache_name)
    #     except Exception as e:
    #         logging.warning(
    #             f"Error: Unable to search cache for video : {cache_name}")
    #         logging.error(f"{e}")

        return result

    def _search_from_pexels(self, query, cache_name):
        search_result = {}
        try:
            # Public endpoint to search the video
            search_result_raw = self._video_search_request(query)

            search_result = json.loads(search_result_raw)
            # save the file in cache for next access
            # self.media_cache.save(search_result, cache_name)
            logging.info("data saved to cache")
        except Exception as e:
            logging.warning(f"Error: Unable to search video : {query}")
            logging.error(f"{e}")
            exit()

        return search_result

    def _video_search_request(self, query):
        # request the pexels APi for video
        url = f"{self.pexels_api_url}search/?query={query}&per_page={self.per_page}&page={self.page}&orientation=landscape&size=medium"
        headers = {"Authorization": self.pexels_api_key}

        try:
            result = requests.get(url, headers=headers, timeout=self.timeout)
        except Exception as e:
            logging.warning(f"Error: unable to get video from video id")
            logging.error(f"{e}")
            exit()
        return result.text