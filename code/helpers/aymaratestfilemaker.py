#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, re, itertools, random


def get_segs(featsfile = 'data/aymara/words_unparsed/Features.txt'):
    '''
    reads in all the segments from the full features file
    '''
    segs = []
    with open(os.path.join(os.getcwd().split('code')[0],featsfile), 'r', encoding='utf-8') as feats:
        sfeats =feats.readlines()[1:]
        for line in sfeats:
            seg = line.split('\t')[0]
            segs.append(seg)
    print('done getting segs')
    return segs 


#this next step could be read in from features, too, but faster and easier to do by hand
aymara_consonants = [x for x in get_segs() if not x in ['X', '¦', 'a','i','u','e','o','U','O','A','E','I']]

vowels = ['a','i','u']
plain = ['p','t','c','k', 'q']
ejective = ['b','d','z','g', 'G']
aspirate=['P','T','K','C', 'Q']
uvulars = ['q','G','Q','x']
velars = ['k','g','K']


stops = plain+ejective+aspirate

nonstops = [x for x in aymara_consonants if not x in stops]

posscodas = nonstops+plain


def cv_syll(consonants, vowels):
    '''
    makes a CV sylable without stops
    '''
    return random.choice(consonants) + ' ' + random.choice(vowels)


def cvc_syll(stops, posscodas, vowels):
    '''
    makes a CVC syllable with a stop onset and whatever coda is specified in posscodas
    '''
    return ' '.join([random.choice(stops), random.choice(vowels), random.choice(posscodas)])

def nplace(word):
    '''
    there are no velar nasals in the language
    but other than velars and uvulars, nasals agree in place of articulation inside morphemes
    it's unclear what happens across morpheme boundaries, but to be on the safe side, the nonce words will have agreement both tauto- and heteromorphemically
    '''
    labrexin = re.compile(r'([nN] )(¦ )*([pbP])')
    labrexout = r'm \2\3'
    dentrexin = re.compile(r'([mN] )(¦ )*([tdT])')
    dentrexout = r'n \2\3'
    palrexin = re.compile(r'([mn] )(¦ )*([czC])')
    palrexout = r'N \2\3'
    word = re.sub(labrexin, labrexout, word)
    word = re.sub(dentrexin, dentrexout, word)
    word = re.sub(palrexin, palrexout, word)
    return word


def mark_copies(word):
    '''
    the laryngeal co-occurrence restriction on ejectives is supposed to be that you can't have two of them in a morpheme unless they are identical
    the learner we are working with cannot encode identity exemptions, so we transcribe the second ejective as a special copy segment, X. thus,
    in: b a m b a
    out: b a m X a
    '''
    eject_re = re.compile(r'([bdgG] )(([^¦bdgG] )*)\1')
    rexout = r'\1\2X '
    CVC = re.match(eject_re, word)
    if CVC: 
        word = re.sub(eject_re, rexout, word)
    return word.strip()



def dor_coocc(word):
    '''
    inside a morpheme, a uvular cannot combine with a velar, and vice versa. 
    the function replaces each dorsal with its velar or uvular counterpart to enforce this 
    since the uvular fricative does not have a velar counterpart, we choose a velar at random
    thus: 
    in: q a n k a
    out: q a n q a
    in: G a g a
    out: G a G a # and we'll fix the two-ejectives problem later, using mark copies
    '''
    dordic = {'k':'q', 'q':'k', 'G':'g', 'g':'G', 'K':'Q', 'Q':'K', 'x': random.choice(velars)}
    dorsals = ''.join(velars+uvulars)
    dor_re = re.compile(r'([' + dorsals + '] )' + '(([^¦' + dorsals + '] )*)' + '([' + dorsals + '])')
    CVC = re.match(dor_re, word)
    if CVC:
        C1= CVC.group(1).strip()
        C2= CVC.group(4).strip()
        repl = r'\1\2'+dordic[C2] 
        if (C1 in velars and not C2 in velars) or (C1 in uvulars and not C2 in uvulars):
           word = re.sub(dor_re, repl, word).strip()
    return word


