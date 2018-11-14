#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''
This module defines the functions that run the actual simulations that induce nonlocal phonological projections.

to see the information on how to use the various options, type "python3 run_sim.py help" at the command line prompt.

'''


import os,shutil, io, contextlib
import datachecker, simfunc, params, mbsublex


def run_mbsublex_sim(language, viol, mgain, nconstraints, mb, gam, parameters):
    '''
    this simulation needs a corpus with morpheme boundaries.
    it starts by running a baseline simulation on the corpus.
    then, if it finds constraints in the resulting grammar that mention [-mb] (see mbsublex module), it splits the learning data into individual morphemes, one morph per line
    it then uses that as a new baseline data set. if it locates any placeholder trigrams in that subset, it makes a projection from them
    and then it runs a projection simulation on the morpheme sublexicon, and on the whole corpus.
    '''
    basepath = os.getcwd().split('code')[0]
    maxentdir = os.path.join(basepath, 'maxent2', 'temp')
    dircontent = os.listdir(maxentdir)
    vio = viol[0:2]
    wrapstring = os.path.join('sims',language.replace(os.sep,"_")) + "_" + '_'.join(['wb','mbsublex', vio,'gain'+str(mgain),'con'+str(nconstraints)])
    if not 'output_baseline' in dircontent:
        simfunc.cleanUpWorkdir(basepath)
        if parameters:
            params.move_params(os.path.join(basepath, 'data', language, 'params.txt'))
            viol, mgain, nconstraints,gamma = params.read_params()
        else:
            params.makeParams(consize=nconstraints, violable=viol, mingain=mgain, gamma=gam, predefault=False)
        simfunc.makeSimFiles(language) 
        print('running the baseline simulation using original training corpus')
        simfunc.runBaselineSim(basepath, rt_output_baseline=False) #copies grammar, proj, tableau, maxentouptut in maxent2/temp/output_baseline
        mbsublex.move_sublex_files(kind='output_baseline')
    if not 'output_mbsublex_baseline' in dircontent:
        print("Baseline simulation found at " + os.path.join(maxentdir, 'output_baseline'))
       #analyze resulting grammar.txt file for [-mb] constraints, and make projections
        found_mb = mbsublex.search_grammar_for_mb()
        if found_mb:
            print('Making a sublexicon with one morph per line')
            mbsublex.make_freewd_sublexicon() #renames curr corpus 'orig_corpus.txt', creates new corpus that consists of just morphologically simple words and is called 'corpus.txt'
            print('Running a new baseline simulation using a sublexicon as training data')
            if parameters:
                params.scale_params(inpath=os.path.join(basepath, 'data', language, 'params.txt'), multiply_by=0.01, keepconsize=True)
            else:
                params.scale_params(viol, gain, consize, gamma, 0.01, True)#last one is keepconsize
            simfunc.runBaselineSim(basepath, rt_output_baseline=False)
            mbsublex.move_sublex_files(kind="output_mbsublex_baseline")
        else:
            print('Did not find any *X-mb-Y trigrams. Quitting now.')
            return mbsublex.wrapSims(wrapstring, basepath, ret=True)
    if not 'output_mbsublex' in dircontent:
        print("Sublexicon baseline simulation found at " + os.path.join(maxentdir, 'output_mbsublex'))
        mbsublex.makeProjection(basepath, 'wb', mb=True)
        print('projections found--running a projection simulation on morph sublexicon')
        simfunc.runCustomSim(simtype='wb')
        mbsublex.move_sublex_files(kind='output_mbsublex')
    if not 'output_final' in dircontent:
        mbsublex.rename_corpus_back()
        print('now running a projection simulation on the original training corpus')
        if parameters:
            params.scale_params(inpath=os.path.join(basepath, 'data', language, 'params.txt'), multiply_by=1, keepconsize=True)
        else:
            params.scale_params(viol, gain, consize, gamma, 10, True)
        simfunc.runCustomSim(simtype='wb')
        mbsublex.move_sublex_files(kind='output_final')
    print('done!')
    try:
        return mbsublex.wrapSims(wrapstring, basepath=maxentdir, ret=True)
    except:
        print("The simulation failed for some reason. Check the contents of " + maxentdir + " to help with debugging.")


def run_wb_sim(language, viol, mgain, nconstraints, mb, gam, parameters):
    '''
    this learning simulation is described in Gouskova and Gallagher (NLLT). The learner starts with a baseline
    grammar; if this grammar contains placeholder trigrams, it creates projections for each distinct trigram and runs a final simulation with those projections available.
    '''
    basepath = os.getcwd().split('code')[0]
    simfunc.cleanUpWorkdir(basepath)
    if parameters: 
        params.move_params(os.path.join(basepath, 'data', language, 'params.txt'))
        viol, mgain, nconstraints,gamma  = params.read_params()
    else:
        params.makeParams(consize=nconstraints, violable=viol, mingain=mgain, gamma=gam, predefault=False)
    simfunc.makeSimFiles(language)
    #baseline simulation
    simfunc.runBaselineSim(basepath)
    #analyze resulting grammar.txt file, make projections for each wb-mentioning constraint
    simfunc.makeProjection(basepath, 'wb', mb)
    if len(os.listdir('projections'))==0:
        print('\nNo projections were found because there were no placeholder constraints in the baseline grammar.')
    else:
        simfunc.runCustomSim(simtype= 'wb')
    vio = viol[0:2]
    wrapstring = os.path.join('sims',language.replace(os.sep,"_")) + "_" + '_'.join(['wb',vio,'gain'+str(mgain),'con'+str(nconstraints)])
    return simfunc.wrapSims(wrapstring, ret=True)


def run_baseline_sim(language, viol, mgain, nconstraints, mb, gam, parameters):
    '''
    this function runs the baseline simulation with a default (segmental) projection
    if it does not succeed, it does not fail gracefully, so be forwarned
    '''
    basepath = os.getcwd().split('code')[0]
    lgfullpath = os.path.join(basepath, 'data', language)
    simfunc.cleanUpWorkdir(basepath)
    if parameters: 
        params.move_params(os.path.join(lgfullpath, 'params.txt'))
        viol, mgain, nconstraints, gam = params.read_params()
    else:
        params.makeParams(consize=nconstraints, violable=viol, mingain=mgain, gamma=gam, predefault=False)
    simfunc.makeSimFiles(lgfullpath)
    try:
        simfunc.runBaselineSim(basepath, reducemem=False)
        #language=language.split('../data/')[1].replace('/','_')
        wrapstring = os.path.join('sims', language.replace(os.sep, "_") +'_baseline' + '_gain'+mgain + '_con' + nconstraints)
        simfunc.wrapSims(wrapstring)
    except CalledProcessError:
        print("Done")


def run_agree_disagree_sim(language, viol, mgain, nconstraints, mb, gam, parameters):
    '''
    this is not described anywhere, is work in progress
    makes a bunch of constraints on the basis of the natural classes structure of the language
    they have the form +f +f, +f [+wb] +f, +f [-wb] +f, and ditto for every combination of + and - for f 
    (in other words, it makes agree constraints and disagree constraints for every feature and nat class in the language)
    it then runs a simulation with this premade constraint set.

    the early results in testing this have not been encouraging
    '''
    basepath=os.getcwd().split('code')[0]
    lgfullpath = os.path.join(basepath, 'data', language)
    simfunc.cleanUpWorkdir(basepath)
    simfunc.makeSimFiles(lgfullpath, ag_disag=True)
    if parameters: 
        params.move_params(lgfullpath, 'params.txt')
        viol, mgain, nconstraints, gam = params.read_params()
    else:
        params.makeParams(consize=nconstraints, violable=viol, mingain=mgain, gamma=gam, ag_disag=True)
    simfunc.runBaselineSim(basepath)
    wrapstring = os.path.join('sims', '_'.join([language.replace(os.sep, "_"), 'baseline', 'AG', viol[:2], 'gain', mingain, 'ncons', nconstraints]))
    return simfunc.wrapSims(wrapstring, ret=True)


def run_handmade_projection_sim(language, viol, mgain, nconstraints, gam, parameters, feature):
    '''
    this either creates a projection file based on the value of "feature" (e.g., "-son") or runs a simulation with a custom projection file. To do the latter, supply a full path to the projection file as the last argument.
    '''
    basepath = os.getcwd().split('code')[0]
    lgfullpath = os.path.join(basepath, 'data', language) 
    simfunc.cleanUpWorkdir(basepath)
    simfunc.makeSimFiles(language)
    if parameters: 
        params.move_params(lgfullpath, 'params.txt')
        viol, mgain, nconstraints, gam = params.read_params()
    else:
        params.makeParams(consize=nconstraints, violable=viol, mingain=mgain, gamma=gam)
    simfunc.handmakeProjection(basepath, feature)
    simfunc.runCustomSim(feature)
    if 'output_baseline' in os.listdir(basepath):
        shutil.rmtree(basepath+'output_baseline')
    simfunc.wrapSims(os.path.join('sims', '_'.join(language.replace(os.sep, "_"), 'custom')), cust=True)

def test_grammar(grammarfile, testfile):
    basepath = os.getcwd().split('code')[0]
    grammardir = grammarfile.split('grammar.txt')[0]
    if not 'projections.txt' in os.listdir(grammardir):
        print('Please make sure there is a projections.txt file in the directory that has your grammar.txt file.')
    elif not 'Features.txt' in os.listdir(testfile.split('TestingData.txt')[0]):
        print('Please make sure there is a Features.txt file in the directory that has your TestingData.txt file.')
    else:
        simfunc.cleanUpWorkdir(basepath)
        simfunc.testGrammar(grammarfile, testfile) 
        print('done! your tableau.txt file has been placed in a new directory that has your original grammar.txt file.')
    

def save_program_trace(learnsim, language, viol, mgain, nconstraints, mb, gam, parameters):
    '''
    saves stdout of learnsim to a file.
    '''
    basepath = os.getcwd().split('code')[0]
    progtrace = io.StringIO()
    out = open(os.path.join(basepath, 'program_trace.txt'), 'w', encoding='utf-8')
    with contextlib.redirect_stdout(progtrace):
        stuff = learnsim(language, viol, mgain, nconstraints, mb, gam, parameters)
    out.write(progtrace.getvalue())
    out.close()
    shutil.move(os.path.join(basepath, 'program_trace.txt'), os.path.join(basepath, stuff, 'program_trace.txt'))
    print(os.path.join(basepath, stuff))
    return os.path.join(basepath, stuff)

if __name__=='__main__':
    import sys
    HelpMessage = '\n\n\nTo run the projection learner from the command line, enter:\n\n\n $ python3 run_sim.py language/subfolder \n\n and then enter the parameters for type of simulation ("baseline", "custom", "wb", "ag_disag", "mbsublex"), gain (e.g., "gain100"), the number of constraints (e.g., "ncons30"), and optionally "mb" if you want to project a morpheme boundary symbol on induced projections. By default, the learner will learn violable constraints ("vi"); if you want to override this, enter "in"(for "inviolable"). We recommend also specifying a "gamma" parameter (e.g., "gamma5"), which increases the importance of constraint violations in the grammar and makes it less likely that you will end up with a lot of constraints with a weight of 0. If not specified it defaults to "0".  \n\nExample: \n\n\n$ python3 run_sim.py quechua/words wb mb gain50 ncons100\n\n This will run a simulation inducing projections from placeholder constraints, project "mb" segments onto the projection, look for constraints that are violable, and leave gamma at the default value of 0. \n\n\nAnother example, this time looking for inviolable constraints in a baseline simulation only: \n\n\n$ python3 run_sim.py russian gamma20 baseline in gain10 ncons50\n\n\nIf you want to run a simulation with a custom projection, enter the features you want to project last, or else specify a path to your projections.txt file.\n\n $ python3 run_sim.py quechua/words custom in 50 100 -sonorant\n\n\n Finally, you may supply your own parameters file, leaving gain, con size,gamma, and violability unspecified in the command line call. Make sure you have a params.txt file in your data folder, and enter a "parameters" argument in your command line call:\n\n$ python3 run_sim.py russian baseline parameters.\n\n\n To run a sublexicon simulation, you must have a parsed file with morpheme boundaries. Call the simulation as follows:\n\n\n$ python3 run_sim.py aymara/words mbsublex parameters\n\n\n(As before, you can specify your own gain and ncons and gamma levels. Keep in mind that these are modified when creating the sublexicon, since a larger learning set needs a higher gain and gamma setting than a smaller one.)\n\n\nTo *test* an existing grammar, do the following:\n\n\n$ python3 run_sim.py fullpathto/grammar.txt fullpathto/TestingData.txt test\n\n\n(the arguments can be in any order, but one must lead to grammar.txt, another--to TestingData.txt, and please supply "test" as the switch. Also, there must be a projections.txt file inside the grammar directory, and a Features.txt file inside the testing data directory.'
    if 'help' in sys.argv:
        print(HelpMessage)
    elif 'test' in sys.argv:
        testpath =[x for x in sys.argv if x.endswith('TestingData.txt')][0]
        grammarpath = [x for x in sys.argv if x.endswith('grammar.txt')][0]
        test_grammar(grammarpath, testpath)
    else:
        filepath=sys.argv[1]
        featurefile = os.path.join(os.getcwd().split('code')[0], 'data', filepath, 'Features.txt')
        datafile = os.path.join(os.getcwd().split('code')[0], 'data', filepath, 'LearningData.txt')
        x = datachecker.findOrphans(datafile, featurefile, verbose=True)
        if x:
            print("Please fix your data file and/or your feature file and test data to continue.")
        else:
            if 'parameters' in sys.argv:
                parameters = True
                mingain, ncons, learnviolable, gam = False, False, False, False 
            else:
                parameters = False
                try:
                    gam = [arg.split('gamma')[1] for arg in sys.argv if len(arg.split('gamma'))>1][0]
                except IndexError:
                    gam = '0'
                try:
                    mingain = [arg.split('gain')[1] for arg in sys.argv if len(arg.split('gain'))>1 and not arg.split('gain')[1]==''][0]
                except IndexError:
                    print('Could not understand your gain setting, so will use the default number (1). Please type "python3 run_sim.py help" for more information.')
                    mingain='1'
                try:
                    ncons = [arg.split('ncons')[1] for arg in sys.argv if len(arg.split('ncons'))>1 and not arg.split('ncons')[1]==''][0]
                except IndexError:
                    print("Could not understand your setting for the number of constraints to induce, so will use the default number (500). Please type 'python3 run_sim.py help' for more information.")
                    ncons='500'
            if 'mb' in sys.argv:
                mb = True
            else:
                mb = False
            if 'wb' in sys.argv:
                symtype='wb'
            if ('in' in sys.argv) or ('inviolable' in sys.argv):
                learnviolable='inviolable'
            else:
                learnviolable='violable'
            if 'baseline' in sys.argv:
                try:
                    run_baseline_sim(filepath, learnviolable, mingain, ncons, mb, gam, parameters)
                except IndexError:
                    print(HelpMessage)
            elif 'custom' in sys.argv:
                try:
                    feat = sys.argv[-1]
                    run_handmade_projection_sim(filepath, learnviolable, mingain, ncons, gam, parameters, feat)
                except IndexError:
                    print(HelpMessage)
            elif 'wb' in sys.argv:
                try:
                    print('Working on your learning simulation. Your results will be saved inside the "sims" folder. If the simulation fails halfway and you get an incomprehensible error, please check the contents of maxent2/temp/maxentoutput.txt.')
                    outdir = save_program_trace(run_wb_sim, filepath, learnviolable, mingain, ncons, mb, gam, parameters)
                    print("Done! look for your results in the simulation folder, " + outdir)
                except IndexError:
                    print(HelpMessage)
            elif 'ag_disag' in sys.argv:
                try:
                    print('Working on your learning simulation.')
                    outdir=save_program_trace(run_agree_disagree_sim, filepath, learnviolable, mingain, mb, ncons, gam, parameters)
                except IndexError:
                    print (HelpMessage)
            elif 'mbsublex' in sys.argv:
                try:
                    print('Working on your learning simulation. To check the progress of the simulation, look inside maxent2/temp. Your results will be saved in the "sims" folder. If the simulation fails halfway or you get an error you cannot understand, the answer is probably inside maxent2/temp/maxentoutput.txt.')
                    outdir=save_program_trace(run_mbsublex_sim, filepath, learnviolable, mingain, ncons, mb, gam, parameters)
                except IndexError:
                    print(HelpMessage)
