#!/usr/bin/env python2.7
# encoding: utf-8
"""
loadingPronToFile.py

Convert data entries to pronunciation using existing PWL file and speechPatch.txt file.

data inputs is a list of entries.

"""

from datetime import date
import argparse
import codecs
import itertools
import os
import re
import sys

# general
# libdir = os.path.dirname(__file__)+"../speech-model-automation/resource/tools/admin/"
libdir = "/Users/limintu/projects/speech-model-automation/resource/tools/admin/"
sys.path.append(libdir)

from checkLibrary import readPwl, addToList, delFromList, uprint
DUPLICATED = 1
SKIPPED = 2


def parsePWLtoOutFile(inspfn, inpwlfn, outfile):
    ''' convert lines that are ADDPRON word pron to ADDTOKEN word pron dictionary if not in PWL'''

    apronh = pron2token(inspfn, inpwlfn)
    pron_file = open(outfile, 'w')

    for word in apronh:
        key = word.encode('utf-8')
        pron = ';'.join(apronh[word])
        pron_file.write("{}\t{}\n".format(key, pron))
    return apronh


def generatePermutations(apronh, target):
    '''generate all permutations from pronunciation list'''

    pron_comb = {}
    if target in apronh.keys():
        return DUPLICATED

    skip_flag = False

    # loop over word in target to show all possible ways of pronunciation on screen
    for word in target:
        # type in SKIP to skip to the end of file
        if skip_flag:
            return SKIPPED
        this_word = word.encode('utf-8')

        # fine_pattern: character match
        # coarse_pattern: whole word match
        try:
            fine_pattern = re.compile(('^' + word + '$').encode('utf-8'))
            coarse_pattern = re.compile(word.encode('utf-8'))
        except:
            continue

        pron_not_found = True
        all_prons = []
        diff_prons = []

        # find possible pronunciation dictionary

        try:
            # may throw exception if word not exist in dictionary
            this_value = apronh[word]
            pron_comb.setdefault(this_word, [])
            for temp_pron in this_value:
                diff_prons.append((word, temp_pron.encode('utf-8')))
            pron_not_found = False
        except Exception as e:
            # print(e)
            for k, v in apronh.items():
                this_key = k.encode('utf-8')
                this_value = v[0].encode('utf-8')

                # To do: add language specific filter from Alex
                if coarse_pattern.match(this_key):
                    all_prons.append((this_key, this_value))
            if not all_prons:
                pron_not_found = True

        if len(diff_prons) >= 1:
            for temp_pron in diff_prons:
                pron_comb.setdefault(this_word, [])
                if temp_pron[1].strip() not in pron_comb[this_word]:
                    pron_comb[this_word].append(temp_pron[1].strip())

        # if not found or more than one pronunciation of that word
        # print out possible pronunciation for user to choose from
        # if pron_not_found or len(diff_prons) > 1:
        if pron_not_found:
            # if len(diff_prons) > 1:
            #     all_prons = diff_prons
            if pron_not_found:
                print("not in lexicon, please find similar pronunciation")
            if all_prons:
                for entry in all_prons:
                    this_entry = u'{0}\t{1}'.format(entry[0].decode('utf-8'), entry[1])
                    print(this_entry.encode('utf-8'))
            print("--------------------------")
            temp_prons = []


            # if user put backspace: empty flag which will result in blank pronunciation
            empty_flag = False

            while not temp_prons:
                print(target.encode('utf-8'))
                answer = raw_input(u"please enter pron for this word [{}] (pron1, pron2 ...): ".format(word).encode('utf-8'))
                if not answer:
                    empty_flag = True
                if answer == "SKIP":
                    skip_flag = True

                # To do: add verfication to pronunciation user put in
                temp_prons = answer.split(",")

            # add all possible pronunciation to pron_comb
            if not empty_flag:
                for temp_pron in temp_prons:
                    pron_comb.setdefault(this_word, [])
                    if temp_pron.strip() not in pron_comb[this_word]:
                        pron_comb[this_word].append(temp_pron.strip())
            print("")

    if skip_flag:
        return SKIPPED

    # generating combo from pron_comb
    temp_data = []
    for word in target:
        this_word = word.encode('utf-8')
        if pron_comb.get(this_word):
            this_combo = pron_comb[this_word]
            temp_data.append(this_combo)
    print(target.encode('utf-8'))
    # print(temp_data)
    combos = list(itertools.product(*temp_data))
    permutations = []
    for combo in list(combos):
        this_combo = '.'.join(combo)
        permutations.append(this_combo)
        print(this_combo)
    print("")

    return (target, permutations)


