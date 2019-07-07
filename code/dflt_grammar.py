#!/usr/bin/env python3
#*-* coding: utf-8 *-*

import os

'''

the gain-based learner as described in Wilson and Gallagher's LI squib is pre-initialized with constraints against all word lengths and constraints against individual segments. this module creates the default file based on a LearningData.txt datafile and a features file that describes all the segments

it opens the LearningData.txt file and finds the longest length of word in it, and creates constraints on the default projections that describe the lengths of the words up to the highest lengths.

it also writes constraints against each segment in the Features.txt file to the default grammar file.
'''

def learnDataMeasure(lgpath):
	'''
	finds the longest word in the dataset at the location 'lgpath'
	'''
	with open(lgpath, 'r', encoding='utf-8') as ld:
		lenth = 0
		for line in ld:
			linelenth = len(line.rstrip('\n').split(' '))
			if linelenth>lenth:
				lenth = linelenth
	return lenth

def collectSegs(featpath):
	'''
	returns a list of all the segments mentioned in the Features.txt file, which is at 'featpath'
	'''
	with open(featpath, 'r', encoding='utf-8') as f:
		feat_file = f.readlines()[1:]
		segs = [x.split('\t')[0] for x in feat_file]
	return segs

def makeDefGramFile(lgpath, path=os.getcwd().split('code')[0]):
	'''
	creates a file called 'baseline_grammar.txt' that has constraints in it against words of various lengths, consisting of segments.
	*[-wb]
	*[-wb][-wb]
	*[-wb][-wb][-wb]
	and so on (and minus the *)
	'''
	maxentpath = os.path.join(path, 'maxent2', 'temp')
	ldlength = learnDataMeasure(os.path.join(lgpath, 'LearningData.txt'))
	segs = collectSegs(os.path.join(lgpath, 'Features.txt'))
	with open(os.path.join(maxentpath, 'baseline_grammar.txt'), 'w', encoding='utf-8') as out:
		for seg in segs:
			out.write('default\t*(%s)\n' % seg)
		for n in range(ldlength+1):
			out.write('default\t*[+wb]'+n*'[-wb]'+'[+wb]\n')



