#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fileopen, random, os, sys

'''
this script creates a random sample of 1/5th of the data from the learning data, which becomes 'test.txt', and then asves the remaining 4/5ths of the learning data into a file called 'corpus.txt'.

it actually duplicates a capability of the java maxent utility
'''

codedir = os.getcwd()
if codedir.endswith('code'):
        if codedir not in sys.path:
                sys.path.append(codedir)
				

def makeRandomTestFile(inpath, testoutpath, learnoutpath, samplesize = 1/5, **kwargs): 
        """
        arg1: the path to directory containing corpus.txt
        arg2: testoutpath, a path to where you want your test file sampled from arg1
        arg3: learnoutpath, where do you want your remainder of inpath file to be placed
        arg4: portion of the learning data file that you want to use for testing. defaults to 1/5. can be given as fractions or as decimals (less than 1)
        """
        learndata = fileopen.fopen(inpath, split=False)
        #get the size of random sample to create:
        lenth = len(learndata)
        if 'samplerate' not in kwargs:
            samplelenth = int(lenth * samplesize)
        #do the random sampling to make a test list, put all the remaining words in a new learning data list:
        testsample = random.sample(learndata, samplelenth)
        learnremainder = [word for word in learndata if not word in testsample]
        #write to file:
        with open(learnoutpath, 'w', encoding='utf-8') as learndatafile:
            for word in learnremainder:
                learndatafile.write(word)
        with open(testoutpath, 'w', encoding='utf-8') as testdatafile:
            for word in testsample:
                testdatafile.write(word)
        print('created sampling test data using ' + str(samplesize) + ' of the learning data')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='help')
    parser.add_argument('--input', help='full path to input file to sample data from')
    parser_add_argument('--output', help='full path to output file to save sampled data to')
    parser.add_argument('--residue', help='full path to where to save remainder of input file')
    parser.add_argument('--samplerate', help='what portion of the learning data should be used for sampling? e.g., "0.5" for 50%, or "0.001" for 1%', const=0.1, type=float, default=0.1)
    parser.add_argument('--slicelength', help='optional argument; if set, the learning data will be randomly sampled to get a file of length "slicelength".')

