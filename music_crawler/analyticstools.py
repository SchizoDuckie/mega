#encoding=utf-8
import os
from collections import Counter
import math
import datetime
from crawlerhelpers import *
from languagecodeclasses import *
from openpyxl import *
import openpyxl.styles.colors
import regex
import itertools
from crawlerhelpers import *
import jieba
from letterMatcher import *

def counter_cosine_similarity(c1, c2):
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    return dotprod / (magA * magB)


def checking_duplicate():
    kkbox_path = os.path.join('kkbox', 'data', 'results')
    mymusic_path = os.path.join('myMusic', 'data', 'results')
    spotify_path = os.path.join('spotify', 'data', 'results')
    cathy_singers_data_path = os.path.join('data_manual_clean', 'singers_union.txt')
    cathy_songs_data_path = os.path.join('data_manual_clean', 'songs_union.txt')
    cathy_pairs_data_path = os.path.join('data_manual_clean', 'pairs_union.txt')

    singer_path = 'singers_ALL_2011-01-01_2018-03-01'
    singer_path_s = 'singers_ALL_2017-01-01_2018-03-01'

    song_path = 'songs_ALL_2011-01-01_2018-03-01'
    song_path_s = 'songs_ALL_2017-01-01_2018-03-01'

    singer_song_pair_path = 'singer_song_pairs_ALL_2011-01-01_2018-03-01'
    singer_song_pair_path_s = 'singer_song_pairs_ALL_2017-01-01_2018-03-01'

    with open(cathy_singers_data_path) as data:
        cathy_singers = Counter(data.read().splitlines())
    with open(os.path.join(kkbox_path, singer_path)) as data:
        kkbox_singers = Counter(data.read().splitlines())
    with open(os.path.join(mymusic_path, singer_path)) as data:
        mymusic_singers = Counter(data.read().splitlines())
    with open(os.path.join(spotify_path, singer_path_s)) as data:
        spotify_singers = Counter(data.read().splitlines())

    with open(cathy_songs_data_path) as data:
        cathy_songs = Counter(data.read().splitlines())
    with open(os.path.join(kkbox_path, song_path)) as data:
        kkbox_songs = Counter(data.read().splitlines())
    with open(os.path.join(mymusic_path, song_path)) as data:
        mymusic_songs = Counter(data.read().splitlines())
    with open(os.path.join(spotify_path, song_path_s)) as data:
        spotify_songs = Counter(data.read().splitlines())

    with open(cathy_pairs_data_path) as data:
        cathy_singer_song_pairs = Counter(data.read().splitlines())
    with open(os.path.join(kkbox_path, singer_song_pair_path)) as data:
        kkbox_singer_song_pairs = Counter(data.read().splitlines())
    with open(os.path.join(mymusic_path, singer_song_pair_path)) as data:
        mymusic_singer_song_pairs = Counter(data.read().splitlines())
    with open(os.path.join(spotify_path, singer_song_pair_path_s)) as data:
        spotify_singer_song_pairs = Counter(data.read().splitlines())

    all_singers = []
    all_singers_set = list(set(mymusic_singers) | set(kkbox_singers) | set(spotify_singers) | set(cathy_singers))
    temp_singers = []
    singer_dup_count = 0
    for singer in all_singers_set:
        if len(singer) == 0:
            continue
        temp_singers.append(singer)
        keep_this = True

        # if singer.lower() not in all_singers and singer != "":
        #     for j in range(0, len(temp_singers)):
        #         if (temp_singers[j] in singer or singer in temp_singers[j]) and len(singer) != len(temp_singers[j]):
        #             print("singer_stored: {}".format(temp_singers[j]))
        #             keep_this = False
        #
        #     if not keep_this:
        #         print("-----current entry-----")
        #         print("singer_now: {}".format(singer))
        #         answer = input("wanna keep this data? (Y/n)")
        #         keep_this = (answer == "y" or answer == "")
        #         if answer == "gg":
        #             break
        #         print("")
        # else:
        #     singer_dup_count += 1
        #     keep_this = False

        if keep_this:
            all_singers.append(singer.lower())

    all_songs = []
    temp_songs = []
    all_songs_set = list(set(mymusic_songs) | set(kkbox_songs) | set(spotify_songs) | set(cathy_songs))
    song_dup_count = 0
    for song in all_songs_set:
        if len(song) == 0:
            continue
        temp_songs.append(song)
        keep_this = True

        # if song.lower() not in all_songs and song != "":
        #     for j in range(0, len(temp_songs)):
        #         if (temp_songs[j] in song or song in temp_songs[j]) and len(song) != len(temp_songs[j]):
        #             print("song_stored: {}".format(temp_songs[j]))
        #             keep_this = False
        #
        #     if not keep_this:
        #         print("-----current entry-----")
        #         print("song_now: {}".format(song))
        #         answer = input("wanna keep this data? (Y/n)")
        #         keep_this = (answer == "y" or answer == "")
        #         if answer == "gg":
        #             break
        #         print("")
        # else:
        #     song_dup_count += 1
        #     keep_this = False

        if keep_this:
            all_songs.append(song.lower())

    all_pairs = []
    temp_singers = []
    temp_songs = []
    all_pairs_set = list(set(mymusic_singer_song_pairs) | set(kkbox_singer_song_pairs) |
                         set(spotify_singer_song_pairs) | set(cathy_singer_song_pairs))
    pair_dup_count = 0
    counter = 0
    global this_pair
    for i in range(0, len(all_pairs_set)):
        this_pair = all_pairs_set[i].replace("\t\t", "\t")
        if len(this_pair) == 0:
            continue
        singer = this_pair.lower().split("\t")[0]
        temp_singers.append(singer)
        song = this_pair.lower().split("\t")[1]
        temp_songs.append(song)
        keep_this = True
        replace_this = False
        final_pair = []
        final_pair.append(this_pair)
        selection = 0

        if this_pair.lower() not in all_pairs and this_pair != "":
            for j in range(0, len(temp_songs)):
                if temp_songs[j] == song and \
                        ((temp_singers[j] in singer or singer in temp_singers[j]) and
                         len(temp_singers[j]) != len(singer)):
                    print("")
                    print("#{}: singer = {}, song = {}".format(len(final_pair),
                                                               temp_singers[j], song))
                    final_pair.append(temp_singers[j] + "\t" + song)
                    keep_this = False

            if not keep_this:
                print("-----current entry-----")
                print("#{}: singer = {}, song = {}".format(len(final_pair), singer, song))
                answer = input("wanna keep this data? (Y/n)")
                answer = ""
                keep_this = (answer != "n")
                range_list = []
                for k in range(1, len(final_pair)):
                    range_list.append(str(k))
                if answer == "gg":
                    break
                elif answer in range_list:
                    keep_this = False
                    replace_this = True
                    selection = int(answer)
                else:
                    keep_this = False
                    replace_this = False
                print("")
                counter += 1
        else:
            pair_dup_count += 1
            keep_this = False

        if keep_this:
            all_pairs.append(this_pair.lower())
        elif replace_this:
            if final_pair[selection].lower() not in all_pairs:
                all_pairs.append(this_pair.lower())
            else:
                all_pairs[all_pairs.index(final_pair[selection].lower())] = this_pair.lower()

    paths = ['data_manual_clean', 'results']
    start_date = datetime.datetime(2011, 1, 1)
    end_date = datetime.datetime(2018, 3, 1)
    file_writer(Language.ALL, start_date, end_date, all_singers, all_songs, [], all_pairs, paths)

    print("singer_dup_count: {}".format(singer_dup_count))
    print("song_dup_count: {}".format(song_dup_count))
    print("pair_dup_count: {}".format(pair_dup_count))

    # count_singers = len(list(((set(kkbox_singers) | set(spotify_singers)) & set(cathy_singers))))
    # count_songs = len(list((set(kkbox_songs) & set(mymusic_songs))))
    # count_singer_song_pairs = len(list((set(kkbox_singer_song_pairs) & set(mymusic_singer_song_pairs))))

    # print(counter_cosine_similarity(kkbox_singers, mymusic_singers))
    # print(counter_cosine_similarity(kkbox_songs, mymusic_songs))
    # print(counter_cosine_similarity(kkbox_singer_song_pairs, mymusic_singer_song_pairs))


