import os
import requests
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys


class synapse:
    def __init__(self):
        self.url = "https://www.twitch.tv/directory/game/League%20of%20Legends/clips?range=7d"
        self.card_xpath = "//a[@data-a-target='preview-card-image-link']"
        self.video_xpath = "//video[@src]"
        self.clips, self.videos = [], []
        with open("blacklist.txt", "r") as f:
            self.blacklist = [x.strip().lower() for x in f.readlines()]

        self.main()

    def get_clips(self, driver):
        driver.get(self.url)
        cards = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.card_xpath))
        )
        while len(self.clips) < 100:
            cards.send_keys(Keys.END)
            self.clips = [clip.get_attribute(
                "href") for clip in driver.find_elements(By.XPATH, self.card_xpath)]

    def get_videos(self, driver):
        for clip in self.clips:
            if clip.split("/")[-3] not in self.blacklist:
                driver.get(clip)
                video = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, self.video_xpath)))
                self.videos.append({"url": video.get_attribute("src"),
                                    "creator": clip.split("/")[-3], })

    def download_videos(self):
        i = 0
        for video in self.videos:
            i += 1
            print(
                f"Downloading video {i}/{len(self.videos)} from: {video['creator']}")
            r = requests.get(video["url"], stream=True)
            with open(f"videos/{video['creator']}_{i}.mp4", "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()

    def make_montage(self):
        input("remove unwanted videos. press enter to continue")
        videos = os.listdir("videos")
        random.shuffle(videos)
        with open("videos.txt", "w") as f:
            for v in videos:
                os.system(
                    f'ffmpeg -i videos/{v} -c copy -bsf:v h264_mp4toannexb -f mpegts clean/{v.split(".")[0]}.ts')
                f.write(f"file 'clean/{v.split('.')[0]}.ts'\n")
        os.system('ffmpeg -f concat -i videos.txt -c copy output.mkv')

    def clear_videos(self):
        for v in os.listdir("videos"):
            os.remove(f"videos/{v}")
            os.remove(f"clean/{v.split('.')[0]}.ts")

    def main(self):
        opts = Options()
        opts.headless = True
        with webdriver.Firefox() as driver:
            self.wait = WebDriverWait(driver, 20)
            self.get_clips(driver)
            self.get_videos(driver)
        self.download_videos()
        self.make_montage()
        self.clear_videos()


if __name__ == "__main__":
    synapse()
