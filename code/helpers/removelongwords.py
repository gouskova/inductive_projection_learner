#!/usr/bin/env python3
# *-* coding:utf-8 *-*

def remove_long_wds(inpath, outpath, threshold):
    with open(inpath, 'r', encoding='utf-8') as infile:
        with open(outpath, 'w', encoding='utf-8') as outfile:
            for line in infile:
                line = line.strip().split()
                if len(line)>threshold:
                    continue
                else:
                    outfile.write(' '.join(line)+'\n')
    print('finished writing your files')


inpath = '/home/maria/git/phonotactics/data/aymara/words_new/LearningData.txt'

outpath = '/home/maria/git/phonotactics/data/aymara/words_new/LearningData_short.txt'

remove_long_wds(inpath, outpath, 39)


