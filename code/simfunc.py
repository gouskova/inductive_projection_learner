#!/usr/bin/env python3
# *-* coding: utf-8 *-*

#standard modules
import os, shutil, subprocess, time, itertools

#custom modules
import fileopen as fo
import proj_maker, fix_input_files, datasampler, dflt_grammar, agree_disagree



def cleanUpWorkdir(basepath, removeprojfile=True, cleanoutput = True, igerr=True):
        """
        removes the contents of maxentworkingpath and empties the projections directory
        everything inside maxentworkingpath (see below for location of that) will be overwritten each time this is run
        basepath is the directory that contains 'code' and maxent2.
        cleanoutput will delete any directory that starts with 'output' inside basepath. (not recursively)
        if you want to be more cautious, set 'igerr' to "False"; the default is to ignore errors thrown up by rmtree deletion function.
        """
        if not 'code' in os.listdir(basepath) or not 'maxent2' in os.listdir(basepath):
                print('there is no "code" folder inside the base path folder you entered. please check location and try again.')
        maxentworkingpath = os.path.join(basepath,'maxent2','temp')
        projdir = os.path.join(basepath,'projections')
        if 'temp' in os.listdir(basepath):
                shutil.rmtree(os.path.join(basepath,'temp'), ignore_errors=igerr)
        if 'temp' in os.listdir(os.path.join(basepath,'maxent2')):
            if removeprojfile:
                shutil.rmtree(maxentworkingpath, ignore_errors=igerr)
                os.mkdir(maxentworkingpath)
            if not removeprojfile:
                files = [x for x in os.listdir(maxentworkingpath) if not x=='projections.txt']
                for x in files:
                    os.remove(os.path.join(maxentworkingpath, x))
                #os.mkdir(maxentworkingpath)
        else:
                os.mkdir(maxentworkingpath)
        if 'projections' in os.listdir(basepath):
                shutil.rmtree(projdir, ignore_errors=igerr)
                os.mkdir(projdir)
        else:
                os.mkdir(projdir)
        if cleanoutput:
                outdirs = [x for x in os.listdir(basepath) if x.startswith('output') or x.startswith('projections') or x == 'alsorans']
                for x in outdirs:
                                shutil.rmtree(os.path.join(basepath, x), ignore_errors=igerr)
