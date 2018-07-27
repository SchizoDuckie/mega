import sys
sys.path.append("../")
from wikiCrawler import *
from letterMatcher import *
import pandas as pd
import os


SKIPPED = 73


def read_input(file_path, delimiter):
    # to skip row, add this parameter: skiprows=range(2004, 2005)
    table = pd.read_csv(file_path, sep="|", header=0, encoding="utf-8")
    header = list(table)[0]
    cols = list(x.strip() for x in header.split(delimiter))
    out_table = pd.DataFrame()
    temp = table[header].str.split(delimiter, n=len(cols)-1, expand=True)
    for i in range(0, len(cols)):
        out_table[cols[i]] = temp[i]
    return out_table


def creating_alias(names, cn_dict, en_dict, cn_ref_table):
    target_names = []
    eng_names = []
    nick_names = []
    cn_ref_table_size = cn_ref_table.shape[0]
    i = 0
    for name in names:
        print("progress {0:.2f} %".format(i / cn_ref_table_size * 100.))
        i += 1
        if pattern_worker(name, ['zh', 'en', 'zh_en_num']):
            data = wiki_crawler(name)
            if data == TO_THE_END:
                break
            zh_name = data[0]
            en_name = data[1]
            if match_pattern(name, dic["en"]):
                en_name = name
            nick_name = data[2]

            if not en_name or zh_name == en_name:
                if zh_name.lower() in en_dict:
                    index = en_dict[zh_name.lower()]
                    en_name = zh_name
                    zh_name = HanziConv.toTraditional(cn_ref_table['cn_name'][index])
                elif HanziConv.toTraditional(zh_name) in cn_dict:
                    index = cn_dict[HanziConv.toTraditional(zh_name)]
                    en_name = cn_ref_table['en_name'][index]
                if zh_name == en_name:
                    zh_name = ""

            target_names.append(zh_name)
            eng_names.append(en_name)
            nick_names.append(nick_name)
        else:
            target_names.append("")
            eng_names.append("")
            nick_names.append("")

    return target_names, eng_names, nick_names


def file_writer(table, file_path):
    table.to_csv(file_path)


def alias_list_creator(store_id_file_path, outfile_path, out_alias_path):
    id_table = read_input(store_id_file_path, "\t")
    ref_table = read_input(outfile_path, ",")
    all_entries = id_table['zh_name'].values.tolist()

    with open(out_alias_path, 'w') as outfile:
        for entry in all_entries:
            check_existing_pairs(entry, ref_table, outfile, loc='zh')
            check_existing_pairs(entry, ref_table, outfile, loc='en')

    outfile.close()


def check_existing_pairs(entry, ref_table, outfile, loc='zh'):
    # adding other loc name to alias list
    # adding zh_num name to alias list
    valid_loc = {'zh', 'en'}
    if loc not in valid_loc:
        raise ValueError("results: loc must be one of %r." % valid_loc)
    from_loc = loc
    to_loc = 'en' if from_loc == 'zh' else 'zh'
    from_loc_name = '{}_name'.format(from_loc)
    to_loc_name = '{}_name'.format(to_loc)

    if match_pattern(entry, dic[from_loc]):
        this_row = ref_table.loc[ref_table[from_loc_name] == entry]
        if not this_row.empty:
            if not this_row['alias'].values[0] and not this_row[to_loc_name].values[0]:
                return SKIPPED
            alias_list = []
            alias_col = this_row['alias'].values[0].split(",")
            other_name_col = this_row[to_loc_name].values[0].split(",")
            for e in alias_col:
                if e:
                    alias_list.append(e)
            for e in other_name_col:
                if e:
                    alias_list.append(e)
        else:
            return SKIPPED
        if alias_list:
            for i in range(0, len(alias_list)):
                alias_list[i] = alias_list[i].replace("\"", "")
            alias_collections = " | ".join(alias_list)
            outfile.write("\t[ \"from\": \"{}\", \"to\": \" ( {} ) \" ],".format(entry, alias_collections))
            outfile.write("\n")


if __name__ == "__main__":
    file_input = os.path.join("..", "data_manual_clean", "alias_name", "zh-HK_2K_artist_id.txt")
    cn_ref_file_input = os.path.join("..", "data_manual_clean", "alias_name", "top2000_cleand_withAdamId_v1.txt")
    file_output = os.path.join("..", "data_manual_clean", "alias_name", "zh-TW_2K_artist_out.txt")
    outfile_path = os.path.join("..", "data_manual_clean", "alias_name",
                                "zh-HK_2K_artist_out.txt")
    out_alias_path = os.path.join("..", "data_manual_clean", "alias_name",
                                "zh-HK_2K_artist_out_alias_list.txt")
    table = read_input(file_input, "\t")
    cn_ref_table = read_input(cn_ref_file_input, ",")
    cn_ref_table_size = cn_ref_table.shape[0]
    cn_ref_dict = {}
    en_ref_dict = {}

    for i in range(0, cn_ref_table_size):
        cn_name = HanziConv.toTraditional(cn_ref_table['cn_name'][i])
        if cn_name:
            cn_ref_dict[cn_name] = i
        en_name = cn_ref_table['en_name'][i].lower()
        if en_name:
            en_ref_dict[en_name] = i

    print(table.keys())

    zh_names = table['zh_name']
    target_names, eng_names, nick_names = creating_alias(zh_names, cn_ref_dict, en_ref_dict, cn_ref_table)
    target_names_se = pd.Series(target_names)
    eng_names_se = pd.Series(eng_names)
    nick_names_se = pd.Series(nick_names)
    temp_table = pd.DataFrame()
    len = target_names_se.shape[0]
    temp_table['adamId'] = table['adamId'][0:len]
    temp_table['zh_name'] = target_names_se.values
    temp_table['en_name'] = eng_names_se.values
    temp_table['alias'] = nick_names_se.values

    print(temp_table.to_string())
    file_writer(temp_table, file_output)

    # alias_list_creator(file_input, outfile_path, out_alias_path)







