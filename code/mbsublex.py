#!/usr/bin/env python3
# *-* coding:utf-8 *-*


'''
Inspects grammar for [-mb] constraints
If such constraints are found, it creates a new training data file from a segmented word corpus

then searches for morpheme structure constraints in the resulting sublexicon

'''

import os, shutil, time
import proj_maker


def search_grammar_for_mb(maxentpath=os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp')):
    grammar = proj_maker.readGrammar(os.path.join(maxentpath, 'output_baseline', 'grammar.txt'))
    natclassdic = proj_maker.getNatClasses()
    found_mb=False
    for c in grammar:
        if grammar[c]['middlegram']=='-mb':
            print('found a constraint of the form *X[-mb]Y: \n'+ c ) 
            surroundsegs = set(grammar[c]['seglists'][0]+grammar[c]['seglists'][2])
            for x in natclassdic:
                if (not x in ['-wb','-mb']) and surroundsegs.issubset(set(natclassdic[x]['segments'])):
                    print('found at least one natural class that contains both X and Y\n\n')
                    found_mb=True
                    break
        elif grammar[c]['middlegram']=='+mb':
            print('found a constraint of the form *X[+mb]Y: \n' +c)
            surroundsegs = set(grammar[c]['seglists'][0]+grammar[c]['seglists'][2])
            for x in natclassdic:
                if (not x in ['-wb','-mb']) and surroundsegs.issubset(set(natclassdic[x]['segments'])):
                    print('found at least natural class that contains both X and Y\n\n')
                    found_mb=True
                    break
    if found_mb:
        return True
    else:
        print('Either no constraints of the form *X[alpha-mb]Y found in the baseline grammar, or no superset classes were found that contain both *X and Y.')
        return False


def find_mb_symbol(maxentpath=os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp')):
    mbsegs = proj_maker.Feature('mb', os.path.join(maxentpath, 'features.txt')).plus_segs
    nonwbsegs = proj_maker.Feature('wb', os.path.join(maxentpath, 'features.txt')).minus_segs
    mbsymbol = list(set(mbsegs)&set(nonwbsegs))[0]
    return mbsymbol



def make_morph_sublexicon(maxentpath=os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp')):
    '''
    this assumes that the mbsymbol is the segment that has the value +mb in the feature file and is not wb!
    '''
    mbsymbol = find_mb_symbol(maxentpath)
    newcorpus = {} 
    with open(os.path.join(maxentpath, 'output_baseline', 'corpus.txt'), 'r', encoding='utf-8') as f:
        for line in f:
            morphs = [x.strip() for x in line.strip().split(mbsymbol) if not x=='']
            for morph in morphs:
                if morph in newcorpus:
                    continue
                else:
                    newcorpus[morph]=True
    with open(os.path.join(maxentpath, 'corpus.txt'), 'w', encoding='utf-8') as f:
        for morph in sorted(newcorpus):
            f.write(morph+'\n')


def make_freewd_sublexicon(maxentpath=os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp')):
    '''
    this assumes that the mbsymbol is the segment that has the value +mb in the feature file and is not wb!
    '''
    mbsymbol = find_mb_symbol(maxentpath)
    newcorpus = []
    with open(os.path.join(maxentpath, 'output_baseline', 'corpus.txt'), 'r', encoding='utf-8') as f:
        for line in f:
                if mbsymbol in line:
                    continue
                elif not line in newcorpus:
                    print(line)
                    newcorpus.append(line)
    with open(os.path.join(maxentpath, 'corpus.txt'), 'w', encoding='utf-8') as f:
        for morph in sorted(newcorpus):
            f.write(morph)


def move_sublex_files(kind, maxentpath=os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp')):
    '''
    creates a folder called [whatever you specify as 'kind'] inside maxent2/temp. moves simulation files into it
    '''
    simfiles = ['corpus.txt', 'maxentoutput.txt', 'tableau.txt', 'grammar.txt']
    #but crucially not params.txt, which will stay in the maxent working directory
    if not kind in os.listdir(maxentpath):
        os.mkdir(os.path.join(maxentpath, kind))
    if kind == 'output_mbsublex_baseline':
        simfiles.remove('corpus.txt')
    for x in simfiles:
        shutil.move(os.path.join(maxentpath, x), os.path.join(maxentpath, kind, x))



def rename_corpus_back(maxentpath=os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp')):
    shutil.copy(os.path.join(maxentpath, 'output_baseline', 'corpus.txt'), os.path.join(maxentpath, 'corpus.txt'))

def wrapSims(pathtotargetlocation, basepath=os.getcwd().split('code')[0], date=True, ret=False):
        '''
        the pathtotargetlocation argument specifies where you want the results of the simulation to be placed.
        all files called 'output...' and 'projections...' will be moved to the new location.
        if your features or learning data vary between simulations, set copyuserfiles to True. it defaults to 'false'
        '''
        os.chdir(basepath)
        maxentpath = os.path.join(basepath, 'maxent2', 'temp')
        if date:
                rightnow = time.strftime("%Y-%m-%d_")
        else:
            rightnow=''
        if pathtotargetlocation.startswith('sims'):
            pathtotargetlocation=os.path.split(pathtotargetlocation)[1]
            pathtotargetlocation=os.path.join(basepath, 'sims',rightnow+pathtotargetlocation)
        counter = 1
        try:
            os.mkdir(pathtotargetlocation)
        except FileNotFoundError:
            print('path to target location, file not found error ' + pathtotargetlocation)
        except FileExistsError:
            if not os.path.isdir(pathtotargetlocation+'_'+str(counter)):
                pathtotargetlocation=pathtotargetlocation+'_'+str(counter)
                os.mkdir(pathtotargetlocation)
            else:
                counter += 1
                pathtotargetlocation=pathtotargetlocation+'_'+str(counter)
                os.mkdir(pathtotargetlocation)
        if 'projections' in os.listdir(basepath) and os.listdir(os.path.join(basepath, 'projections')) == []:
                shutil.rmtree('projections', ignore_errors=True)
                files = [x for x in os.listdir(maxentpath) if x.startswith('output')]
        else:
                files = [x for x in os.listdir(maxentpath) if x.startswith('output')]
        for fi in files:
            os.renames(fi, os.path.join(pathtotargetlocation,fi))
        print('files have been moved to '+ pathtotargetlocation)
        os.chdir('code')
        if ret==True:
                return pathtotargetlocation

def makeProjection(basepath, projtype, mb):
        '''
        basepath is where the temp is located (needed to have access to original Features.txt). make it end in '/'
        type argument can be chosen from: 
                "wb" : takes word boundary-adjacent natural classes, finds all superset classes that contain them and makes a proj file for each
        '''
        maxentworkingpath=os.path.join(basepath, 'maxent2','temp')
        grammar = os.path.join(maxentworkingpath, 'output_mbsublex_baseline', 'grammar.txt')
        features = os.path.join(maxentworkingpath, 'features.txt')
        proj_maker.makeWBProj(grammar, features, maxentworkingpath, mb)



