#!/usr/bin/env python3
#*-* coding: utf-8 *-*


'''
some utility functions for calculating the size of CON for various natural class sizes, as well as ngram counts for words of different length

see Gallagher and Gouskova 2018, section on "Why not search exhaustively"
'''

import numpy as np
import matplotlib.pyplot as plt

def consize_calc(conlength, natclass_size):
    consize = 0
    for i in range(conlength+1):
        consize += natclass_size**i
    return consize


def trigram_count(conlength):
    return conlength**3


def reviewer_consize_calc(conlength, natclass_size):
    return int(consize_calc(conlength, natclass_size)+trigram_count(conlength))


def local_ngram_counts(wordlenth, ngramsize):
    return wordlenth-ngramsize+1+2


def nonlocal_ngram_counts(wordlenth, ngramsize):
    '''
    returns the number of nonlocal *segmental* n-grams for words of length N
    formula: N!/n!/(N-n)!
    '''
    if wordlenth > ngramsize:
        fac = np.math.factorial
        return fac(wordlenth)/fac(ngramsize)/fac(wordlenth-ngramsize)
    elif wordlenth == ngramsize:
        return 1
    else:
        return 0


def nonloc_ngram_lineplot(wordlenthrange, ngramsize):
    rangetoplot = [nonlocal_ngram_counts(x, ngramsize) for x in wordlenthrange]
    plt.plot(rangetoplot)
    plt.xticks(np.arange(min(wordlenthrange), max(wordlenthrange)+1, 1.0))
    rangetoplot = [local_ngram_counts(x, ngramsize) for x in wordlenthrange]
    plt.plot(rangetoplot)
    plt.show()


quech_wordlenths = {4:5, 5:38, 6:265, 7:568, 8:715, 9:1414, 10:1327, 11:1626, 12:1424, 13:1074, 14:886, 15:600, 16:435, 17:229, 18:131, 19:55, 20:29, 21:18, 22:6, 23:3}

shona_wordlenths ={4:146, 5:780, 6:5151, 7:9059, 8:24669, 9:29519, 10:45359, 11:41966, 12:41886, 13:32786, 14:25771, 15:17442, 16:10837, 17:6483, 18:3900, 19:2077, 20:1275, 21:804, 22:533}


def wordlenths_histo(language):
    '''
    visualizes in a histogram what the language's word length distributiosn look like
    takes data from dictionaries like the two above, which are copied from maxentoutput.txt
    line called "empiricalLengthDistrib"
    in the future, this could be incorporated into the learner's displays; would need to read from the learning data or from maxentoutput.txt as it's being created
    '''
    plt.bar(language.keys(), language.values())
    plt.show()


def make_wordlenth_ngramdic(language):
    dicofngrams = {}.fromkeys(language)
    for lenth in dicofngrams:
        dicofngrams[lenth]=nonlocal_ngram_counts(lenth,3)*language[lenth]
    return dicofngrams

def plot_number_of_ngrams_per_lg(language):
    dicofngrams = make_wordlenth_ngramdic(language)
    wordlenths_histo(dicofngrams)


def count_seg_searches_nonlocal(language):
    '''
    returns the number of *nonlocal* segmental trigram searches that would be performed given a language's word length distribution data
    '''
    dicofngrams = make_wordlenth_ngramdic(language)
    return sum(dicofngrams.values())

def count_seg_searches_local(language):
    '''
    returns a calculation of local ngram searches given a language's word lenth distrib
    '''
    ngram_searches_per_wrd_lenth = {}.fromkeys(language)
    for lenth in ngram_searches_per_wrd_lenth:
        ngram_searches_per_wrd_lenth[lenth] = local_ngram_counts(lenth, 3)*language[lenth]
    return sum(ngram_searches_per_wrd_lenth.values())
    
