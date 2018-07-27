import urllib3
from bs4 import BeautifulSoup
import os
import re
import json
import sys
sys.path.append("../")
import multiprocessing as mp
import datetime
from crawlerhelpers import *
from languagecodeclasses import *


def kkbox_crawler(date, target='song', cate=Language.ZH_TW, date_format='%Y-%m-%d'):
    """
    --main kkbox webpage crawler--
    function parameters can be selected from the website
    :param str date: date to be crawled
    :param str target: ranked by song / album / singer
    :param int cate: language code, refer to Language enum class
    :return: None
    """

    kkbox_page = 'https://kma.kkbox.com/charts/daily/song'
    http = urllib3.PoolManager()
    this_date = date.strftime(date_format)
    fields = {'date': this_date, 'cate': cate}
    try:
        page = http.request('GET', kkbox_page, fields=fields)
    except urllib3.error.HTTPError as e:
        print(e)
        sys.exit(1)

    soup = BeautifulSoup(page.data, 'html.parser')
    pattern_date = re.compile(r'var\schartDate\s=\s"\d{4}-\d{2}-\d{2}";')
    pattern_ranking = re.compile(r'var\schart\s=\s(\[.*\]);')
    script = soup.find('script', text=pattern_date)
    data = pattern_ranking.search(script.text).group(1)
    ranking = json.loads(data)

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
    start_date = datetime.datetime(2005, 9, 28)
    end_date = datetime.datetime(2018, 3, 1)
    languages_selected = [Language.ZH_TW, Language.TW, Language.EN, Language.JA]
    processes = [mp.Process(target=main_crawler,
                            kwargs={'start_date': start_date, 'end_date': end_date,'crawler': kkbox_crawler,
                                    'force_crawl': False, 'date_format': '%Y-%m-%d',
                                    'cate': [language]}) for language in languages_selected]
    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print("completed!")


if __name__ == "__main__":
    # multi_crawler()
    start_date1 = datetime.datetime(2011, 1, 1)
    languages1 = [Language.KO, Language.ZH_HK]

    start_date2 = datetime.datetime(2005, 9, 28)
    languages2 = [Language.ZH_TW, Language.TW, Language.EN, Language.JA]

    end_date = datetime.datetime(2018, 3, 1)

    main_crawler(start_date1, end_date, crawler=kkbox_crawler, cate=languages1,
                 data_sorting=True, force_crawl=False, get_raw_data=False, date_format='%Y-%m-%d')