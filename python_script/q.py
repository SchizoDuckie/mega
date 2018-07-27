import json
import sys
import logging
import requests

output_path = "../mega_run_result_json/"

def get_results_by_page(runid, feed, page):
    url = "https://mega.usspk02.orchard.apple.com/api/tests?locale=zh_TW&run_id={0}&source={1}&page={2}"
    res = requests.get(url.format(runid, feed, page)).json()
    logging.debug("get {0} results on page {1} of data feed {2} with runid {3}".format(len(res['result']), page, feed, runid))
    return res['result']

def get_all_results(runid, feed):
    page = 1
    results = []
    while True:
        r = get_results_by_page(runid, feed, page)
        if len(r) <= 0:
            break
        results += r
        logging.info("Added page {0}, total {1} results. ".format(page, len(results)))
        page += 1
    logging.info("Get all results finished, len = {0}".format(len(results)))
    return results

def make_json_list_unique(json_list):
    str_list = [ json.dumps(each, sort_keys=True) for each in json_list ]
    # make it unique
    str_list = list(set(str_list))
    ret = [ json.loads(each) for each in str_list ]
    logging.info("Make unique list, len = {0}".format(len(ret)))
    return ret

def fetch_data(runid, feed):
    logging.info("Fetching data from {0} with runid {1}".format(feed, runid))
    results = get_all_results(runid, feed)
    results = make_json_list_unique(results)
    with open(output_path+feed+str(runid)+'.json', 'w') as fw:
        json.dump(results, fw, indent=2, ensure_ascii=False)

def split_asr(results_file, pass_file, fail_file):
    testcase_list = []
    with open(results_file) as fr:
        testcase_list = json.load(fr)
    pass_cases, fail_cases = [], []
    for each in testcase_list:
        if each['testing']['asr']['asr_pass'] == True:
            pass_cases.append(each)
        else:
            fail_cases.append(each)
    logging.info("split results, ASR pass = {0}".format(len(pass_cases)))
    logging.info("split results, ASR fail = {0}".format(len(fail_cases)))
    with open(pass_file, 'w') as fw:
        json.dump(pass_cases, fw, indent=2, ensure_ascii=False)
    with open(fail_file, 'w') as fw:
        json.dump(fail_cases, fw, indent=2, ensure_ascii=False)

# python3 q.py feed_artist 1644 -d
# available: ["3rd-party_artist", "3rd-party_song", "3rd-party_songByArtist", "feed-8K_artist", "feed-tail_artist", "feed-tail_song", "feed_artist", "feed_song", "feed_songByArtist", "usage_logs_artist"] for zh_CN"
if __name__=='__main__':
    if len(sys.argv) > 1 and '-d' in ' '.join(sys.argv):
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    
    feed = sys.argv[1]
    runid = sys.argv[2]

    fetch_data(runid, feed)
    split_asr(output_path+feed+str(runid)+'.json', output_path+'pass_'+feed+str(runid)+'.json', output_path+'fail_'+feed+str(runid)+'.json')
    
