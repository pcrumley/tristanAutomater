import re, sys, os, h5py
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),'src/'))
from tracked_particles import TrackedDatabase

class cachedProperty(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    """
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

class PictorSim(object):
    def __init__(self, dirpath=None, xtraStride = 1, outputFileNames = ['fld_*', 'prtl_*']):
        self._outputFileNames = outputFileNames
        self._outputFileKey = [key.split('_')[0] for key in self._outputFileNames]
        self._outputFileRegEx = [re.compile(elm) for elm in self._outputFileNames]

        self._outputFileH5Keys = []
        self._pathDict = {}
        self._collisionFixers = {}
        self.dir = str(dirpath)

        self._name = os.path.split(self.dir)[0]
        self._name = os.path.split(self.dir)[-1]
        self.xtraStride = xtraStride
        self._h5Key2FileDict = {}
        self._fnum = self.getFileNums()
        self.dd = {}
        self.paramKeys = []
        ### open first file and get all the keys:

        if len(self) != 0:
            for fname in self._outputFileNames:
                tmpStr = ''
                for elm in fname.split('_')[:-1]:
                    tmpStr += elm +'_'
                tmpStr += self._fnum[0]
                with h5py.File(os.path.join(self.dir, tmpStr), 'r') as f:
                    self._outputFileH5Keys.append([key for key in f.keys()])
            # Build an key to h5 file dictionary, and a h5 file to key dictionary
            self._output = [OutputPoint(self, n=x) for x in self.getFileNums()]
            for fkey in self._outputFileKey:
                for key in getattr(self[0], '_'+fkey).keys():
                    if key in self._h5Key2FileDict.keys():
                        if key not in self._collisionFixers.keys():
                            print(f'{key} in {fkey} has collision with {self._h5Key2FileDict[key]}')
                            print(f'Please update self._collisionFixers dictionary in __init__()')
                            print(f'function of TristanSim class')
                        else:
                            self._h5Key2FileDict[key] = self._collisionFixers[key]
                    else:
                        self._h5Key2FileDict[key] = fkey
            with h5py.File(os.path.join(self.dir, 'param'), 'r') as f:
                self.paramKeys = [key for key in f.keys()]
            self.params = h5Wrapper(os.path.join(self.dir, 'param'), self.paramKeys)
            self._output[0].setParams(self.paramKeys)
            self._output[0].setKeys(self._h5Key2FileDict)

    def getFileNums(self):
        try:
            # Create a dictionary of all the paths to the files
            tmp1 = []
            tmp2 = []
            tmp3 = []
            for name, key, regEx in zip(self._outputFileNames, self._outputFileKey, self._outputFileRegEx):
                if len(list(filter(regEx.match, os.listdir(self.dir)))) != 0:
                    tmp1.append(name)
                    tmp2.append(key)
                    tmp3.append(regEx)
            self._outputFileNames = tmp1
            self._outputFileKey = tmp2
            self._outputFileRegEx = tmp3

            for key, regEx in zip(self._outputFileKey, self._outputFileRegEx):
                self._pathDict[key] = [item for item in filter(regEx.match, os.listdir(self.dir))]
                self._pathDict[key].sort()
                for i in range(len(self._pathDict[key])):
                    elm = self._pathDict[key][i]
                    try:
                        int(elm.split('_')[-1])
                    except ValueError:
                        self._pathDict[key].remove(elm)
            ### GET THE NUMBERS THAT HAVE ALL SET OF FILES:
            allThere = set(elm.split('_')[-1] for elm in self._pathDict[self._outputFileKey[0]])
            for key in self._pathDict.keys():
                allThere &= set(elm.split('_')[-1] for elm in self._pathDict[key])
            allThere = list(sorted(allThere, key = lambda x: int(x)))
            return allThere

        except OSError:
            return []


    @property
    def name(self):
        return self._name

    # setting the values
    @name.setter
    def name(self, myName):
        self._name = myName

    @property
    def trackStart(self):
        return self._trackStart



    def __len__(self):
        #return np.sum(self._mask)
        return len(self._fnum)

    def __getitem__(self, val):
        return self._output[val]

    def saveDD(self):
        # We assume that all things are all npy arrays
        ddPath = os.path.join(self.dir, '.dd.npz')
        np.savez(ddPath, **self.dd)
    def loadDD(self):
        # We assume that all things are all npy arrays
        ddPath = os.path.join(self.dir, '.dd.npz')
        if os.path.exists(ddPath):
            with np.load(ddPath) as npzFile:
                for arr in npzFile.files:
                    self.dd[arr] = npzFile[arr]

    def loadAllFields(self):
        for out in self:
            for key, val in self._h5Key2FileDict.items():
                if val == 'flds':
                    getattr(out, key)
    def loadAllPrtls(self):
        for out in self:
            for key, val in self._h5Key2FileDict.items():
                if val == 'prtl':
                    getattr(out, key)


class ObjectMapper(object):
    '''A base object that holds the info of one type of particle in the simulation
    '''
    __h5Keys = []
    __paramKeys = []
    def __init__(self, sim, n=0):
        pass
    @classmethod
    def setParams(cls, paramList):
        cls.__paramKeys = [p for p in paramList]
    @classmethod
    def getParams(cls):
        return cls.__paramKeys
    @classmethod
    def setKeys(cls, mapdict):
        cls.__h5Keys = [key for key in mapdict.keys()]
    @classmethod
    def getKeys(cls):
        return cls.__h5Keys

class OutputPoint(ObjectMapper):
    '''A object that provides an API to access data from Tristan-mp
    particle-in-cell simulations. The specifics of your simulation should be
    defined as a class that extends this object.'''
    def __init__(self, sim, n='001'):
        self._sim = sim
        self.__myKeys = []
        self.fnum = n

        for key, fname, h5KeyList in zip(sim._outputFileKey, sim._outputFileNames, sim._outputFileH5Keys):
            self.__myKeys.append(key)
            tmpStr = ''
            for elm in fname.split('_')[:-1]:
                tmpStr += elm +'_'
            tmpStr += n
            setattr(self, '_'+key, h5Wrapper(os.path.join(sim.dir, tmpStr), h5KeyList))

    def __getattribute__(self, name):
        if name in super().getKeys():
            return getattr(getattr(self,'_'+self._sim._h5Key2FileDict[name]), name)
        elif name in super().getParams():
            return getattr(self._sim.params, name)
        else:
            return object.__getattribute__(self, name)


    def clear(self):
        for key in self.__myKeys:
            getattr(self, f'_{key}').clear()


class h5Wrapper(object):
    def __init__(self, fname, h5Keys):
        self._fname = fname
        self.__h5Keys = h5Keys
        self.clear()

    def __getattribute__(self, name):
        if object.__getattribute__(self, name) is None:
            if name in self.__h5Keys:
                with h5py.File(self._fname, 'r') as f:
                    if np.sum([x for x in f[name].shape])!= 1:
                        setattr(self, name, f[name][:])
                    else:
                        setattr(self, name, f[name][0])
        return object.__getattribute__(self, name)

    def keys(self):
        return self.__h5Keys

    def clear(self):
        for key in self.__h5Keys:
            setattr(self, key, None)



if __name__=='__main__':
    import time
    import matplotlib.pyplot as plt
    mySim = TristanSim('~/tig/RelTracking/StampedeRun/output')
    #plt.imshow(mySim[0].ex[0,:,:])
    #plt.show()