def uv_V_agr(word):
    '''
    this language contrasts three vowel qualities: [i, u, a]
    but the high vowels lower to mid around uvulars. this happens both before and after uvulars, with intervening segments
    for example, 
    /qumpa/ --> [qompa]
    /pilqu/ --> [pelqo]
    but this lowering is bounded; if the high vowel is too far, it is not affected.
    /CiQa-m-pi-s-ti/ --> [CeQa-m-pi-s-ti] not *CeQampeste
    /apa-ni-ta-x-ti/ --> [apa-ni-ta-x-te] not *apanetaxte
    '''
    highs = {'i':'e',
            'I':'E',
            'u':'o',
            'U':'O'}
    rex1 ='([^kgK] ){0,1}([xqGQ])'
    rex2 = '([xqGQ])( [^kgK]){0,1}'
    for vowel in highs:
        #high vowels become mid when followed by a uvular:
        rexin = '('+ vowel+ ' )' + rex1
        rexout = highs[vowel]+' \\2\\3'
        word = re.sub(rexin, rexout, word)
        #high vowels become mid when preceded by a uvular:
        rexin = rex2 + '( '+vowel+ ")"
        rexout = '\\1\\2' +' '+highs[vowel]
        word = re.sub(rexin, rexout, word)
    return word

def cor_coocc(word):
    '''
    inside a morpheme, a dental [tdT] cannot combine with a palatal [czC]. 
    the function replaces palatals downstream from dentals with dentals having corresponding laryngeal features 
    in: t a n C a
    out: t a n T a
    in: d a z a
    out: d a d a # and we'll fix the two-ejectives problem later, using mark copies
    '''
    dic = {'c':'t', 'z':'d', 'C':'T'}
    cor_re = re.compile(r'([tdT] )' + '(([^¦tdT] )*)' + '([cCz])')
    CVC = re.match(cor_re, word)
    if CVC:
        C1= CVC.group(1).strip()
        C2= CVC.group(4).strip()
        repl = r'\1\2'+dic[C2] 
        if (C1 in ['t','d','T'] and not C2 in ['t','d','T']):
           word = re.sub(cor_re, repl, word).strip()
    return word


def make_monomorphemic_cvcv(consonants1, consonants2, vowels, nwords):
    '''
    we are mostly interested in the restrictions on ejective and aspirated stops, so we'll create a number of CVCV words with stops as onsets as well as some nonstops in each position
    nasal agreement will not be relevant in CVCV words, but dorsal co-occurrence and uvular V agremeent will be, as will copy marking
    '''
    wlist = []
    while len(wlist)<nwords:
        syll1 = cv_syll(consonants1, vowels)
        syll2 = cv_syll(consonants2, vowels)
        word= ' '.join([syll1, syll2])
#        word = mark_copies(uv_V_agr(dor_coocc(cor_coocc(word))))
        word = mark_copies(uv_V_agr(word))
        if not word in wlist:
            wlist.append(word)
    return wlist

def make_monomorphemic_cvccv(ons1, ons2, posscodas, vowels, nwords):
    '''
    to make CVCCV roots, there are three additional considerations:

    nasal place assimilation has to be enforced on codas
    '''
    wlist = []
    while len(wlist)<nwords:
        syll1 = cvc_syll(ons1, posscodas, vowels)
        syll2 = cv_syll(ons2, vowels)
        word = ' '.join([syll1, syll2])
        word = mark_copies(uv_V_agr(dor_coocc(nplace(cor_coocc(word)))))
        if not word in wlist:
            wlist.append(word)
    return wlist


def make_complex_cvccv(ons1, ons2, posscodas, vowels, nwords, longv):
    wlist = []
    while len(wlist)<=nwords:
        syll1 = cvc_syll(ons1, posscodas, vowels)
        if longv:
            syll2 = cv_syll(ons2, vowels)
        else:
            syll2 = cv_syll(ons2, ['I', 'A', 'U'])
        syll3 = random.choice(['N a', 'Y u', 's I'])
        word = ' ¦ '.join([syll1, syll2, syll3])
        word = mark_copies(uv_V_agr(dor_coocc(nplace(cor_coocc(word)))))
        if not word in wlist:
            wlist.append(word)
    return wlist

def make_testwords(num):
    '''
    returns num x 10 of CVCV monomorphemic words
    num x 10 of CVCCV monomorphemic words
    '''
    stimdic = {}.fromkeys(make_monomorphemic_cvcv(nonstops, stops, vowels, num*10), 'nonstop_V_stop_V') #start by making some fillers of the CVCV shape
    pool = ['ejective', 'aspirate', 'plain']
    for x in make_monomorphemic_cvccv(nonstops,stops, posscodas, vowels, num*10):
        stimdic[x]='nonstop_VC_stop_V' #and some CVCCV
#    for x in make_complex_cvccv(nonstops, stops, posscodas, vowels, num, True):
#        stimdic[x]='nonstop_VC_¦_stop_VV'
#    for x in make_complex_cvccv(nonstops, stops, posscodas, vowels, num, False):
#        stimdic[x]='nonstop_VC_¦_stop_V'
    combos = list(itertools.product(pool, repeat=2))
    for x in combos:
        wds = make_monomorphemic_cvcv(eval(x[0]), eval(x[1]), vowels, num)
        for wd in wds:
            stimdic[wd] = '_'.join([x[0],'V', x[1], 'V'])
