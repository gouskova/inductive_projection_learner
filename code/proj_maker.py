#!/usr/bin/env python3

import os

#custom modules

import natclasses
import fileopen as fo

#import matplotlib.pyplot as plt

path = os.getcwd().split('code')[0]


#===================================================================================
#"segs" and "features" dictionaries. 'segs' just has a feature value listing for each segment. segdict is a feature name + value pairing dictionary. segsnozero is the same thing as segs only does not include zero values
#===================================================================================

def segsFeats(featfilepath):
	'''
	input argument: path to Features.txt.
	output 1: segs, a dictionary of segments along with all the feature values (+cont, 0str, etc.)
	output 2: segsnozero, a dictionary of segments with only the non-zero feature values (+cont but not 0str)
	output 3: features, a list of feature names

	the Features.txt file needs to be in the standard 2009 UCLAPL GUI format, i.e., tab separated, no 'word_boundary' segment defined in the list of segments, and the first line starts with an empty tab and then feature names.
	'''
	with open(featfilepath, 'r', encoding='utf-8') as featurefile:
		feat_file = featurefile.readlines()
	features = feat_file.pop(0).lstrip("\t").rstrip("\n").split("\t")
	segs = {}
	for line in feat_file:
		line=line.rstrip("\n").split("\t")		
		seg=line[0]
		segs[seg]=[]
		for feature in features:
			i = features.index(feature)
			segs[seg].append(str(line[i+1])+str(feature))
	segsnozero = {}
	for line in feat_file:
		line=line.rstrip("\n").split("\t")		
		seg=line[0]
		segsnozero[seg]=[]
		for feature in features:
			i = features.index(feature)
			if line[i+1]!='0':
				segsnozero[seg].append(str(line[i+1])+str(feature))
	if 'wb' not in features:	
		features.append('word_boundary')
	return(segs, segsnozero, features)



#====================================================================================
#this grammar dictionary gets used in the projection making functions later 
#====================================================================================


def readGrammar(gramfile, newMaxEnt=True):
	'''
	first argument is a path to the grammar file, grammar.txt
	tne function reads in the grammar.txt file from a specified output directory. returns a dictionary with constraint keys and tiers, weights, and features as values. takes newMaxEnt argument that is "TRUE" or "FALSE". some special handling required for grammar output of new maxent learner, especially the word boundary feature.
		a few of the functions were originally supposed to work with either the old command line version underlying the GUI or with the newer one. i never cleaned up this but everything defaults to the newer maxent version now
	'''
	gramdic={}
	grammar = fo.fopen(gramfile)
	for line in grammar:
		if not newMaxEnt:
			constraint = line[0]
			tier=line[1].lstrip('(tier=').rstrip(')')
			weight = line[2]
			feats = line[0].lstrip("*").replace("][", ",").rstrip("]").lstrip("[").split(',')
			natclasses = constraint.strip('[]').split('][')
			natclasses_commaless = natclasses.replace(',',"")
			gramdic[constraint]={'tier':tier,'weight':weight, 'features':feats, 'natclasses':natclasses,'natclasses_nocomma' :natclasses_commaless}
		if newMaxEnt:
			if line[0]=='projection':
				continue
			else:
				tier = line[0]
				weight = line[2]
				constraint = line[1]
				segs = line[-1]
				if constraint=='*[]':
					constraint = constraint.replace('*[]', '*[-wb,+wb]')
					feats = ['-wb','+wb'] 
					natclasses=['-wb,+wb']
				else:
					feats = line[1].lstrip("*").replace('[]','[-wb,+wb]').replace("][", ",").strip("[]").split(',')
					natclasslist=line[1].lstrip("*").replace('[]','[-wb,+wb]').split('][')
					natclasses = [cl.strip('[]') for cl in natclasslist]
					natclasses_commaless=[cl.strip('[]').replace(',', '') for cl in natclasslist]
					seglist=segs.strip('()').split(')(')
					if len(natclasslist)==3:
						firstgram = natclasslist[0].strip('[]')
						middlegram=natclasslist[1].strip('[]')
						thirdgram = natclasslist[2].strip('[]')
					else:
						middlegram,firstgram,thirdgram=None,None,None
					gramdic[constraint]={'tier':tier,'weight':weight, 'features':feats, 'middlegram':middlegram, 'firstgram':firstgram, 'thirdgram':thirdgram, 'natclasses':natclasses, 'natclasses_nocomma':natclasses_commaless, 'segblocks':seglist, 'seglists':[x.split('|') for x in seglist]} 
	return gramdic
	

