import sqlite3
import re
import urllib3
from bs4 import BeautifulSoup
import datetime
import sys
import wikipediaapi

def wiki_crawler(target):
    wiki_wiki = wikipediaapi.Wikipedia('zh-tw')
    page_py = wiki_wiki.page(target)
    print(page_py.title)
    print(page_py.summary)

if __name__ == "__main__":
    wiki_crawler("Nicki Minaj")