#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#this takes files that are compatible with the UCLAPL GUI and converts them to command line "Maxent2" files
import os


def fixDataFile(inpath, outpath=os.getcwd().split('code')[0], typ="learning"):
    """Converts UCLAPL GUI-compatible Learning Data file and Testing Data file to a format that the new MaxEnt Phonotactic Learner uses. Empty lines and gratuitous whitespace are removed and files are renamed. 
        """
    if typ == 'learning':
        oldfilename = 'LearningData.txt'
        newfilename = 'corpus.txt'
    if typ == 'test':
        oldfilename = 'TestingData.txt'
        newfilename = 'test.txt'
    oldfile = open(os.path.join(inpath,oldfilename), 'r', encoding='utf-8')
    newfile = open(os.path.join(outpath,'maxent2', 'temp', newfilename), 'w', encoding='utf-8')
    for line in oldfile.readlines():
        outline = line.strip().replace("  ", " ")
        if line == '\n' or line =='':
            continue
        else:
            newfile.write(outline+'\n')
    oldfile.close()
    newfile.close()

def fixFeatureFile(inpath, outpath):
        """Opens a UCLAPL GUI-compatible Features file and creates a features.txt file that works with the new MaxEnt format. adds an obligatory wb feature and 'segments' that are appropriately specified for it.
        if "mb" is one of the features, it is interpreted as "morpheme_boundary"--which means that "word boundary" will be +mb,+wb, and "morpheme boundary" will be -wb, +mb. All segments are -mb, -wb 
        """
        newfile = open(os.path.join(outpath,'features.txt'),'w', encoding='utf-8')
        with open(os.path.join(inpath, 'Features.txt'), 'r', encoding='utf-8') as oldfile:
            lines=oldfile.readlines()
        header = lines[0]
        seglines = lines[1:]
        featnames = header.strip('\n').lstrip('\t').split('\t')
        newfeatnames = ['wb'] + featnames
        newfile.write('\t'+'\t'.join(newfeatnames)+'\n')
        if not "mb" in featnames:
            newfile.write('<#' + '\t' + "+\t" +'\t'.join(len(featnames)*'0')+'\n')
            newfile.write('#>' + '\t' + "+\t" +'\t'.join(len(featnames)*'0')+'\n')
        else:
            mbloc = featnames.index('mb')-1
            #what needs to happen here is:
            #       F1  F2  F3  F4  F5  F6  F7  mb  F8  F9
            #<#     0   0   0   0   0   0   0   +   0   0
            newfile.write('<#' + "\t" + "+\t" + "\t".join((mbloc+1)*"0")+"\t+\t"+ "\t".join((len(featnames)-mbloc-2)*"0")+"\n")
            newfile.write('#>' + "\t" + "+\t" + "\t".join((mbloc+1)*"0")+"\t+\t"+ "\t".join((len(featnames)-mbloc-2)*"0")+"\n")

        for segentry in seglines:
                segentry = segentry.strip('\n').split('\t')
                newseg = segentry[0]
                featvalues=segentry[1:]
                newsegentry = [newseg, '-']+featvalues
                newfile.write('\t'.join(newsegentry)+'\n')
        newfile.close()
