import sys, os, re, itertools
import numpy as np
import yaml
#import unittest
class simulationSearcher(object):
    '''A object that will handle the searching of parameter space
    '''
    def __init__(self):

        self.interval = 1000
        self.end = 100000
        self._rootDir = './'
        self.tunit = None
        self._cfgOpts = {} # will store the input file of tristan
        self._submitOpts = {}
        self.__cfgMapper = {}
        self._submitDict = {} # will store and write the submit file
        self._searchGrid = []
        self._gridNames = []
        self._executeables = []

    def deepCopyDict(self, aDictionary):
        returnDictionary = {}
        for key, val in aDictionary.items():
            returnDictionary[key] = {optn: optv for optn, optv in val.items()}
        return returnDictionary

    def buildSearchGrid(self,box, **kwargs):
        '''This is garbage code... I should simplify this.'''
        grid = None
        for key, val in kwargs.items():
            if grid is None:
                grid = val
            else:
                grid = itertools.product(grid,val)
                tmpGrid = []
        
                for item in grid:
                    try:
                        tmpList =list(item[0])
                        tmpList.append(item[1])
                    
                    except TypeError:
                        tmpList = list(item)
                        
                    tmpGrid.append(tmpList)                
                grid = tmpGrid
        #print(grid)
        for pt in grid:
            tmpDict = self.deepCopyDict(self._cfgOpts)
            
            tmpStr = ''
            for key, val in zip(kwargs.keys(), pt):
                if key not in ['sizex', 'sizey']:
                    tmpStr += str(key) + '_' + str(val) + '_'
                tmpDict[self.__cfgMapper[key]][key] = val
            #self._searchGrid.append({key: val for key, val in tmpDict.items()})
            self._searchGrid.append(self.deepCopyDict(tmpDict))
            self._gridNames.append(tmpStr)

        for i in range(len(self._searchGrid)):
            name = self._gridNames[i]
            pt = {key: val for key, val in self._searchGrid[i].items()}
            tmpConst = 1
            if box['units'] == 'omega_pe':
                tmpConst = int(pt[self.__cfgMapper['c_omp']]['c_omp'])

            elif box['units'] == 'omega_pi':
                tmpConst = int(pt[self.__cfgMapper['c_omp']]['c_omp'])
                tmpConst *= np.sqrt(float(pt[self.__cfgMapper['mi']]['mi']))
                tmpConst /= np.sqrt(float(pt[self.__cfgMapper['me']]['me']))

            converter = lambda d: int(d*tmpConst)
            xiter = map(converter, box['x'])
            yiter = [2] if len(box['y']) == 0 else map(converter, box['y'])
            ziter = [1] if len(box['z']) == 0 else map(converter, box['z'])
            boxkeys = ['mx0', 'my0', 'mz0']
            boxheaders = [self.__cfgMapper[key] for key in boxkeys]
            
            for boxX in xiter:
                #print(boxX)
                for boxY in yiter:
                    for boxZ in ziter:
                        for head, key, val in zip(boxheaders, boxkeys, [boxX, boxY, boxZ]):
                            pt[head][key] = val
                            name += str(key) + '_' + str(val) + '_'
            self._gridNames[i] = name[:-7] if len(box['z']) == 0 else name[:-1] 
    def loadInputTemplate(self, input_file):
        '''Converts tristan_input to a python dict'''
        headers = re.compile("\<(.*?)\>")
    
        with open(input_file, 'r') as f:
            inputlist = f.readlines()
        for line in inputlist:
            if headers.search(line):
                curHeader = headers.search(line).group(0)
                self._cfgOpts[curHeader] = {}
            else:
                try:
                    if line.split()[1]=='=':
                        self._cfgOpts[curHeader][line.split()[0]]=line.split()[2]
                        self.__cfgMapper[line.split()[0]] = curHeader
                except IndexError:
                    continue

    def setOutputOpts(self,**kwargs):

        outkeys = 'hi'
        tmpConst = 1
        units = kwargs.pop('units', None)
        cfgKeys = []
        cfgHeaders = []
        vals = []
        for key in kwargs.keys():
            cfgKeys.append(key)
            cfgHeaders.append(self.__cfgMapper[key])
            vals.append(kwargs[key])
        for pt in self._searchGrid:
            if units == 'omega_pe':
                tmpConst = int(pt[self.__cfgMapper['c_omp']]['c_omp'])
                tmpConst /= float(pt[self.__cfgMapper['c']]['c'])
                #print(float(pt[self.__cfgMapper['c']]['c']))
            elif units == 'omega_pi':
                tmpConst = float(pt[self.__cfgMapper['c_omp']]['c_omp'])
                tmpConst *= float(np.sqrt(pt[self.__cfgMapper['mi']]['mi']))
                tmpConst /= float(np.sqrt(pt[self.__cfgMapper['me']]['me']))
                tmpConst /= pt[self.__cfgMapper['c']]['c']
            for head, key, val in zip(cfgHeaders, cfgKeys, vals):
                if key in ['last', 'interval', 'dlaplec', 'teststartlec', 'testendlec', 'dlapion', 'teststartion', 'testendion']:
                    pt[head][key] = int(tmpConst*val)
                else:
                    pt[head][key] = val

                                      
            
    def submitJobs(self, **kwargs):
        #The grid has been build and we are ready to make the directories and input files
        for key, val in kwargs.items():
            self._submitOpts[key] = val

        slurmcmds = []
        for elm in self._submitOpts['exec']:
            tmpStr = os.path.split(elm)[-1]
            for name, cfgDict in zip(self._gridNames, self._searchGrid):
                dirname = name + tmpStr
                dirname = os.path.join(self._rootDir, dirname)
                os.makedirs(dirname, exist_ok=True)
                dirname = os.path.abspath(dirname)
                tmpInput = os.path.join(dirname,'input')
                self.writeInputFile(cfgDict, outfile=tmpInput)
                #outdir = os.path.join(dirname, 'output/')
                outdir = './output/'
                outfile = 'out'
                coresNeeded = int(cfgDict[self.__cfgMapper['sizex']]['sizex'])*int(cfgDict[self.__cfgMapper['sizey']]['sizey'])
                os.system(f'cp {elm} {dirname}')
                slurmcmds.append({'cores': coresNeeded, 'slurmString': f"cd {dirname} && srun -n {coresNeeded} {elm} -i input -o {outdir} > {outfile}"})
        #print(len(slurmcmds), self._submitOpts['jobs'])
        print(range(0,len(slurmcmds), len(slurmcmds)//self._submitOpts['jobs']))
        breaks = list(range(0,len(slurmcmds)+1, len(slurmcmds)//self._submitOpts['jobs']))
        breaks[-1] = len(slurmcmds)
        totalCores = self._submitOpts['coresPerNode']*self._submitOpts['nodesPerJob']
        for i in range(self._submitOpts['jobs']):
            with open(f'submit{i}', 'w+') as f:
                f.write('#!/bin/bash\n')
                f.write(f'#SBATCH -n {totalCores}\n')
                f.write(f"#SBATCH -t {self._submitOpts['totalTime']}\n")
                f.write("#SBATCH --mail-type=all\n")
                f.write(f"#SBATCH --mail-user={self._submitOpts['email']}\n\n")
                
                for module in self._submitOpts['modules']:
                    f.write('module load {}\n'.format(module))
                coreCount = 0
                print(breaks, i)
                for cmd in slurmcmds[breaks[i]:breaks[i+1]]:
                    f.write(cmd['slurmString'])
                    coreCount+=cmd['cores']
                    if coreCount < totalCores:
                        f.write(' &\n')
                    else:
                        coreCount = 0
                        f.write('\n'+ 'wait\n')
            os.system(f'sbatch submit{i}')
        
    def writeInputFile(self,cfgDict, outfile='test.txt'):
        with open(outfile, 'w+') as f:
            for key, val in cfgDict.items():
                f.write(key+'\n')
                for opt, ans in val.items():
                    f.write(opt + ' = ' + str(ans) + '\n')
                f.write('\n')
    def setRootDir(self, dirname):
        self._rootDir = dirname
if __name__ == '__main__':
    with open("config.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            print(config)
        except yaml.YAMLError as exc:
            print(exc)

    runBuilder = simulationSearcher()
    runBuilder.setRootDir(config['ROOT_DIRECTORY'])
    runBuilder.loadInputTemplate(config['BASE_INPUT_FILE'])
    runBuilder.buildSearchGrid(box=config['box'], **config['paramOpts'])
    runBuilder.setOutputOpts(**config['outputOpts']) 
    runBuilder.submitJobs(**config['submitOpts'])