def count_duplicate(lan_codes=['zh'], DEBUG_MODE=False):
    file_input = 'zh_TW_feed_artist_051618.xlsx'
    print("file input: {}\n".format(file_input))
    data_tw_mega_path = os.path.join('data_manual_clean', 'mega_data', file_input)
    singer_path = 'singers_ALL_2011-01-01_2018-03-01'
    data_all_singer = os.path.join('data_manual_clean', 'results_cleaning', singer_path)

    loc_path = os.path.join('data_manual_clean', 'Lexicon_fix', 'zh_TW_singer_lex_all')

    with open(data_all_singer) as data:
        temp_singers = Counter(data.read().splitlines())

    with open(loc_path) as data:
        LEX_data = data.readlines()

    for i in range(0, len(LEX_data)):
        LEX_data[i] = LEX_data[i].split(" ")[0]

    all_singers_from_data = list(set(temp_singers))

    mega_inputs = []
    wb = load_workbook(data_tw_mega_path)
    first_sheet = wb.get_sheet_names()[0]
    worksheet = wb.get_sheet_by_name(first_sheet)

    for row in range(2, worksheet.max_row + 1):
        for column in "B":
            cell_name = "{}{}".format(column, row)
            # the value of this cell: worksheet[cell_name].value
            mega_inputs.append(str(worksheet[cell_name].value).lower())

    for lan_code in lan_codes:
        count_ASR_FAIL_ALL = 0
        count_E2E_FAIL_ALL = 0
        count_ASR_FAIL = 0
        count_E2E_FAIL = 0
        count_Locale = 0
        results1 = []
        results2 = []
        dup = 0
        dict_all = []
        count_LEX_ASR_FAIL = 0
        for index, mega_input in enumerate(mega_inputs):
            # Red: (FF)FF0000; Green: (FF)00FF00
            color = worksheet["{}{}".format('C', index + 2)].fill.start_color.index
            E2E_correctness = (str(worksheet["{}{}".format('G', index + 2)].value) == "PASS")
            ASR_correctness = (color == "FF00FF00")
            if match_pattern(mega_input, dic[lan_code]) and not ASR_correctness:
                if DEBUG_MODE:
                    ASR_utterance = str(worksheet["{}{}".format('C', index + 2)].value)
                    REF_utterancet = str(worksheet["{}{}".format('D', index + 2)].value)
                    ASR_output = str(worksheet["{}{}".format('E', index + 2)].value)
                    REF_output = str(worksheet["{}{}".format('F', index + 2)].value)
                    print('singer: {}'.format(mega_input))
                    print('ASR utterance: {}'.format(ASR_utterance))
                    print('REF utterance: {}'.format(REF_utterancet))
                    print('ASR output: {}'.format(ASR_output))
                    print('REF output: {}'.format(REF_output))
                    print()

                results1.append(mega_input)
                pattern = regex.compile(r'([\p{IsHan}]+)', regex.UNICODE)
                song_trimmed = song_album_trimmer(mega_input, pattern)
                this_song = song_trimmed[0]
                results2.append(this_song)

                count_ASR_FAIL += 1
                # print(mega_input)
                # if not E2E_correctness:
                #     count_ASR_FAIL += 1
                    # print(mega_input)
            # if match_pattern(mega_input, dic[lan_code]) and ASR_correctness:
            #     print(mega_input)

            if match_pattern(mega_input, dic[lan_code]):
                if not E2E_correctness and ASR_correctness:
                    count_E2E_FAIL += 1
                count_Locale += 1
                # print(mega_input)

            if not E2E_correctness:
                count_E2E_FAIL_ALL += 1

            if not ASR_correctness and not E2E_correctness:
                count_ASR_FAIL_ALL += 1
                if mega_input in dict_all:
                    dup += 1

            dict_all.append(mega_input)

            if mega_input in LEX_data and not ASR_correctness:
                count_LEX_ASR_FAIL += 1
                # print(mega_input)

        # print("mega input of {}".format(lan_code))
        # print(results2)
        print("{} all: {}".format(lan_code, count_Locale))
        print("{} ASR FAIL: {}".format(lan_code, count_ASR_FAIL))
        print("{} ASR PASS & E2E FAIL: {}".format(lan_code, count_E2E_FAIL))
        print()

    print("Duplicate data: {}".format(dup))
    print("ALL ASR FAIL: {}".format(count_ASR_FAIL_ALL))
    print("ALL E2E FAIL: {}".format(count_E2E_FAIL_ALL))

    print("LEX ASR FAIL: {}".format(count_LEX_ASR_FAIL))

    # if DEBUG_MODE:
    #     print("original\ttrimmed")
    #     for i in range(0, len(results1)):
    #         print("{}\t{}".format(results2[i], results1[i]))
    #     # print(countB)


def tokenization(sentences):
    jieba.set_dictionary('data_manual_clean/jieba_dict/dict.txt.big.txt')
    for sentence in sentences:
        print("Input：", sentence)
        words = jieba.cut(sentence, cut_all=False)
        print("Output 精確模式 Full Mode：")
        for word in words:
            print(word)
        print()


# data_inputs = ["小白放輕鬆的音樂"]
# tokenization(data_inputs)

# this_dict = {"a": ['1','2'], "b":["3","4"], "c": ["5", "6"]}
# words = "abc"
# input_data = []
#
# for word in words:
#     this_combo = this_dict[word]
#     input_data.append(this_combo)
#
# combos = list(itertools.product(*input_data))
# print(list(combos))

# ['zh', 'en', 'jp', 'kr', 'zh_any']
count_duplicate(lan_codes=['zh', 'en', 'jp', 'kr'])
# checking_duplicate()