#====================================================================================
#the supplied methods list all the weights and constraints and tiers in the grammar, as well as ordered triplets of weights-constraints-tiers, and a dictionary of weights and constraints
#====================================================================================

class Grammar:
	'''
	packages the output of readGrammar() into methods. requires grammar.txt to exist
	'''
	def __init__(self, gramfile):
		grammar = readGrammar(gramfile)
		self.constraints = list(grammar.keys())
		weights = []
		tiers = []
		for cons in grammar:
			weights.append(grammar[cons]['weight'])
			tiers.append(grammar[cons]['tier'])
		self.weights = weights
		if any([x=='0' for x in self.weights]):
			self.duds=[c for c in grammar if grammar[c]['weight']=='0']
		else:
			self.duds="the grammar has no constraints with zero weights"	
		self.tiers = tiers
		if all([x =='default' for x in self.tiers]):
			self.name = 'default'
		else:
			nondefaulttiers = [x for x in self.tiers if x !='default']
			self.name = nondefaulttiers[0]
		self.c_w_t = list(zip(self.constraints, self.weights, self.tiers))
		self.c_w = dict(zip(self.constraints, self.weights))	
		self.c_t = dict(zip(self.constraints, self.tiers))

#====================================================================================

class Feature:
	"""
	example: Feature('son', '~/blah/Features.txt').plus_segs 
	'l', 'm', 'n', 'r', 'w', 'j'
	
	returns plus and minus versions of each feature, lists segments associated with them, and counts the overall freq of mention for the feature as well as plus and minus versions. doubles as a feature-to-segment mapper, though only for one feature at a time.
	"""

	def __init__(self, fname, featfilepath):
		segs = segsFeats(featfilepath)[0]
		self.name = fname
		self.plus_f = "+"+fname
		self.minus_f = "-"+fname
		self.plus_segs=[seg for seg in segs if self.plus_f in segs[seg]] 
		self.minus_segs=[seg for seg in segs if self.minus_f in segs[seg]] 
		self.plusfreq=0
		self.minusfreq=0
		self.overall_freq=0
		if featfilepath.endswith('features.txt'):
			pass
		elif featfilepath.endswith('Features.txt'):
			if self.name == 'word_boundary' or self.name=='wb':
				self.minus_segs = list(segs.keys())
				self.plus_segs = ['<#','#>']
	def count_freq(self, item):
		if item == self.plus_f:
			self.plusfreq+=1
		if item == self.minus_f:
			self.minusfreq+=1
		self.overall_freq=self.plusfreq+self.minusfreq



class PrintFeature:
	"""
	returns the features that have non-zero value when a plus or a minus value of a feature is specified, as well as feature values shared by all the segs that have the value, and features that can contrast in a binary way. Plus some printable versions of them.
	"""
	def __init__(self, fname, featfilepath, newMaxEnt=True):
		segsFtuple = segsFeats(featfilepath)
		features = segsFtuple[2]
		segsnozero = segsFtuple[1]
		self.name=fname
		self.nonzero_features=[]
		self.entailed_features=[]
		self.contrastive_features=[]
		self.tiername=fname
