import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from collections import defaultdict
import pymongo
import sqlite3

#client = pymongo.MongoClient(connect = False)
#db = client.youtube
db = sqlite3.connect('./yt-captions.db')

def pull_transcript(youtube_watch_link, youtube_id):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    browser = webdriver.Chrome("./chromedriver.exe", chrome_options=options)
    browser.get('{}'.format(youtube_watch_link))

    try:
        element = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='More actions']")))
        element.click()
    except:
        print("Not aria-label=more actions.. trying aria-label=action menu")
        try:
            element = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Action menu.']")))
            element.click()
        except Exception as e:
            print(e+" : Do something usefull in your life.")
    try:
        elemz = browser.find_element_by_xpath("//yt-formatted-string[@class = 'style-scope ytd-menu-service-item-renderer']")
        elemz.click()
    except Exception as e:
        print("I think there are no subtitles/captions avaliable.")
        print(e)

    time.sleep(5)
    try:
        htmlSource = browser.page_source
        soup = BeautifulSoup(htmlSource, 'lxml')
        parents = soup.findAll("div",{"class":"cue-group style-scope ytd-transcript-body-renderer"})
        records = []
        captions_dict = defaultdict(list)

        for parent in parents:
            time_stamp = parent.text.strip()[0:5]
            caption = parent.text.strip()[5:]
            records.append((time_stamp.strip(), caption.strip()))

            words = caption.strip().split()

            for word in words:
                word = word.replace(".", "")
                word = word.replace("(", "")
                word = word.replace(")", "")
                word = word.replace(",", "")
                word = word.replace("!", "")
                word = word.encode('ascii', 'ignore').decode('ascii')
                captions_dict[word.lower()].append(time_stamp)

        df = pd.DataFrame(records, columns = ['time_stamp', 'caption'])

        lastrowtime = df['time_stamp'].iloc[-1]
        print(lastrowtime)
        # new_cache = {
        #     "url" : youtube_id,
        #     "lasttimestamp" : lastrowtime,
        #     "captionsd" : dict(captions_dict)
        # }
        # db.cached.insert(new_cache, check_keys = False)
        db.execute('''INSERT INTO youtube values(?,?,?)''', (youtube_id, lastrowtime, str(dict(captions_dict))))
        browser.quit()

    except Exception as e:
        browser.quit()
        print('Trolololol')
        lastrowtime = ""
        normaldict = {".":"[00:00]"}
        # new_cache = {
        #     "url" : youtube_id,
        #     "lasttimestamp" : lastrowtime,
        #     "captionsd" : normaldict
        # }
        # db.cached.insert(new_cache, check_keys = False)
        db.execute('''INSERT INTO youtube values(?,?,?)''', (youtube_id, lastrowtime, str(dict(captions_dict))))

        return "No"

    print('Appending to db')
    db.commit()


if __name__ == "__main__":
    pull_transcript('https://www.youtube.com/watch?v=bukzXzsG77o','bukzXzsG77o')
