#!/usr/bin/env python3
# *-* coding: utf-8 *-*

'''
given a feature file, produces agree and disagree bigrams and [] trigrams
as in:
*[+son][+son]
*[-son][-son]
*[+son][-son]
*[-son][+son]
*[+son][][+son]
*[-son][][-son]
*[+son][][-son]
*[-son][][+son]
'''


import os

def find_feat_values(featfilepath):
    with open(featfilepath, 'r', encoding='utf-8') as f:
        featfile = f.readlines()
        features = featfile.pop(0).lstrip("\t").rstrip('\n').split('\t')
        fdic = {}.fromkeys(features)
        for feat in features:
            fdic[feat]=['+'+feat]
            for line in featfile:
                line = line.rstrip('\n').split('\t')
                if '-'+feat not in fdic[feat]:
                    i = features.index(feat)
                    if line[i+1]=='-':
                        fdic[feat].append('-'+feat)
                else:
                    break
    return fdic
                    

def make_bigrams(fdic, agree=True, ocp=True):
    conlist = []
    for feat in fdic:
        fplus = fdic[feat][0]
        if ocp:
            conlist.append('[%s][%s]' % (fplus, fplus))
        if len(fdic[feat])>1:
            fminus = fdic[feat][1]
            if ocp:
                conlist.append('[%s][%s]' % (fminus, fminus))
            if agree:
                conlist.append('[%s][%s]' % (fplus, fminus))
                conlist.append('[%s][%s]' % (fminus, fplus))
    return conlist


def make_placeholder_trigrams(fdic, agree=True, ocp=True):
    conlist = []
    for feat in fdic:
        fplus = fdic[feat][0]
        if ocp:
            conlist.append('[%s][][%s]' % (fplus, fplus))
        if len(fdic[feat])>1:
            fminus = fdic[feat][1]
            if ocp:
                conlist.append('[%s][][%s]' % (fminus, fminus))
            if agree:
                conlist.append('[%s][][%s]' % (fplus, fminus))
                conlist.append('[%s][][%s]' % (fminus, fplus))
    return conlist


def make_edge_trigrams(conlist, kind='+wb'):
    #this should be the output of make_bigrams()
    newconlist = []
    kind = '['+kind+']'
    for c in conlist:
        newconlist.append(kind+c)
        newconlist.append(c+kind)
    return newconlist

def make_mb_trigrams(fdic, ocp=True, agree=True):
    conlist = []
    for feat in fdic:
        fplus = fdic[feat][0]
        if ocp:
            conlist.append('[%s][+mb][%s]' % (fplus, fplus))
        if len(fdic[feat])>1:
            fminus = fdic[feat][1]
            if ocp:
                conlist.append('[%s][+mb][%s]' % (fminus, fminus))
            if agree:
                conlist.append('[%s][+mb][%s]' % (fplus, fminus))
                conlist.append('[%s][+mb][%s]' % (fminus, fplus))
    conlist.extend(make_edge_trigrams(make_bigrams(fdic), kind='+mb'))
    return conlist


def make_gram_file(proj = 'default', path=os.getcwd().split('code')[0], featfilepath=os.path.join(os.getcwd().split('code')[0], 'temp', 'Features.txt')):
    fdic = find_feat_values(featfilepath)
    conlist = make_bigrams(fdic)
    conlist.extend(make_edge_trigrams(conlist))
    conlist.extend(make_placeholder_trigrams(fdic))
    with open(os.path.join(path, 'maxent2', 'temp', 'baseline_grammar.txt'), 'w', encoding='utf-8') as out:
        for c in conlist:
            out.write(proj+'\t*'+c+'\n')
    print('made agree/ocp grammar file')


   
    
