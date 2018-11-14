#!/usr/bin/env python3
# *-* coding=utf-8 *-*


'''
parameters for the maxent phonotactic learner.

If a params.txt file exists at a specified path, this gets passed to the learner directly.

Alternatively, this will create a dictionary from variables and write it to a params.txt file.
'''

import shutil, os


def move_params(inpath, basepath=os.getcwd().split('code')[0]):
    '''
    if a params.txt file exists at a specified location, this moves it to the maxent learner's temp directory
    '''
    maxentpath = os.path.join(basepath, 'maxent2', 'temp')
    shutil.copy(inpath, os.path.join(maxentpath, 'params.txt'))
    

    
def read_params():
    paramspath = os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp', 'params.txt')
    with open(paramspath, 'r', encoding='utf-8') as f:
        paramsdic = {}
        for line in f:
            param = line.strip().split('\t')[0]
            if len(line.strip().split('\t'))>1:
                value = line.strip().split('\t')[1]
            else:
                value = None
            paramsdic[param] = value
    if '-maxObsVioln' in paramsdic:
        if paramsdic['-maxObsVioln']=='0':
            viol = 'in'
        else:
            viol = 'viol_' + paramsdic['-maxObsVioln']
    else:
        viol = 'vi'
    if '-minGain' in paramsdic:
        gain = paramsdic['-minGain']
    else:
        gain = '1'
    if '-maxConSize' in paramsdic:
        consize = paramsdic['-maxConSize']
    else:
        consize = 500
    if '-gamma' in paramsdic:
        gamma = paramsdic['-gamma']
    else:
        gamma = 0 
    return(viol, gain, consize, gamma)


def scale_params(inpath=None, viol=None, gain=None, consize=None, gamma=None, multiply_by=10, keepconsize=False):
    '''
    assumes that either a path is given for reading in the parameters or the values are given by something like read_params()
    '''
    if inpath:
        with open(inpath, 'r', encoding='utf-8') as f:
            paramsdic = {}
            for line in f:
                param = line.strip().split('\t')[0]
                if len(line.strip().split('\t'))>1:
                    value = line.strip().split('\t')[1]
                else:
                    value = None
                paramsdic[param]=value
        newparamsdic = {}
        paramstomodify=['-minGain', '-gamma']
        if not keepconsize:
            paramstomodify.append('-maxConSize')
        for val in paramstomodify:
            if val in paramsdic:
                newparamsdic[val]=str(int(round(int(paramsdic[val])*multiply_by,0)))
        for x in paramsdic:
            if not x in newparamsdic:
                newparamsdic[x]=paramsdic[x]
        paramsout = os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp', 'params.txt')
        with open(paramsout, 'w', encoding='utf-8') as f:
            for param in newparamsdic:
                if newparamsdic[param]!=None:
                    f.write('\t'.join([param, newparamsdic[param]]) + '\n')
                else:
                    f.write(param+'\n')
    else:
        newgain = str(int(round(int(gain)*multiply_by,0)))
        newgamma = str(int(round(int(gamma)*multiply_by,0)))
        if keepconsize:
            newconsize = consize
        else:
            newconsize =str(int(round(int(consize)*multiply_by,0)))
        makeParams(consize=newconsize, violable=viol, mingain=newgain, gamma=newgamma)
    print('the new simulation will run with parameters modified by ' + str(multiply_by))



def makeParams(violable='violable', consize=50, mingain=50.0, select='gain', gamma=0, maxwdlength=8, pathtoparams=os.getcwd().split('code')[0]+'maxent2/temp/params.txt', compclasses=False, predefault=False, ag_disag=False):
        '''
        this creates a basic params.txt file that's passed to the command line version of the UCLAPL.
        most of the parameters should be left alone.
        'violable' controls whether the learner discovers violable constraints (in which case you should set it to violable=True) or only inviolable ones (set it to violable=False).
        predefault is an option that pre-weighs unigram constraints against every segment in the learning data, and also constraints that delimit word length distribution. by default it is turned off.
        if you want 'preefault' to be on, also make sure to turn on 'predefault' in makeSimFiles()
        '''
        pathtoparams=os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp', 'params.txt')
        paramsdic={'features':{'value':'features.txt', 'comment':''},
                'projections': {'value': 'projections.txt', 'comment': None},
                'corpus': {'value':'corpus.txt', 'comment': None},
                'l2': {'value': '0.00001', 'comment': 'scale of L2 weight regularizer'},
                'test': {'value': 'test.txt', 'comment':'test on forms after learning, writing tableau.txt'},
                'train': {'value': None, 'comment': 'train weights and write grammar.txt after selection'},
                'maxWordLength': {'value': str(maxwdlength), 'comment':None},
                'maxConSize': {'value': str(consize), 'comment': 'max. number of constraints to learn'},
                'evaluator': {'value': select, 'comment': 'options are "gain", "observedOverExpected", "grafting"'},
                'select':{'value': None, 'comment': None},
                'gamma':{'value': str(gamma), 'comment': None}
                #'doNotPruneConstraints':{'value':None, 'comment': None}
                #'complementClasses':{'value':None, 'comment': None}
                }
        #if paramsdic['gamma']['value']=='0':
        #    paramsdic['l2']={'value':'0.00001', 'comment':'scale of L2 weight regularizer'}
        if compclasses:
            paramsdic['complementClasses']={'value':None, 'comment':None}
            paramsdic['doNotPruneConstraints']={'value':None,'comment':None}
        if select=='gain':
            paramsdic['minGain']= {'value':str(mingain), 'comment': 'threshold that constraint must exceed to be learned'}
        elif select=='observedOverExpected':
            print("observedOverExpected is not implemented in this version, sorry--please use the 2008 GUI")
            pass    
            #'doNotAddStarSeg' : {'value': None, 'comment': None}
        if violable == 'inviolable':
            paramsdic['maxObsVioln']= {'value': '0', 'comment':'maximum number of observed violations is Zero; it means only inviolable constraints are learned.'}
        elif violable=='inviolable':
            paramsdic['maxObsVioln']={'value': None, 'comment': None}
        if predefault==True:
            paramsdic['grammar']={'value':'baseline_grammar.txt', 'comment': 'wd length constraints and anti-seg constraints pre-included as defaults.'}
        if ag_disag==True:
            paramsdic['grammar']={'value':'baseline_grammar.txt', 'comment': 'agree and disagree constraints pre-included in baseline grammar.'}
        params=open(pathtoparams, 'w', encoding='utf-8')
        for param in paramsdic:
                line = '-'+ param
                if paramsdic[param]['value']!=None:
                    line = line +'\t' + paramsdic[param]['value']
                if paramsdic[param]['comment']!=None:
                    line = line + '\t' + ' # ' + paramsdic[param]['comment']
                line = line + '\n'
                params.write(line)
        params.close()

