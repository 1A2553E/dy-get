from moviepy.editor import *
from os import chdir, getcwd, mkdir
from random import randint
import sys
import requests

from concurrent.futures import ThreadPoolExecutor
from requests import get, head
import time


class downloader:
    def __init__(self, url, num, name):
        self.url = url
        self.num = num
        self.name = name
        self.getsize = 0
        r = head(self.url, allow_redirects=True)
        self.size = int(r.headers['Content-Length'])

    def down(self, start, end, chunk_size=10240):
        headers = {'range': f'bytes={start}-{end}'}
        r = get(self.url, headers=headers, stream=True)
        with open(self.name, "rb+") as f:
            f.seek(start)
            for chunk in r.iter_content(chunk_size):
                f.write(chunk)
                self.getsize += chunk_size

    def main(self):
        start_time = time.time()
        f = open(self.name, 'wb')
        f.truncate(self.size)
        f.close()
        tp = ThreadPoolExecutor(max_workers=self.num)
        futures = []
        start = 0
        for i in range(self.num):
            end = int((i+1)/self.num*self.size)
            future = tp.submit(self.down, start, end)
            futures.append(future)
            start = end+1
        while True:
            process = self.getsize/self.size*100
            last = self.getsize
            time.sleep(1)
            curr = self.getsize
            down = (curr-last)/1024
            if down > 1024:
                speed = f'{down/1024:6.2f}MB/s'
            else:
                speed = f'{down:6.2f}KB/s'
            print(f'process: {process:6.2f}% | speed: {speed}', end='\r')
            if process >= 100:
                print(f'process: {100.00:6}% | speed:  00.00KB/s', end=' | ')
                break
        tp.shutdown()
        end_time = time.time()
        total_time = end_time-start_time
        average_speed = self.size/total_time/1024/1024
        print(
            f'total-time: {total_time:.0f}s | average-speed: {average_speed:.2f}MB/s')


DOWNMUSIC = True
url = input("url:")
video_id = url.split("/")  # 切割链接，获取视频id
# 获得视频id 例如https://www.douyin.com/video/7058986650088607012
video_id = video_id[len(video_id)-1]
try:
    int(video_id)
except:
    print("dy-get [error] 获取video_id失败!")
    sys.exit(1)
response = requests.get('https://www.douyin.com/web/api/v2/aweme/iteminfo/?item_ids='+str(video_id),
                        headers='')  # 可填入自己的headers
try:
    video_json = response.json()  # 读取json
except:
    print("dy-get [error] 获取json失败!")
    sys.exit(1)
try:
    get_id = video_json["item_list"][0]["video"]["vid"]
except:
    print("dy-get [error] 获取vid失败!")
    sys.exit(1)
picture = video_json["item_list"][0]["video"]["ratio"]
width = video_json["item_list"][0]["video"]["width"]
height = video_json["item_list"][0]["video"]["height"]
music_url = video_json["item_list"][0]["music"]["play_url"]["uri"]


url = "https://aweme.snssdk.com/aweme/v1/play/?video_id="+get_id+"&line=0"
response = requests.get(url,
                        headers='')  # 可填入自己的headers
url = response.url
random_value = str(int(time.time()))
mkdir(str(get_id)+"_"+random_value)
chdir(str(get_id)+"_"+random_value)
mkdir("video")
chdir("video")

save = str(get_id)+".mp4"
down = downloader(url, 12, save)
down.main()


chdir("../")

mkdir("music")
chdir("music")
url = music_url
response = requests.get(url,
                        headers='')  # 可填入自己的headers
url = response.url
save = str(get_id)+".mp3"
down = downloader(url, 12, save)
down.main()


chdir("../")
chdir("video")


old_video = get_id+".mp4"
new_video = get_id+"_nosound.mp4"

video = VideoFileClip(old_video)
video = video.without_audio()  # 删除声音，返回新的视频对象，原有对象不更改
video.write_videofile(new_video)