#        wds = make_monomorphemic_cvccv(eval(x[0]),eval(x[1]),  posscodas, vowels, num)
#        for wd in wds:
#            stimdic[wd] =x[0]+'_VC_'+ x[1]+'V'
#        wds = make_complex_cvccv(eval(x[0]),eval(x[1]), posscodas, vowels, num, True)
#        for wd in wds:
#            stimdic[wd] =x[0]+'_VC_¦_'+ x[1]+'VV'
#        wds = make_complex_cvccv(eval(x[0]),eval(x[1]), posscodas, vowels, num, False)
#        for wd in wds:
#            stimdic[wd] =x[0]+'_VC_¦_'+ x[1]+'V'
    return stimdic

def make_consonant_clusters(consonants=aymara_consonants, lenth=2):   
    '''
     make all the possible consonant clusters of length X
    '''
    if lenth == 2:
        clusters = [' '.join(string) for string in list(itertools.product(consonants, repeat=2))]
        morphclusters = [' ¦ '.join(string) for string in list(itertools.product(consonants,repeat=2))]

    else:
        powerset = itertools.chain.from_iterable(itertools.product(consonants, repeat=r) for r in range(lenth+1))
        clusters = [' '.join(string) for string in list(powerset) if len(string)>1]
        morphclusters = [' ¦ '.join(string) for string in list(powerset) if len(string)>1]
    print('done making consonant clusters')
    return clusters+morphclusters 


def get_ref_wdlist(path):
    '''
    tell the cluster finder where to look for wds of the language
    '''
    with open(path, 'r', encoding='utf-8') as f:
        wlist = f.read().replace('\n', '|')
        print('retrieved reference wordlist')
    return wlist


def find_att_clusters(wlist, clist, lenth):
    '''
    identifies those clusters of all the possible combos that are in the words of a wlist.
    wlist is a giant string. read it in from a file without splitting on newlines 
    lenth specifies the maximum length of a cluster that will be searched for
    '''
    clusters = make_consonant_clusters(clist, lenth)
    print('number of possible clusters: ')
    print(len(clusters))
    return sorted([x for x in clusters if x in wlist])


def count_att_clusters(wlist):
    dic ={}
    consonant = ''.join(aymara_consonants)
    cluster_re = re.compile(r'(['+consonant+'] ¦* *['+consonant+'])')
    with open(wlist, 'r', encoding='utf-8') as f:
        for wd in f:
            clusts = re.findall(cluster_re, wd)
            for cl in clusts:
                if cl in dic:
                    dic[cl]+=1
                else:
                    dic[cl]=1
    return dic

def write_clusters(out='/home/maria/Desktop/clusters.txt'):
    with open(out, 'w', encoding='utf-8') as f:
        for x in sorted(clusters, key=clusters.get, reverse=True):
            f.write('%s\t%s\n' % (x, clusters[x]))

def write_testfile(stimdic, outpath, filterclusters=False):
    '''
    filterclusters is either a dictionary of clusters produced by the count_att_clusters function or 'False'
    '''
    print(len(stimdic))
    counter=0
    if filterclusters:
        goodclusters = [x for x in filterclusters if filterclusters[x]>20]
        with open(outpath, 'w', encoding='utf-8') as outfile:
            for wd in stimdic:
                if not 'VC' in stimdic[wd]:
                    outfile.write("%s\t%s\n" % (wd, stimdic[wd]))
                    counter+=1
                elif 'VC' in stimdic[wd] and not '¦' in stimdic[wd]:
                    clust = wd[4:7]
                    if clust in goodclusters:
                        outfile.write("%s\t%s\n" % (wd, stimdic[wd]))
                        counter+=1
                elif 'VC_¦'  in stimdic[wd]:
                    clust = wd[4:9]
                    if clust in goodclusters:
                        outfile.write("%s\t%s\n" % (wd, stimdic[wd]))
                        counter+=1
        print(counter)
    elif not filterclusters:
        with open(outpath, 'w', encoding='utf-8') as outfile:    
            outfile.write("%s\t%s\n" % (wd, stimdic[wd]))
    



clusters = count_att_clusters('/home/maria/git/phonotactics/data/aymara/words/LearningData_orig.txt')

dic = make_testwords(1000)

write_testfile(dic, '/home/maria/Desktop/TestingData.txt', filterclusters=False) #else filterclusters=clusters


