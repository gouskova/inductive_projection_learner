#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
this is a utility function for checking data for the UCLAPL learner (command line version)
it goes through a file called LearningData.txt, and checks it against your Features.txt file 
if any segments turn up that aren't in both files, the function alerts you.

usage:
    datachecker.findOrphans('/home/you/WordListFile.txt', '/home/you/Featfile.txt')
'''

import proj_maker

def collectLDSegs(somepath):
	segs = []
	try:
		with open(somepath, 'r', encoding='utf-8') as ldatafile:
			for line in ldatafile:
				wordsegs = line.strip('\n').split('\t')[0].split()
				for seg in wordsegs:
					if not seg in segs:
						segs.append(seg.strip())
	except FileNotFoundError:
		print("\n\n\nNo LearningData.txt file at " + somepath + '\n\n\n\n')
	return segs

def collectFSegs(somepath):
	return proj_maker.segsFeats(somepath)[0].keys()

def findOrphans(learningdata, featurefile, verbose=False):
	learningdatasegs = collectLDSegs(learningdata)
	featurefilesegs = collectFSegs(featurefile)
	for x in ['+', '-', '*', '|']:
		if x in featurefilesegs:
			print("Please do not use " + x + "in your segment list. Choose a symbol that is not used in regular expressions.")
	if verbose:
		print("\nThe segments in your data file are: \n %s" % ','.join(sorted(learningdatasegs)))
		print("\nThe segments in your Features.txt file are: \n %s" % ','.join(sorted(featurefilesegs)))
	orphans = list(set(learningdatasegs) - set(featurefilesegs))
	if len(orphans)==0:
		print('\nAll the segments are defined in the feature file.')
	else:
		if verbose:
			print('\nyour orphan segments are: ' + ','.join(orphans))
			return orphans
		else:
			#pass
			return orphans



if __name__ == '__main__':
	import sys
	helpmessage = 'please provide the full locations of the learning data file and the feature file as follows: \n$ python3 datachecker.py /home/me/Desktop/LearningData.txt /home/me/Desktop/Features.txt'
	if len(sys.argv)>1:
		learningdata=sys.argv[1]
		featurefile = sys.argv[2]
		print('learning data: ' + learningdata)
		print("feature file: " + featurefile)
		findOrphans(learningdata, featurefile, verbose=True)
	else:
		try:
			findOrphans(learningdata, featurefile, verbose=True)
		except FileNotFoundError:
			print (helpmessage)
