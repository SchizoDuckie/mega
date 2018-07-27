#!./ENV/bin python
# -*- coding: utf-8 -*-

'''
clean.py
- This script cleans the given .csv file.

Written by: Alex Wong
Date: Mar 26, 2018
'''

import collections
import regex


en_pattern = regex.compile(u'([a-zA-Z]+)', regex.UNICODE)
zh_pattern = regex.compile(u'([\p{IsHan}]+)', regex.UNICODE)
jp_pattern = regex.compile(u'([\p{IsHira}\p{IsKatakana}]+)', regex.UNICODE)
kr_pattern = regex.compile(u'([\p{IsHangul}]+)', regex.UNICODE)
num_pattern = regex.compile(u'([0-9]+)', regex.UNICODE)
bopo_pattern = regex.compile(u'[\p{IsBopo}]', regex.UNICODE)
patterns = [en_pattern, zh_pattern, jp_pattern, kr_pattern, num_pattern, bopo_pattern]

dic = collections.defaultdict(list)
dic['zh'] = [False, True, False, False, False, False]  # zh
dic['zh_num'] = [False, True, False, False, None, False]  # zh, nums
dic['en'] = [True, False, False, False, None, False]  # en, {nums}
dic['jp'] = [None, False, True, False, None, False]  # jp, {nums}
dic['kr'] = [None, False, False, True, None, False]  # kr, {nums}
dic['zh_en_num'] = [None, True, False, False, None, False]
dic['all'] = [None, None, False, False, None, None]

def match_pattern(data, dict_code):
    """
    Check data to match all the patterns.
    :param data: string
    :param patterns: list of regex.compile patterns
    :param founds: list of booleans/None. True: exist, False: not exist, None: optional
    :return: boolean
    """
    for i in range(len(patterns)):
        if dict_code[i] is None:
            continue
        elif dict_code[i] != (patterns[i].search(data) is not None):
            return False
    return True

def pattern_worker(data_input, codes):
    """
    Check data to match all the patterns.
    :param data_inputs: string array
    :param codes: list of {'zh' | 'zh_num' | 'en' | 'jp' | 'kr'}
    :return: void
    """
    answer = False
    for code in codes:
        answer = (answer or match_pattern(data_input, dic[code]))
    return answer

if __name__ == "__main__":
    nick_name = "Christian Bale – 英文"
    print(nick_name.split("–")[0].strip())