#		self.tiername=fname.lstrip(fname[0]).capitalize()
		#plus version of the feature:
		self.segs = [seg for seg in segsnozero if fname in segsnozero[seg]]
		#if feature is in a seg's listing, append all its nonzero feats to list 
		for seg in self.segs:
			for feat in segsnozero[seg]:
				if feat in segsnozero[seg] and feat not in self.nonzero_features:
					self.nonzero_features.append(feat.lstrip('+-'))
		self.nonzero_features = list(set(self.nonzero_features))
		if newMaxEnt:
			self.nonzero_features.append("wb")
		else:
			self.nonzero_features.append("word_boundary")
		#contrastive is a subset of nonzero but we're finding the set a bit differently
		for feature in features:
			feature=Feature(feature, featfilepath)
			if (feature.plus_f in self.nonzero_features) and (feature.minus_f in self.nonzero_features):
				self.contrastive_features.append(feature.name)
			if feature.plus_f in self.nonzero_features and feature.minus_f not in self.nonzero_features:
				self.entailed_features.append(feature.plus_f)
			elif feature.minus_f in self.nonzero_features and feature.plus_f not in self.nonzero_features:
				self.entailed_features.append(feature.minus_f)
		self.nonzero_printable=','.join(self.nonzero_features)
		self.entailed_printable=','.join(self.entailed_features)
		self.contrastive_printable=','.join(self.contrastive_features)
		if not newMaxEnt: #these are for the GUI version
			self.contrastive_features.append("word_boundary")
			self.entailed_features.append("word_boundary")
			self.nonzero_printable=','.join(self.nonzero_features)+',word_boundary' 
			self.contrastive_printable=','.join(self.contrastive_features)+',word_boundary' 
			self.entailed_printable=','.join(self.entailed_features)+',word_boundary' 



#====================================================================================

#writing the projections file

def makeDefaultProj(path, featfile, ngrams=3, CV=False, outwrite=True):
	"""
	The New MaxEnt learner requires a default projection to be defined.
	arguments: path is the location of the projections file where the output is supposed to be written; 
	featfile is the location of Features.txt
	ngrams is how the setting is passed to the learner; defaults to 3
	CV is either True or False; setting determines whether +syllabic and -syllabic are tested as part of the baseline run. The feature that divides the set into consonants and vowels can be called "syllabic" or "syll" or "syl". If no such feature is found, the learner will say so
	"""
	default = 'default\tany\tall\t'+str(ngrams)
	consonantal=""
	vocalic=""
	if CV:
		features = set(segsFeats(featfile)[2])
		CVfeats = set(['syllabic', 'syll', 'syl'])
		if len(features & CVfeats)!= 1:
			CVfeatError = 'Your Features.txt file does not have a C/V feature with a standard name. Please add a feature named "syllabic", "syll", or "syl" and specify the values for all the segments in the list so that a Consonantal and a Vocalic tier can be added to the baseline projection run.'
			raise CVfeatError
		else:	
			syllabicfeat=list(features & CVfeats)[0]
			Cons_feats_to_project = PrintFeature('-'+syllabicfeat, featfile).nonzero_printable			
			consonantal = 'Consonantal'+ '\t-' + syllabicfeat + '\t' + Cons_feats_to_project + '\t'+ str(ngrams)
			Voc_feats_to_project = PrintFeature('+'+syllabicfeat,featfile).nonzero_printable
			vocalic = 'Vocalic'+ '\t+' + syllabicfeat + '\t' + Voc_feats_to_project + '\t' + str(ngrams)		
	if outwrite:
		f = open(os.path.join(path, 'projections.txt'), 'w', encoding='utf-8')
		f.write(default+'\n')
		if CV:
			f.write(consonantal +'\n') 
			f.write(vocalic)
		f.close()
	else:
		return([default,consonantal,vocalic])
		

#===========================================================================================

def getNatClasses():
	'''
	the output of this function is a dictionary of nat classes.
	structure: '+son-cont' {'features': ["whatever"], 'segments': ["whatever"], 'classname': "+son,-cont"}
	'''
	return natclasses.packNatClasses()

#===========================================================================================

