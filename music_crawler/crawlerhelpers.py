import time
import datetime
import os
import json
import regex
from languagecodeclasses import *
from letterMatcher import *


def language_crawler(start_date, end_date, crawler, cate, top_n=30, force_crawl=False,
                     wait_time=0.25, target='song', get_raw_data=False,
                     delta=1, date_format='%Y-%m-%d'):
    """
    wrapper function for multiple dates input for the basic crawler
    :param datetime start_date:
    :param datetime end_date:
    :param int top_n: pick the top n singers / songs / albums on the list
    :param boolean force_crawl: force update the crawled data
    :param float wait_time: crawl interval
    :param str target: ranked by song / album / singer
    :param int cate: language code, refer to Language enum class
    :param int delta: time step in day
    :return: [singers, songs, albums, singer_song_pairs]
    """

    # change the crawling data frequency
    step = datetime.timedelta(days=delta)
    this_date = start_date

    # we could implement the random access on http request for better stealth crawling
    date_series = []
    singers = []
    songs = []
    albums = []
    singer_song_pairs = []

    # regex pattern for checking no existence of  BoPoMoFo / japanese / korean characters
    # e.g. \p{IsHan} for chinese characters
    pattern = regex.compile(r'([\p{IsBopo}\p{IsHira}\p{IsKatakana}\p{IsHangul}]+)', regex.UNICODE)

    while this_date <= end_date:
        this_date_str = this_date.strftime('%Y-%m-%d')
        # print(this_date_str)
        date_series.append(this_date_str)
        ranking = []
        safe_flag = False
        filename = 'ranking_{}_{}.json'.format(cate.name, this_date_str)
        full_path = os.path.join('data', target, filename)

        # if json file exists, no need to crawl again, unless specified (force_crawl)
        if os.path.isfile(full_path) and not force_crawl:
            with open(full_path) as json_data:
                ranking = json.load(json_data)
                json_data.close()

            # set the flag to True if we load the data from local
            safe_flag = True
        else:
            ranking = crawler(this_date, cate=cate, date_format=date_format)

        # pick the top n from the raw data
        ranking = ranking[0:top_n]

        # rearrange the singers / songs / albums data
        for data in ranking:
            singer_trimmed = singer_trimmer(data['artist_name'], pattern)
            song_trimmed = song_album_trimmer(data['song_name'], pattern)
            album_trimmed = song_album_trimmer(data['album_name'], pattern)
            singer_song_pair = []

            if len(singer_trimmed) == 0 or len(song_trimmed) == 0:
                continue

            this_singer = singer_trimmed[0]
            this_song = song_trimmed[0]

            singer_song_pair = this_singer + "\t" + this_song

            for singer in singer_trimmed:
                if singer not in singers or get_raw_data:
                    singers.append(singer)

            for song in song_trimmed:
                if song not in songs or get_raw_data:
                    songs.append(song)

            for album in album_trimmed:
                if album not in albums or get_raw_data:
                    albums.append(album)

            if singer_song_pair not in singer_song_pairs or get_raw_data:
                singer_song_pairs.append(singer_song_pair)

        # wait for some time in case web server catches us
        if not safe_flag:
            time.sleep(wait_time)
        safe_flag = False

        this_date += step

    # debug the output and write the results to file
    paths = ["data", "collections"]
    file_writer(cate, start_date, end_date, singers, songs, albums, singer_song_pairs, paths)

    return [singers, songs, albums, singer_song_pairs]


def main_crawler(start_date, end_date, crawler, cate, date_format,
                 force_crawl=False, data_sorting=False, get_raw_data=False):
    """
    wrapper and add the data concatenation function
    :param start_date: datetime obj
    :param: end_date: datetime_obj
    :param force_crawl: force update the local database
    :param cate: language code, refer to Language enum class
    :param data_sorting: enable data concatenation
    :return: None
    """
    languages = cate
    singers = []
    songs = []
    albums = []
    singer_song_pairs = []

    print(languages)

    # data available on kkbox for chinese: 2005-09-28
    # date available on kkbox for korean: 2011-01-01

    for language in languages:
        collections = language_crawler(start_date, end_date, date_format=date_format,
                                       top_n=3, cate=language, force_crawl=force_crawl,
                                       crawler=crawler, get_raw_data=get_raw_data, delta=7)

        if data_sorting:
            for singer in collections[0]:
                if (singer not in singers or get_raw_data) and match_pattern(singer, dic['all']):
                    singers.append(singer)

            for song in collections[1]:
                if (song not in songs or get_raw_data) and match_pattern(song, dic['all']):
                    songs.append(song)

            for album in collections[2]:
                if (album not in albums or get_raw_data) and match_pattern(album, dic['all']):
                    albums.append(album)

            for singer_song_pair in collections[3]:
                if (singer_song_pair not in singer_song_pairs or get_raw_data) and match_pattern(singer_song_pair, dic['all']):
                    singer_song_pairs.append(singer_song_pair)

    if data_sorting:
        paths = ['data', 'results']
        file_writer(Language.ALL, start_date, end_date, singers, songs, albums, singer_song_pairs, paths)


