#!usr/bin/env python3
# -*- coding: utf-8 -*-


def fopen(filepath, div = '\t', split=True):
	'''
	Usage: fopen(filepath, div = '\t', split = True)
	reads a file from specified location, 
	if 'split' is True, returns a list of lists split on tab with the newline stripped.
	if 'split' is set to False, returns a list of the file's lines.
	the separator defaults to tab (div="\t") but can be specified to any character--comma ",", space "\s", etc.
	'''
	with open(filepath, 'r', encoding='utf-8') as f:
	    readobj=f.readlines()
	if split:
	    return [x.strip('\n').split(div) for x in readobj] 
	else:
	    return readobj