def isNatSubset(cl1, cl2):
	'''
	checks if cl1 is a subset of cl2; returns cl1 if true
	returns cl2 if c1 is a superset of cl1
	returns 'overlap' and 'disjunctive' if the classes are not in a superset relationship, as approrpiate
	'''
	natclasses = getNatClasses()
	segs1 = set(natclasses[cl1]['segments'])
	segs2 = set(natclasses[cl2]['segments'])
	if segs1.issubset(segs2):
		return(cl1)
	elif segs2.issubset(segs1):
		return(cl2)
	elif len(segs1&segs2)>0:
		return "overlap"
	elif len(segs1&segs2)==0:
		return 'disjunctive'

#===========================================================================================
#the nonzero features associated with a natural class's segments 
#===========================================================================================
		
def findFeatsToProject(featfilepath):
	"""
	featfilepath is the location of Features.txt associated with this run
	also requires a list of segments and the nonzero features they are associated with.
	returns a dictionary of non-zero features associated with each natural class, and those features plus "wb" for the purposes of writing a projection file.
	'morph_boundary' adds 'mb' to the class of features that get projected onto every projection. The function will check whether 'mb' is in the feature file. If it is but the segment is not in the data file, that's not a problem.
        Because of the way projections work in the command line version of the maxent learner, the procedure for creating a projection that includes a morpheme boundary is a bit different: it compiles a natural class that includes all the segments from the natural class in question, but returns the segment list plus the [+mb] symbol and NOT a natural class with those segs.
        """
	segsFeatuple = segsFeats(featfilepath) #first is segslist, then segsnozero, then featnames
	nclassdic=getNatClasses()
	for natclass in nclassdic:
		nclassdic[natclass]['nonzerofeats']=[]
		nclassdic[natclass]['featstoproject']=['wb']
		segs = nclassdic[natclass]['segments']
		nclassdic[natclass]['segments']=segs
		for boundary in ["<#", "#>"]:
			if boundary in segs:
				segs.remove(boundary)
		for seg in segs:
			for otherseg in segs:
				try:
					segentry = segsFeatuple[1][seg]
					othersegentry = segsFeatuple[1][otherseg]
				except KeyError:
					print("first seg: " + seg+ '\n otherseg: ' + otherseg)
					print('seg entry: '+ str(segentry))
					print('other seg entry: '+ str(othersegentry))
					#print(nclassdic)
					pass
				nonzerofeats = set(segentry) & set(othersegentry)
				for feat in nonzerofeats:
					if feat not in nclassdic[natclass]['nonzerofeats'] and feat not in nclassdic[natclass]['features']:
						nclassdic[natclass]['nonzerofeats'].append(feat)	
		for feat in nclassdic[natclass]['nonzerofeats']:
			strippedfeat = feat.strip("+-")
			if strippedfeat not in nclassdic[natclass]['featstoproject']:
				nclassdic[natclass]['featstoproject'].append(strippedfeat)
	return nclassdic


		