#        if not 'output_baseline' in os.listdir(basepath):
#                os.mkdir(os.path.join(basepath,'output_baseline'))
#        for folder in os.listdir(basepath):
#                if folder.endswith('Projection'):
#                        shutil.rmtree(os.path.join(basepath,folder), ignore_errors=igerr)

        
def makeSimFiles(language, outpath=os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp'), testDataToUse=1/5, predefault=False, ag_disag=False):
        """
        makes corpus.txt, test.txt, learning.txt files compatible with the command line learner
        If not given a test data file, it will use 1/5th of the learning data file to make a random subset (or the amount you specify in the last arg)
        """
        inpath = os.path.join(os.getcwd().split('code')[0], 'data', language)
        fix_input_files.fixFeatureFile(inpath, outpath)
        #make a test file from 1/5th of the data, then make a learning file from what remains
        if "TestingData.txt" in os.listdir(inpath):
                fix_input_files.fixDataFile(inpath, typ = 'test')
                fix_input_files.fixDataFile(inpath, typ='learning')
        #otherwise we'll make one out of 20% of your learning data and withhold it:
        else:
                #converting LearningData.txt to 'corpus.txt':
                fix_input_files.fixDataFile(inpath, typ='learning')
                corpath = os.path.join(outpath, 'corpus.txt')#'LearningData.txt')
                testdatapath = os.path.join(outpath, 'test.txt')#'TestingData.txt')
                newlearndatapath = os.path.join(outpath,'subcorpus.txt')
                #make a random sample file using specified amount of data
                datasampler.makeRandomTestFile(corpath, testdatapath, newlearndatapath, testDataToUse)        
                #fix_input_files.fixDataFile(testdatapath, typ='test')
                os.remove(os.path.join(outpath, 'corpus.txt'))
                os.rename(os.path.join(outpath, 'subcorpus.txt'), os.path.join(outpath, 'corpus.txt'))
        #if you want to turn on the preselection option
        if predefault:
            dflt_grammar.makeDefGramFile(inpath)
        if ag_disag:
            agree_disagree.make_gram_file()


def copyTestFiles(grammarpath, testfilepath):
    '''
    for testing an existing grammar.
    this copies a grammar.txt file and a projections.txt file to the maxent directory, and a test file and a features file to the maxent directory
    grammarpath leads to the locatioon of grammar.txt, and testfilepath to TestingData.txt.
    '''
    maxentpath = os.path.join(os.getcwd().split('code')[0], 'maxent2', 'temp')
    testfiledir = testfilepath.split('TestingData.txt')[0]
    fix_input_files.fixFeatureFile(testfiledir, maxentpath)
    fix_input_files.fixDataFile(testfiledir, typ='test')
    with open(os.path.join(maxentpath, 'params.txt'), 'w', encoding='utf-8') as f:
            f.write('-test\ttest.txt\n-grammar\tgrammar.txt\n-projections\tprojections.txt\n-features\tfeatures.txt')
    shutil.copy(grammarpath, os.path.join(maxentpath, 'grammar.txt'))
    projections = os.path.join(grammarpath.split('grammar.txt')[0], 'projections.txt')
    shutil.copy(projections, os.path.join(maxentpath, 'projections.txt'))

def makeJarPaths(basepath):
        """
        do not call this function directly, it gets invoked by setJVOptions.
        this just pastes a bunch of jar files together into a path that gets passed to the java run of maxent.
        by default, jardir will be in basepath+'maxent2/jar'
        returns a string that is passed to setJVOptions (the function will be called via the basepath arg)
        """
        jardir = os.path.join(basepath,'maxent2','jar')
        extdir = os.path.join(basepath,'maxent2','extern')
        jarfiles = [x for x in os.listdir(jardir) if not x.startswith('.')]
        extjarfiles = [x for x in os.listdir(extdir) if not x.startswith('.')]
        jarpaths = [os.path.join(jardir, x) for x in jarfiles]
        extpaths = [os.path.join(extdir, x) for x in extjarfiles]
        alljar=':'.join(jarpaths+extpaths)
        return alljar

def setJVOptions(basepath, reducemem=True, timeoutinsec=False):
        '''
        do not call this directly, it gets called by one of the simulation functions (runBaselineSim, for example)
        basepath is where maxent2 is located (see makeJarPaths)
        reducemem should be set if you are working with limited RAM. Something around 4GB is not enough to run certain complex simulations; for example, Quechua runs on that setting but Latin does not.
        timeout should be set to something other than False if you are pressed for time. timeout=1000 will set it to 1000 seconds (16.6 min)
        '''
        alljar = makeJarPaths(basepath)
        JVOptions = ['java', '-cp', alljar, 'edu.jhu.maxent.Maxent', 'params.txt'] #-cp adds the files listed in alljar to classpath; add it every time     
        if reducemem:
                JVOptions.append('-Xmx2g')
        if timeoutinsec:
                JVOptions.append('timeout='+str(timeoutinsec))          
        return JVOptions

def getMaxentHelp(basepath=os.getcwd().split('code')[0]):
    '''
    this is dumb but probably helpful. it allows you to call the help file without having to put all the paths in the command line.
    '''
    os.chdir(os.path.join(basepath,'maxent2'))
    alljar = makeJarPaths(basepath)
    JVOptions = ['java', '-cp', alljar, 'edu.jhu.maxent.Maxent', '-help']
    gethelp=subprocess.run(JVOptions)
    os.chdir(basepath)


def saveNatClasses(featfile=os.path.join('maxent2', 'temp', 'features.txt')):
    '''
    calls features.jar, which makes a natural classes file
    packages everything into a dictionary
    the featfilepath should point to a file that's been processed by fix_input_files.fixFeatureFile.
    this normally happens in the course of running a simulation, but a normal place for it is in maxent2/temp/features.txt.
    '''
    basepath=os.getcwd().split('code')[0]
    os.chdir(os.path.join(basepath,'maxent2'))
    alljar = makeJarPaths(basepath)
    features = os.path.join(basepath, featfile)
    JVOptions = ['java', '-cp', alljar, 'edu.jhu.features.NaturalClasses', features]
    natclassfile = open(os.path.join(basepath,'maxent2','temp', 'naturalclasses.txt'), 'w', encoding='utf-8')
    natclassprocess = subprocess.run(JVOptions, check=True, stdout=natclassfile)
    natclassfile.close()
    os.chdir(basepath)


def readNatClasses(cleanup=False):
    basepath = os.getcwd().split('code')[0]
    natclassfile = os.path.join(basepath,'maxent2', 'temp', 'naturalclasses.txt')
    nclassdic= {}
    natclasses = open(natclassfile, 'r').readlines()
    for line in natclasses[1:]:
        line = line.strip().split('\t')
        classname = line[1].strip('[]').replace(',', '')
        simname = line[1].strip('[]')
        features = simname.split(',')
        segments = line[2].strip('()').split(',')
        nclassdic[classname] = {'features': features,
            'segments': segments,
            'classname': simname
            }
    if cleanup:
        os.remove(natclassfile)
    return nclassdic
 
def runBaselineSim(basepath, reducemem=True, timeoutinsec=False, rt_output_baseline=True):
        """
        this will run a simulation with just a default projection.
        basepath is the location of maxent2/temp.
        if you don't go with the default, make sure your selections work with what cleanUpWorkdir is doing
        reducemem will have to be reset to "True" in the code itself, as will timeoutinsec
        (these reduce working memory demands and set a default timeout setting for simulations; might be needed if you are working on a slow computer)
        """
        JVOptions = setJVOptions(basepath, reducemem, timeoutinsec)
        maxentoutput=open(os.path.join(basepath, 'maxent2', 'temp', 'maxentoutput.txt'), 'w', encoding='utf-8')
        features = os.path.join(basepath,'temp', 'Features.txt')
        maxentworkingpath = os.path.join(basepath,'maxent2', 'temp')
        os.chdir(maxentworkingpath)
        proj_maker.makeDefaultProj(path=maxentworkingpath, featfile=features)
        print("Running the baseline simulation now.")
        try:
            #this is the line that runs the java process (the actual maxent simulation):
            basesimulation = subprocess.run(JVOptions, check=True, stdout=maxentoutput)
            maxentoutput.close()
            removeLrnDatafromMEOut(os.path.join(maxentworkingpath, 'maxentoutput.txt'))
            #copy files to outpath:
            outfiles = ['grammar.txt', 'projections.txt', 'tableau.txt', 'maxentoutput.txt']
            if rt_output_baseline:
                if 'output_baseline' not in os.listdir(basepath):
                    os.mkdir(os.path.join(basepath, 'output_baseline'))
                outpath = os.path.join(basepath, 'output_baseline')
            else:
                if 'output_baseline' not in os.listdir(maxentworkingpath):
                    os.mkdir(os.path.join(maxentworkingpath, 'output_baseline'))
                    outpath = os.path.join(maxentworkingpath, 'output_baseline')
            for f in os.listdir(maxentworkingpath):
                    if f in outfiles:
                            shutil.copy(os.path.join(maxentworkingpath, f), os.path.join(outpath, f))
            print('Done with baseline simulation.')
        except:
                print('The baseline simulation failed. It might have run out of memory, or there is a problem with your data files. To diagnose the problem, start by checking the contents of maxent2/temp/maxentoutput.txt.')
        os.chdir(basepath)


def testGrammar(grammarpath, testfilepath):
    '''
    tests an existing grammar file
    '''
    basepath = os.getcwd().split('code')[0]
    outpath = os.path.join(grammarpath.split('grammar.txt')[0], 'test_'+ time.strftime('%Y-%m-%d-%H_%M'))
    JVOptions = setJVOptions(basepath)
    copyTestFiles(grammarpath,testfilepath)
    maxentworkingpath = os.path.join(basepath, 'maxent2', 'temp')
    maxentoutput = open(os.path.join(maxentworkingpath, 'maxentoutput.txt'), 'w', encoding='utf-8')
    os.chdir(maxentworkingpath)
    print("Testing your grammar now")
    try:
        basesimulation = subprocess.run(JVOptions, check=True, stdout=maxentoutput)
        maxentoutput.close()
    except:
        print("Something went wrong and the testing of your grammar failed.")
    outfiles = ['tableau.txt', 'maxentoutput.txt']
    os.mkdir(outpath)
    for f in outfiles:
        shutil.move(os.path.join(maxentworkingpath,f), os.path.join(outpath, f))
    os.chdir(basepath)




def makeProjection(basepath, projtype, mb):
        '''
        basepath is where the temp is located (needed to have access to original Features.txt). make it end in '/'
        type argument can be chosen from: 
                "wb" : takes word boundary-adjacent natural classes, finds all superset classes that contain them and makes a proj file for each
        '''
        grammar = os.path.join(basepath, 'output_baseline', 'grammar.txt')
        maxentoutputpath=os.path.join(basepath,'output_baseline','maxentoutput.txt')
        maxentworkingpath=os.path.join(basepath, 'maxent2','temp')
        features = os.path.join(maxentworkingpath, 'features.txt')
        projectiondir = os.path.join(basepath,'projections')
        if not os.path.exists(projectiondir):
            os.mkdir(projectiondir)
        proj_maker.makeWBProj(grammar, features, projectiondir, mb)
        if os.path.exists(projectiondir):
            if os.listdir(projectiondir):
                shutil.copy(os.path.join(projectiondir, 'projections.txt'), os.path.join(maxentworkingpath, 'projections.txt'))
            else:
                pass

def handmakeProjection(basepath, feature):
    '''
    basepath: where temp is located
    feature: if you pass this something like "+sonorant" or "-round", it will look up the features in the file associated with your data.
    otherwise, you can give it a path to a handmade projections file. if you want to do that, give it the full path starting with '/'. for example,
    "/Users/yourname/Desktop/projections.txt"
    if the second argument ends in "projections.txt", all that will happen is your projections file will get copied to the maxent2/temp directory.
    this function calls proj_maker.makeHandmadeProj(), passes two paths to it and a feature name.
    it is called by run_sim.runHandProjSim(), which takes path and feature from it
    '''
    maxentworkingpath=os.path.join(basepath,'maxent2','temp')
    features = os.path.join(maxentworkingpath, 'features.txt')
    if feature.endswith('projections.txt'):
        shutil.copy(feature, os.path.join(maxentworkingpath,'projections.txt'))
        print('copied your custom file to the temp directory')
    else:
        proj_maker.makeHandmadeProj(maxentworkingpath, feature, features)
        print('made a projection file for just default and a tier based on ' + feature)



def runCustomSim(feature=None, simtype='custom', basepath=os.getcwd().split('code')[0], reducemem=True, package=True):
        '''
        runs one simulation with a default tier plus a single additional tier.
        that tier can be based on a feature, or supplied manually.
        simtype defaults to 'custom' (proj file is either made from scratch given a command line feature spec or taken from an existing projection file, handpicked)
        '''
        print("Running simulation using new special projection")
        compoptions=setJVOptions(basepath, reducemem)
        maxentworkingpath=os.path.join(basepath,'maxent2','temp')
        maxentoutput=open(os.path.join(maxentworkingpath,'maxentoutput.txt'), 'w', encoding='utf-8')
        os.chdir(maxentworkingpath)
        if feature !=None and feature.endswith('.txt'):
            feature = feature.split('.txt')[0]
        outfiles=['grammar.txt', 'projections.txt', 'tableau.txt', 'maxentoutput.txt']
        try:
            projsimulation=subprocess.run(compoptions, check=True, stdout=maxentoutput)
            maxentoutput.close()
            if package:
                if simtype=='custom':
                    simdir = os.path.join(basepath,'output_custom_'+feature)
                elif simtype=='wb': 
                    simdir = os.path.join(basepath, 'output_final')
                    os.mkdir(simdir)
                    for f in outfiles:
                        shutil.copy(os.path.join(maxentworkingpath, f), os.path.join(simdir, f))
            print('Done with simulation.')
        except:
            print('The simulation failed. It might have run out of memory, or there is a problem with your data files. To diagnose the problem, start by checking the contents of maxent2/temp/maxentoutput.txt.')
        os.chdir(basepath)

def readParamsFromMaxentFile(maxentoutputfile):
    with open(maxentoutputfile, 'r', encoding='utf-8') as f:
        args = f.readline().strip('\n').split(',')


def duplicateSimChecker(basepath):
    sims = [x for x in os.listdir() if x.startswith('output_')]
    currentproj_path = os.path.join(basepath, 'maxent2', 'temp', 'projections.txt')
    simexists = False
    currentproj = open(currentproj_path, 'r', encoding='utf-8').readlines()
    for path in sims:
        proj = open(os.path.join(basepath, path, 'projections.txt'), 'r', encoding='utf-8').readlines()
        if currentproj == proj:
            simexists = True
            projpath = path
        else:
            continue
    if simexists:
        return projpath
    else:
        return False 


def removeLrnDatafromMEOut(pathtomaxentoutputfile):
        '''
        this is a utility function that serves to make maxentoutput.txt files smaller.
        by default, they include all the words from the learning and training data, which if you run a lot of simulations can really add to the size of the simulation directories.
        this opens up a maxentoutput file, takes out the data, and saves everything else.
        '''
        maxentfile=open(pathtomaxentoutputfile, 'r', encoding='utf-8')
        nondataoutput = []
        for line in maxentfile:
                if line.split(',')[0]!='[<#':
                        nondataoutput.append(line)
        maxentfile.close()
        maxentout = open(pathtomaxentoutputfile, 'w', encoding = 'utf-8')
        for item in nondataoutput:
                maxentout.write(item)
        maxentout.close()




def wrapSims(pathtotargetlocation, basepath=os.getcwd().split('code')[0], copyuserfiles = False, date=True, ret=False, cust=False):
        '''
        the pathtotargetlocation argument specifies where you want the results of the simulation to be placed.
        all files called 'output...' and 'projections...' will be moved to the new location.
        if your features or learning data vary between simulations, set copyuserfiles to True. it defaults to 'false'
        '''
        os.chdir(basepath)
        if date:
                rightnow = time.strftime("%Y-%m-%d_")
        else:
            rightnow=''
        if pathtotargetlocation.startswith('sims'):
            pathtotargetlocation=os.path.split(pathtotargetlocation)[1]
            pathtotargetlocation=os.path.join('sims',rightnow+pathtotargetlocation)
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
                files = [x for x in os.listdir(basepath) if x.startswith('output') or x =='alsorans']
        if cust:
                files = [x for x in os.listdir(os.path.join(basepath, 'maxent2','temp')) if x in ['maxentoutput.txt', 'projections.txt', 'tableau.txt', 'grammar.txt']]
        else:
                files = [x for x in os.listdir(basepath) if x.startswith('output') or x.startswith('projections') or x == 'alsorans']
        for fi in files:
            if not cust:
                os.renames(fi, os.path.join(pathtotargetlocation,fi))
            else:
                os.renames(os.path.join('maxent2','temp', fi), os.path.join(pathtotargetlocation, 'output_final', fi))
        if copyuserfiles:
            userfiles = [x for x in os.listdir(basepath) if not x.startswith('.')]
            for fi in userfiles:
                if not fi in os.listdir(pathtotargetlocation):
                    os.renames(fi, os.path.join(pathtotargetlocation,fi))
        print('files have been moved to '+ pathtotargetlocation)
        if 'temp' in os.listdir(basepath):
                shutil.rmtree('temp', ignore_errors=True)
        os.chdir('code')
        if ret==True:
                return pathtotargetlocation