def file_writer(cate, start_date, end_date, singers, songs, albums, singer_song_pairs, paths):
    """
    function for writing data to file
    :param list paths: the write directories
    :return: None
    """

    write_song = False
    write_singer = False
    write_album = False

    if songs != []:
        write_song = True

    if singers != []:
        write_singer = True

    if albums != []:
        write_album = True

    if write_singer:
        singer_output_name = "singers_{}_{}_{}".format(cate.name,
                                                       start_date.strftime('%Y-%m-%d'),
                                                       end_date.strftime('%Y-%m-%d'))
        full_path = ""
        for path in paths:
            full_path = os.path.join(full_path, path)
        full_path = os.path.join(full_path, singer_output_name)
        singer_output = open(full_path, 'w')
        for singer in singers:
            singer_output.write(singer)
            singer_output.write("\n")
        singer_output.close()

    if write_song:
        song_output_name = "songs_{}_{}_{}".format(cate.name,
                                                   start_date.strftime('%Y-%m-%d'),
                                                   end_date.strftime('%Y-%m-%d'))
        full_path = ""
        for path in paths:
            full_path = os.path.join(full_path, path)
        full_path = os.path.join(full_path, song_output_name)
        song_output = open(full_path, 'w')
        for song in songs:
            song_output.write(song)
            song_output.write("\n")
        song_output.close()

    if write_album:
        album_output_name = "albums_{}_{}_{}".format(cate.name,
                                                     start_date.strftime('%Y-%m-%d'),
                                                     end_date.strftime('%Y-%m-%d'))
        full_path = ""
        for path in paths:
            full_path = os.path.join(full_path, path)
        full_path = os.path.join(full_path, album_output_name)
        album_output = open(full_path, 'w')
        for album in albums:
            album_output.write(album)
            album_output.write("\n")
        album_output.close()

    if write_singer and write_song:
        singer_song_pair_output_name = "singer_song_pairs_{}_{}_{}".format(cate.name,
                                                                           start_date.strftime('%Y-%m-%d'),
                                                                           end_date.strftime('%Y-%m-%d'))
        full_path = ""
        for path in paths:
            full_path = os.path.join(full_path, path)
        full_path = os.path.join(full_path, singer_song_pair_output_name)
        singer_song_pair_output = open(full_path, 'w')
        for singer_song_pair in singer_song_pairs:
            singer_song_pair_output.write(singer_song_pair)
            singer_song_pair_output.write("\n")
        singer_song_pair_output.close()


def singer_trimmer(raw_data, pattern):
    """
    separate singers and data cleaner
    :param raw_data: singers data
    :param pattern: determine which language character should be omitted
    :return: clean singers data
    """
    clean_data = raw_data.replace('+', ",") \
        .replace('feat', ",") \
        .replace('&', ",").split(",")
    all_singers = []
    for singer in clean_data:
        singer = singer.split("/")[0].strip()
        singer = singer.split("(")[0].strip()
        singer = singer.split("【")[0].strip()
        singer = singer.split("（")[0].strip()
        singer = singer.split("、")[0].strip()
        if pattern.search(singer) is None:
            all_singers.append(singer)
        # if len(parenthesis) > 1:
        #     all_singers.append(parenthesis[1].strip().split(')')[0])
    return all_singers


def song_album_trimmer(raw_data, pattern):
    """
    song and album data cleaner
    :param raw_data: songs / albums
    :param pattern: determine which language character should be omitted
    :return: clean songs / albums data
    """
    if len(raw_data) == 0:
        return []
    all_songs_albums = []
    clean_data = raw_data.split("-")
    clean_data = clean_data[0].split("(")
    # clean_data = raw_data.split("(")
    clean_data = clean_data[0].split("【")
    clean_data = clean_data[0].split("（")
    clean_data = clean_data[0].split("、")
    clean_data = clean_data[0].split("feat")
    # if pattern.search(clean_data[0]) is None:
    #     all_songs_albums.append(clean_data[0].strip())
    all_songs_albums.append(clean_data[0].strip())
    return all_songs_albums
