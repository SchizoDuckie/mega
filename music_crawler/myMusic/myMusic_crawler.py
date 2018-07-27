import urllib3
from bs4 import BeautifulSoup
import os
import re
import json
import datetime
import sys
sys.path.append("../")
import multiprocessing as mp
from crawlerhelpers import *
from languagecodeclasses import *


def mymusic_crawler(date, target='song', cate=Category.ZH_TW, date_format='%Y%m%d'):
    """
    --main mymusic webpage crawler--
    function parameters can be selected from the website
    :param str date: date to be crawled
    :param str target: ranked by song / album / singer
    :param int cate: language code, refer to Language enum class
    :return: None
    """

    mymusic_page = 'https://www.mymusic.net.tw/board/dailySong'
    http = urllib3.PoolManager()
    this_date = date.strftime(date_format)
    fields = {'date': this_date, 'musicType': cate, 'cmd': 'ezpc'}
    try:
        page = http.request('GET', mymusic_page, fields=fields)
    except urllib3.error.HTTPError as e:
        print(e)
        sys.exit(1)

    soup = BeautifulSoup(page.data, 'html.parser')
    pattern_singer = re.compile('.*/singer/show/.*')
    pattern_song = re.compile('.*/song/show/.*')
    # singers = soup.findAll('a', attrs={'href': pattern_singer})
    songs = soup.findAll('td', attrs={'class': 'song'})
    ranking = []

    for i in range(0, len(songs)):
        raw_data = songs[i].text.strip()
        pattern_spliter = re.compile('(.*)[\n\t\r]+(.*)')
        song_name = pattern_spliter.search(raw_data).group(1)
        singer_name = pattern_spliter.search(raw_data).group(2)
        ranking.append({'artist_name': singer_name, 'song_name': song_name, 'album_name': ''})

    # save the raw data to corresponding directory
    full_path = os.path.join('data', target, 'ranking_{}_{}.json'.format(cate.name, date.strftime('%Y-%m-%d')))
    with open(full_path, 'w') as outfile:
        json.dump(ranking, outfile, ensure_ascii=False)

    return ranking


def multi_crawler():
    """
    implement multiprocess so the crawler can run in parallel
    :return: None
    """
    start_date = datetime.datetime(2018, 1, 1)
    end_date = datetime.datetime(2018, 3, 1)
    languages_selected = [Category.ZH_TW, Category.KO_JA, Category.TW, Category.ZH_HK]
    processes = [mp.Process(target=main_crawler,
                            kwargs={'start_date': start_date, 'end_date': end_date, 'crawler': mymusic_crawler,
                                    'force_crawl': False, 'date_format': '%Y%m%d',
                                    'cate': [language]}) for language in languages_selected]
    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print("completed!")


if __name__ == "__main__":
    # multi_crawler()
    start_date = datetime.datetime(2011, 1, 1)
    end_date = datetime.datetime(2018, 3, 1)
    languages = [Category.ZH_TW, Category.KO_JA, Category.TW, Category.ZH_HK]
    main_crawler(start_date, end_date, crawler=mymusic_crawler, cate=languages,
                 data_sorting=True, force_crawl=False, get_raw_data=False, date_format='%Y%m%d')