#=========================================================================================
def makeWBProj(pathtogrammarfile, featpathfile, outputpathdir, mb, ngrams = '2\t3', defaultngram=3):
	"""
	pathtogrammarfile: the path to output_baseline/grammar.txt
	featpathfile: the path to data/language/Features.txt
	outputpathdir: the path to where projections.txt will be written
	ngrams: maximal size of a projection-based constraint. defaults to 3
	multi: if true, everything is in its own file, named after the nat class. if false, everything is in one file
	goes through the constraints of a baseline grammar. if -wb is mentioned, get the natural classes to either side of -wb, and make projections from them.
                in the baseline grammar, usually the constraints will mention [] rather than [-wb]---this is the class that includes [-wb] and [+wb], i.e., any position. ETA: [-mb] as well, since for segments, this is the same class as [-wb].
	note that only trigram constraints will be examined. the constraint in question has to look something like *[+low][-wb][-high,-low]--as in Hayes and Wilson's baseline Shona grammar
	requires access to natural class information, which is collected previously into featsprintabledic (using proj_maker.findFeatsToProject())
	"""
	nclassdic = findFeatsToProject(featpathfile)
	grammar=readGrammar(pathtogrammarfile)
	join_char = '\t' 
	defproj = ['default', 'any', 'all', str(defaultngram)]
	projlist = []
	for c in grammar:
		if c=='[+mb][][+mb]' or c.startswith('[-wb,+mb]') or c.endswith('[-wb,+mb]'):
			continue
		else:
			allsuperclasses = []
			if (len(grammar[c]['natclasses'])==3) and ('+wb' not in grammar[c]['natclasses']) and ('+copy' not in grammar[c]['natclasses']) and ('-wb' in grammar[c]['features'] or '-mb' in grammar[c]['features']):
				natclasses = grammar[c]['natclasses_nocomma']
				if natclasses[1] in ['-wb', '-mb', '-wb+wb']: #this is the placeholder clause: [], [-mb], or [-wb] define "any segment"
					try:
						prevclass=natclasses[0]
						follclass=natclasses[2]
						prevsegs = nclassdic[prevclass]['segments']
						follsegs = nclassdic[follclass]['segments']
						allthesegs = set(prevsegs + follsegs)
						superclasses = sorted([x for x in nclassdic if set(nclassdic[x]['segments']).issuperset(allthesegs) and x!='' and x not in ['-wb', '-mb']], key=lambda x: len(nclassdic[x]['segments']))
					except:
						print(c)
						print('\n\n\n\n')
						print(natclasses)
						print('\n\n\n\n')
						print(grammar)
						print('\n\n\n\n')
						print(nclassdic)
					if len(superclasses)>0:
						smallest = superclasses[0]
						allsuperclasses.extend([x for x in superclasses if len(nclassdic[x]['segments']) == len(nclassdic[smallest]['segments'])]) 
						if len(allsuperclasses)>1:
							print('\nplaceholder constraint found: ' +c + ' \nconstructed several projections for natural classes because there is more than one superset natural class encompassing the segments to either side of the placeholder, and there is no "shortest" class')
						elif len(allsuperclasses)==1:
							print('\nplaceholder constraint found: ' + c + '\nconstructed a projection for the smallest natural class : \n' + smallest)
					else:
						print('\nplaceholder constraint found: ' + c + '\nbut, no superset classes exist that include both classes to either side of the placeholder')
				else:
					continue
			projlist.extend(allsuperclasses)
	projlist = list(set(projlist))
	if len(projlist)==0:
			print('no placeholder constraints were found in the baseline grammar.')
	else:    
		projection_file = open(os.path.join(outputpathdir, 'projections.txt'), 'w', encoding='utf-8')
		projection_file.write(join_char.join(defproj) + '\n')
		for cl in projlist:
			if (cl == '+mb') or (cl == '-wb+mb'):
				continue
			else:
				feats_to_project = ','.join(nclassdic[cl]['featstoproject'])
				if mb:
					defin_feats = '{'+','.join(nclassdic[cl]['segments'])+','+','.join(nclassdic['+mb']['segments'])+'}' 
				else:
					defin_feats = nclassdic[cl]['classname']
				projection_file.write(join_char.join([cl, defin_feats, feats_to_project, str(ngrams)+'\n']))
		projection_file.close()
		print('\ndone making a combo projection file from "-wb"-mentioning constraints')


#=========================================================================================
# a custom projection maker given a feature value
#=========================================================================================
def makeHandmadeProj(pathtoprojfile, feature, featpathfile, ngrams="2\t3", defaultngram=3):
	defproj = ['default', 'any', 'all', str(defaultngram)]
	join_char='\t'
	feats_to_project=PrintFeature(feature, featpathfile).nonzero_printable
	projection_file=open(os.path.join(pathtoprojfile,'projections.txt'), 'w', encoding='utf-8')
	projection_file.write(join_char.join(defproj)+'\n')
	projection_file.write(join_char.join([feature, feature, feats_to_project, str(ngrams)]))
	projection_file.close()


