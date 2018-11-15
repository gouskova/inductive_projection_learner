import os, subprocess



'''
a helper that runs the java natural classes utility; packNatClasses returns a natural classes dictionary that gets used a lot in proj_maker and other places
'''


def makeJarPaths(basepath):
        """
        this pastes a bunch of jar files together into a path that gets passed to the java run of maxent.
        by default, jardir will be in basepath+'maxent2/jar'
        
        it is a dumb copy of the same function in simfunc.py, because i couldn't figure out a better way to avoid circular dependencies
        """
        jardir = os.path.join(basepath,'maxent2', 'jar')
        extdir = os.path.join(basepath,'maxent2', 'extern')
        jarfiles = [x for x in os.listdir(jardir) if not x.startswith('.')]
        extjarfiles = [x for x in os.listdir(extdir) if not x.startswith('.')]
        jarpaths = [os.path.join(jardir,x) for x in jarfiles]
        extpaths = [os.path.join(extdir,x) for x in extjarfiles]
        alljar=':'.join(jarpaths+extpaths)
        return alljar


def packNatClasses(featfile=os.path.join('maxent2', 'temp', 'features.txt')):
    '''
    input argument: feature file, converted to command line maxent format.
    by default this is in maxent2/temp/features.txt.
    this will return a natural class dictionary with
    'features' (['-son', '+cont'])
    'segments'(['p', 't', 'k'])
    classname (e.g., '-son,+cont')
    for each nat class
    '''
    basepath=os.getcwd().split('code')[0]
    os.chdir(os.path.join(basepath,'maxent2'))
    alljar = makeJarPaths(basepath)
    features = os.path.join(basepath,featfile)
    JVOptions = ['java', '-cp', alljar, 'edu.jhu.features.NaturalClasses', features]
    nclassdic= {}
    natclasses = subprocess.check_output(JVOptions)
    natclasses = natclasses.decode('utf-8').split('\n')#checkoutput returns a bytestring, b'garbage'
    for line in natclasses[1:-2]: #the first line is 'id\t features \t segments', and the second is for the [] class. the last line is an empty string for some dumb reason because subprocess sucks
        line = line.split('\t')
        classname=line[1].strip('[]').replace(',','')
        simname = line[1].strip('[]')
        features = simname.split(',')
        segments = line[2].strip('()').split('|')
        nclassdic[classname] = {'features': features,
            'segments': segments,
            'classname': simname
            }
    os.chdir(basepath)
    return nclassdic





