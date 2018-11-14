#!/usr/bin/env python3


'''
this is the script that created shona/TestingData.txt

it can do a bit more than just combine vowels and attested singleton and cluster Cs, but running it from the command line generates a file of 40,000 trisyllables. look at the bottom of this script to see the path it saves the file to.

'''

import os
import itertools
import random

disharmcombos = ['ae', 'ao', 'ei', 'eo', 'ue', 'uo', 'ie','io', 'ou']




def get_segs(featsfile = 'data/shona/verbs/Features.txt'):
    '''
    reads in all the segments from the full features file
    '''
    segs = []
    with open(os.path.join(os.getcwd().split('code')[0],featsfile), 'r', encoding='utf-8') as feats:
        sfeats =feats.readlines()[1:]
        for line in sfeats:
            seg = line.split('\t')[0]
            segs.append(seg)
    vowels = ['a','e','i','o','u']
    print('done getting segs')
    return [x for x in segs if not x in vowels] 


def make_consonant_clusters(consonants, lenth):   
    '''
     make all the possible consonant clusters of length X
    '''
    if lenth == 2:
        clusters = [' '.join(string) for string in list(itertools.product(consonants, repeat=2))]
    else:
        powerset = itertools.chain.from_iterable(itertools.product(consonants, repeat=r) for r in range(lenth+1))
        clusters = [' '.join(string) for string in list(powerset) if len(string)>1]
    print('done making consonant clusters')
    return clusters


def find_att_clusters(wlist, clist, lenth):
    '''
    identifies those clusters of all the possible combos that are in the words of a wlist.
    wlist is a giant string. read it in from a file without splitting on newlines 
    lenth specifies the maximum length of a cluster that will be searched for
    '''
    clusters = make_consonant_clusters(clist, lenth)
    return sorted([x for x in clusters if x in wlist])


def count_att_clusters(wlist, clusters):
    dic = {}.fromkeys(clusters, 0)
    for wd in wlist:
        for cl in dic:
            if cl in wd:
                dic[cl]+=1
            else:
                continue
    return dic


def get_ref_wdlist(path):
    '''
    tell the cluster finder where to look for wds of the language
    '''
    with open(path, 'r', encoding='utf-8') as f:
        wlist = f.read().replace('\n', '|')
    print('retrieved reference wordlist')
    return wlist


def make_illeg_clusters(wlist, clist, lenth):
    '''
    returns a list of clusters of length "lenth" that are NOT in wlist
    '''
    clusters = set(make_consonant_clusters(clist, lenth))
    return sorted(list(clusters-set(find_att_clusters(wlist, clist, lenth)))) 

def cvsyll(clist, verbfinal=False):
    '''
    makes a simple CV sylable
    if verbfinal==True, the vowel is 'a'. else drawn at random from five vowels
    '''
    vowels = ['a','e','i','o','u']
    consonants = clist
    if verbfinal == True:
        return random.choice(consonants) + ' ' + 'a'
    else:
        return random.choice(consonants) + ' ' + random.choice(vowels)


def filter_cons_clusters():
    cons = get_segs()
    path = os.getcwd().split('code')[0]+'data/shona/verbs/LearningData.txt'
    wdlist = get_ref_wdlist(path)
    for wd in wdlist.split('|'):
        print(wd)
    clusts = find_att_clusters(wdlist, cons, lenth=2)
    print(clusts)
    out = count_att_clusters(wdlist.split('|'), clusts)
    return out

def make_CVtrisylls(nwords, binary=False):
    wds = {}
    cons = get_segs()
    while len(wds)<=nwords:
        syll1 = cvsyll(cons)
        syll2 = cvsyll(cons)
        syll3 = cvsyll(cons, verbfinal=True)
        wd = ' '.join([syll1,syll2,syll3])
        vlist = ''.join([x for x in wd[:-1] if x in ['a', 'e','i','o','u']])
        if binary:
            if not vlist in disharmcombos:
                wds[wd] = {'consonants': 'singleton', 'vowels':'harmonic'}
            else:
                wds[wd] = {'consonants': 'singleton', 'vowels': 'disharmonic'}
        else:
            wds[wd]={'consonants':'singleton', 'vowels':vlist}
    return wds




def make_att_CCtrisylls(nwords, lenth,  binary=False, scrape_clusts=False):
    vowels = ['a','e','i','o','u']
    wds = {}
    cons=get_segs()
    path = os.getcwd().split('code')[0]+'data/shona/verbs/LearningData.txt'
    print('path where reference clusters are coming from:')
    print(path)
    if not scrape_clusts:
        clusts = find_att_clusters(get_ref_wdlist(path), cons, lenth)
    else:
        clusts = ['g w', 'm w', 'n j', 'n d', 'b w', 'N g', 'n z', 'k w', 'h w', 's w', 'm b']
    print('the clusters')
    print(clusts)
    while len(wds)<=nwords:
        syll1 = cvsyll(cons)
        syll3 = cvsyll(cons, verbfinal=True)
        syll2 = random.choice(clusts) + ' ' + random.choice(vowels)
        wd = ' '.join([syll1,syll2,syll3])
        vlist = ''.join([x for x in wd[:-1] if x in vowels])
        if binary:
            if not vlist in disharmcombos:
                wds[wd] = {'consonants': 'attested', 'vowels':'harmonic'}
            else:
                wds[wd] = {'consonants': 'attested', 'vowels': 'disharmonic'}
        else:
            wds[wd]={'consonants':'attested', 'vowels': vlist}
    return wds

   
def make_unatt_CCtrisylls(nwords, lenth,  binary=False):
    vowels = ['a','e','i','o','u']
    wds = {}
    cons=get_segs()
    path = os.getcwd().split('code')[0]+'data/shona/verbs/LearningData.txt'
    clusts = make_illeg_clusters(get_ref_wdlist(path), cons, lenth)
    while len(wds)<=nwords:
        syll1 = cvsyll(cons)
        syll3 = cvsyll(cons, verbfinal=True)
        syll2 = random.choice(clusts) + ' ' + random.choice(vowels)
        wd = ' '.join([syll1,syll2,syll3])
        vlist = ''.join([x for x in wd[:-1] if x in vowels])
        if binary:
            if not vlist in disharmcombos:
                wds[wd] = {'consonants': 'unattested', 'vowels':'harmonic'}
            else:
                wds[wd] = {'consonants': 'unattested', 'vowels': 'disharmonic'}
        else:
            wds[wd]={'consonants':'unattested', 'vowels':vlist}
    return wds





def write_testfile(dics, outpath):
    with open(outpath, 'w', encoding='utf-8') as outfile:
        for dic in dics:
            for wd in dic:
                outfile.write("%s\t%s\t%s\n" % (wd, dic[wd]['vowels'],dic[wd]['consonants']))



words1 = make_CVtrisylls(5000)
words2 = make_att_CCtrisylls(5000, 2, scrape_clusts=True)




write_testfile([words1, words2], '/home/maria/Desktop/TestingData.txt')



 
