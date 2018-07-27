import urllib3
from bs4 import BeautifulSoup
import os
import re
import json
import datetime
import time
import sys
sys.path.append("../")
import multiprocessing as mp
from crawlerhelpers import *
from languagecodeclasses import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def qqmusic_crawler(date, target='song', cate=Region.cn, date_format='%Y%m%d', wait_time=2):
    """
    --main mymusic webpage crawler--
    function parameters can be selected from the website
    :param str date: date to be crawled
    :param str target: ranked by song / album / singer
    :param int cate: language code, refer to Language enum class
    :return: None
    """
    # week_of_year = date.isocalendar()[1] if date.isocalendar()[1] != 52 else 0
    qqmusic_page = 'https://y.qq.com/n/yqq/toplist/5.html#t1={}&t2={}&t3=song'.format(
        date.year, date.isocalendar()[1])
    print(date.strftime('%Y-%m-%d') + " " + str(date.isocalendar()[1]))

    driver = webdriver.Firefox()
    driver.get(qqmusic_page)
    delay = wait_time

    # the loop that crawl page 1 to 4
    # moved ranking here, so it's accessible by the file generating
    ranking = []
    for pageNum in range (1,5,1):

        for _ in range(100):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'js_song')))
            print("Page is ready!")
        except TimeoutException:
            print("Loading took too much time!")
        raw_data = driver.page_source.encode('utf-8')

        # print(len(raw_data))

        soup = BeautifulSoup(raw_data, 'html.parser')
        pattern_script = re.compile(r'require.resourceMap\((.*)\)')
        pattern_url = re.compile(r'\"url\":\"(.*?)\",')
        row_data = soup.find_all('li', attrs={'class': None})

        # ranking = []

        print(len(row_data))

        for i in range(0, len(row_data)):
            singers = row_data[i].find_all('a', attrs={'class': 'singer_name'})
            songs = row_data[i].find_all('a', attrs={'class': 'js_song'})
            all_singer = ""
            for singer in singers:
                all_singer += singer.text + '、'
            ranking.append({'artist_name': all_singer, 'song_name': songs[0].text, 'album_name': ''})

        # click the next page
        if pageNum < 4:
            driver.find_element_by_link_text(str(pageNum + 1)).click()
        else: break

    # save the raw data to corresponding directory
    full_path = os.path.join('data', target, 'ranking_{}_{}.json'.format(cate.name, date.strftime('%Y-%m-%d')))
    with open(full_path, 'w') as outfile:
        json.dump(ranking, outfile, ensure_ascii=False)
    driver.quit()
    return ranking




if __name__ == "__main__":
    # data crawled from 2013-1-1 week 1
    start_date = datetime.datetime(2013, 1, 1)
    end_date = datetime.datetime(2013, 2, 1)
    languages = [Region.cn]
    main_crawler(start_date, end_date, crawler=qqmusic_crawler, cate=languages,
                 data_sorting=True, force_crawl=True, get_raw_data=False, date_format='%Y%m%d')