def pron2token(inspfn, inpwlfn):
    '''
    convert lines in speechPatch.txt that are ADDPRON word pron to ADDTOKEN word pron if not in PWL
    function modified from addpron2addtoken.py
    '''

    # get the PWL words
    aphones, astates, awords, awordh, apronh, astateh = readPwl(inpwlfn, useutf8=True)
    for line in file(inspfn):
        line = line.strip()
        uline = line.decode('utf8')
        if uline.startswith("LEX"):
            try:
                (lex, lexline) = uline.split('\t')
            except ValueError:
                if '\t' not in uline: uprint("no tab in line :%s:" % (uline))
                badfields = uline.split('\t')
                print(badfields)
                raise ValueError, "Cannot split line :%s: into 2 by tab (%s)" % (uline, "/".join(badfields))
            fields = lexline.split(None)
            if lexline.startswith("ADDPRON"):
                word, pron = fields[1], fields[2]
                awords.add(word)
                try:
                    apronh[word].append(pron)
                except:
                    apronh[word] = [pron]
            # keep up to date with tokens introduced in lexpatch
            elif lexline.startswith("ADDTOKEN"):
                word, pron = fields[1], fields[2]
                awords.add(word)
                try:
                    apronh[word].append(pron)
                except:
                    apronh[word] = [pron]
            elif lexline.startswith("CLONETOKEN"):
                uprint("Error: CLONETOKEN deprecated", fp=sys.stderr)
                sys.exit(1)
            elif lexline.startswith("MODTOKEN"):
                fromword, toword = fields[2], fields[1]
                awords.remove(fromword)
                awords.add(toword)
                apronh[toword] = apronh[fromword][:]
            elif lexline.startswith("DELTOKEN"):
                word = fields[1]
                awords.remove(word)
                del apronh[word]
            elif lexline.startswith("DELPRON"):
                word, pron = fields[1], fields[2]
                if pron == '*':
                    apronh[word] = []
                else:
                    apronh[word] = delFromList(apronh[word], pron)
            elif lexline.startswith("MODPRON"):
                uprint("Error: MODPRON deprecated", fp=sys.stderr)
                sys.exit(1)
    return apronh


############################################################
def main():

    # data initialization
    lexipatch = False
    locale = "zh_TW"

    # parameters for speechPatch, lex_dict, pwl file, out_lex_file
    # have to extract the pwl file
    # inspfn = os.path.join("..", "speech-model-automation", "resource", "patches", locale, "speechPatch.txt")
    # outspfn = os.path.join("..", "speech-model-automation", "resource", "patches", locale, "lex_dict")
    # inpwlfn = os.path.join("..", "speech-model-automation", "resource", "patches", locale, "{}.pwl".format(locale))
    inspfn = "/Users/limintu/projects/speech-model-automation/resource/patches/zh_TW/speechPatch.txt"
    outspfn = "/Users/limintu/projects/speech-model-automation/resource/patches/zh_TW/lex_dict"
    inpwlfn = "/Users/limintu/projects/speech-model-automation/resource/patches/zh_TW/zh_TW.pwl"

    # input
    # data_dir = '../../../music-crawler/temp/{0}'.format(date(2018, 5, 7))
    # data_dir = './mega2k/{0}'.format(date.today())
    data_dir = './'
    # data_files = [f for f in os.listdir(data_dir) if '_title.csv' in f]
    data_file = '/2k_artists_only_chinese.txt'
    with codecs.open(data_dir + data_file, 'r', encoding='utf-8') as f:
        data_inputs = [line.strip().encode('utf-8') for line in f.readlines()]
        print len(data_inputs)

    # cat = 'spotify'
    # with codecs.open('{0}{1}'.format(data_dir, data_file.format(cat, '.csv')), 'r', encoding='utf-8') as f:
        # data_inputs = [line.strip().encode('utf-8') for line in f.readlines()]

    # data_inputs = ['一妳好嗎'] #'勉強幸福', '如果我們不曾相遇'

    # output
    # dir = '{0}/out_lex_files'.format(data_dir)
    dir = data_dir
    if not os.path.exists(dir):
        os.makedirs(dir)
    # out_lex_file_path = '{0}/{1}'.format(dir, data_file.format(cat, '_pron.txt'))
    out_lex_file_path = '{0}/{1}'.format(dir, 'ARTIST.lst')

    if not os.path.isfile(inpwlfn):
        raise IOError, "pwl file not found: %s" % inpwlfn
    if "pwl" not in inpwlfn:
        raise IOError, "please ensure pwl is i the name of the input pwl file" % inpwlfn

    # check existance of output files/directories
    outdir = os.path.dirname(outspfn)
    if not outdir:
        outdir='.'
    elif not os.path.isdir(outdir):
        os.makedirs(outdir,0755)

    # generate pronunciation dictionary
    apronh = parsePWLtoOutFile(inspfn, inpwlfn, outfile=outspfn)
    all_prons = []

    # for words in data_inputs:
    #     this_input = words.decode('utf-8')
    #     print(this_input)
    #     for word in this_input:
    #         print(apronh[word])

    # loop over data_inputs to generate pronunciation
    for data_input in data_inputs:
        this_input = data_input.decode('utf-8')
        return_val = generatePermutations(apronh, this_input)
        if return_val != DUPLICATED and return_val != SKIPPED:
            all_prons.append(return_val)
        else:
            print('data exists: {0}'.format(data_input))

    out_lex_file = open(out_lex_file_path, 'w')
    for all_pron in all_prons:
        for i in range(0, len(all_pron[1])):
            pron = all_pron[1][i]

            # this part is for lexipatch
            # if working on loc-data you may toggle lexipatch tag to remove LEX ADDTOKEN / ADDPRON
            if pron:
                addtoken_flag = "LEX\tADDTOKEN " if lexipatch else ""
                addpron_flag = "LEX\tADDPRON "if lexipatch else ""
                if i == 0:
                    out_lex_file.write("{}{} {}\n".format(addtoken_flag, all_pron[0].encode('utf-8'), pron))
                else:
                    out_lex_file.write("{}{} {}\n".format(addpron_flag, all_pron[0].encode('utf-8'), pron))
    out_lex_file.close()

    # finished
    return 0        # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)
