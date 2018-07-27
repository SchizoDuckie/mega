import wikipedia
import urllib3
import wikipediaapi
from bs4 import BeautifulSoup
from hanziconv import HanziConv
import re
import time
from letterMatcher import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


TO_THE_END = 87


def wiki_crawler(target, lang="zh-tw", wait_time=3):
    wikipedia.set_lang(lang)
    try:
        page_data = wikipedia.page(target)
        if match_pattern(target, dic['zh_en_num']):
            zh_name = target
        else:
            zh_name = page_data.title
    except wikipedia.exceptions.PageError or ValueError:
        print("{} not found!".format(target))
        print()
        return (target, "", "")
    except wikipedia.exceptions.DisambiguationError:
        print("{} ambiguous!".format(target))
        print()
        return (target, "", "")

    print("loading page...")
    print(page_data.url)
    page_url = page_data.url

    # wiki_wiki = wikipediaapi.Wikipedia(lang)
    # page_py = wiki_wiki.page(target)
    #
    # if page_py.exists():
    #     page_data = page_py
    #     page_url = page_py.fullurl
    #     if match_pattern(target, dic['zh_en_num']):
    #         zh_name = target
    # else:
    #     answer = input("save this data? (Y/n)")
    #     to_the_end = (answer == "end")
    #     if to_the_end:
    #         return TO_THE_END
    #
    #     print("{} not found!".format(target))
    #     print()
    #     return (target, "", "")
    # eng_title = soup.find('li', attrs={'class':'interlanguage-link interwiki-en'}).a['title']

    target_temp = target.replace("*", "")
    target_temp = target_temp.replace("+", "")
    target_reg = re.compile(".{0,30}".join(target_temp.lower().split(" ")))

    if not HanziConv.same(target, page_data.title) \
            and target not in page_data.title \
            and page_data.title not in target \
            and target not in page_data.summary \
            and not len(target_reg.findall(page_data.summary.lower())):
        print("this target: {}".format(target))
        print("wiki target: {}".format(page_data.title))
        print(page_data.summary)
        answer = input("save this data? (Y/n)")
        # answer = "n"
        throw_this = (answer == "n")
        to_the_end = (answer == "end")
        if throw_this:
            print("{} unchanged!".format(target))
            print()
            return (target, "", "")
        if to_the_end:
            print("to the end!")
            print()
            return TO_THE_END
    else:
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("intl.accept_languages", lang)
        firefox_profile.update_preferences()
        driver = webdriver.Firefox(firefox_profile=firefox_profile)
        driver.get(page_url)
        html_data = driver.page_source.encode('utf-8')
        driver.close()

        soup = BeautifulSoup(html_data, 'html.parser')

        zh_names = soup.find('h1', attrs={'id': 'firstHeading'})
        eng_names = soup.findAll('span', attrs={'class': 'nickname'})
        nick_names = soup.find('td', attrs={'class': 'nickname'})
        english_link_name = soup.find('a', attrs={'lang': 'en', 'hreflang': 'en'})

        zh_name = zh_names.text.replace("[編輯]", "")
        if not match_pattern(zh_name, dic["zh_en_num"]):
            zh_name = target
        eng_name = ""
        nick_name = ""

        if eng_names:
            try:
                eng_name = eng_names[1].text.strip()
            except:
                eng_name = eng_names[0].text.strip()

        if not match_pattern(eng_name, dic["en"]):
            eng_name = ""
            if english_link_name:
                eng_name = english_link_name.get('title')
                eng_name = eng_name.split("–")[0].strip()

        if nick_names:
            print(nick_names)
            pattern = r'\[\d+\]'
            nick_name = nick_names.get_text("\n").strip()
            nick_name = nick_name.replace("、", ",")
            nick_name = nick_name.replace("\n", ",")
            nick_name = re.sub(pattern, "", nick_name)
            nick_name_temp = nick_name.split(",")
            for i in range(0, len(nick_name_temp)):
                if nick_name_temp[i] == target:
                    nick_name_temp[i] = ""
                nick_name_temp[i] = nick_name_temp[i].strip()
            nick_name_temp[:] = [item for item in nick_name_temp if item != '']
            nick_name = ",".join(nick_name_temp)

        print("printing info:")
        print(zh_name)
        print(eng_name)
        print(nick_name)
        print()

        return (zh_name, eng_name, nick_name)

if __name__ == "__main__":
    data_inputs = ['楊錦聰', '糯米糰', '譚艷', '那我懂你意思了', '郁可唯', '羅時豐', '陳勢安', '魏如萱']
    for singer in data_inputs:
        wiki_crawler(singer)