#!/usr/bin/env python3
# *-* coding:utf-8 *-*

def count_lengths(path):
    lenthdic = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            lenth = len(line.strip().split())
            if not lenth in lenthdic:
                lenthdic[lenth]=1
            else:
                lenthdic[lenth]+=1
    for lenth in lenthdic:
        print('%s\t%s' % (lenth,lenthdic[lenth]))
    return lenthdic

lang = '/home/maria/git/phonotactics/data/shona/verbs/LearningData.txt'
count_lengths(lang)

lang1 = '/home/maria/git/phonotactics/data/aymara/wpdebug/LearningData.txt'

print("Aymara that doesn't work")
#count_lengths(lang1)

lang2 = '/home/maria/git/phonotactics/data/aymara/words_mb/LearningData.txt'
print("Aymara that works")
#count_lengths(lang2)


lang3 = '/home/maria/git/phonotactics/data/quechua/words_mb/LearningData.txt'
print("Quechua that works")

#count_lengths(lang3)


lang4= '/home/maria/git/phonotactics/data/russian/words_mb/LearningData.txt'

print("Russian, doesn't work")
#count_lengths(lang4)




