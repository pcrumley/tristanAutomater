import re, os, h5py
import numpy as np
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

class TristanSim(object):
    def __init__(self, dirpath=None, xtraStride = 1):
        self._trackKeys = ['t', 'x', 'y', 'u', 'v', 'w', 'gamma', 'bx', 'by', 'bz', 'ex', 'ey', 'ez']
        self._outputFileNames = ['flds.tot.*', 'prtl.tot.*', 'spect.*', 'param.*']
        self._outputFileKey = [key.split('.')[0] for key in self._outputFileNames]
        self._outputFileRegEx = [re.compile(elm) for elm in self._outputFileNames]
        self._pathDict = {}
        self._collisionFixers = {'time': 'param', 'dens': 'flds'}
        self.dir = str(dirpath)
        self.getFileNums()
        self.xtraStride = xtraStride
        self._h5Key2FileDict = {}
        self.__output = [OutputPoint(self, n=x) for x in self.getFileNums()]


        if len(self) != 0:
            # Build an key to h5 file dictionary
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
            self.__output[0].setMapper(self._h5Key2FileDict)
    def getFileNums(self):
        try:
            # Create a dictionary of all the paths to the files
            hasStar = 0
            for key, regEx in zip(self._outputFileKey, self._outputFileRegEx):
                self._pathDict[key] = [item for item in filter(regEx.match, os.listdir(self.dir))]
                self._pathDict[key].sort()
                for i in range(len(self._pathDict[key])):
                    elm = self._pathDict[key][i]
                    try:
                        int(elm.split('.')[-1])
                    except ValueError:
                        if elm.split('.')[-1] == '***':
                            hasStar += 1
                        self._pathDict[key].remove(elm)
            ### GET THE NUMBERS THAT HAVE ALL SET OF FILES:
            allThere = set(elm.split('.')[-1] for elm in self._pathDict[self._outputFileKey[0]])
            for key in self._pathDict.keys():
                allThere &= set(elm.split('.')[-1] for elm in self._pathDict[key])
            allThere = list(sorted(allThere, key = lambda x: int(x)))
            if hasStar == len(self._pathDict.keys()):
                allThere.append('***')
            return allThere

        except OSError:
            return []

    @cachedProperty
    def trackedLecs(self):
        return TrackedDatabase(self, 'lecs', keys = self._trackKeys)
    @cachedProperty
    def trackedIons(self):
        return TrackedDatabase(self, 'ions', keys = self._trackKeys)
    def __len__(self):
        #return np.sum(self._mask)
        return len(self.__output)

    def __getitem__(self, val):
        return self.__output[val]
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
    __h5_dict = {}
    def __init__(self, sim, n=0):
        pass
    @classmethod
    def setMapper(cls, dict):
        cls.__h5_dict = {key: val for key, val in dict.items()}
    @classmethod
    def getMapper(cls):
        return cls.__h5_dict

class OutputPoint(ObjectMapper):
    '''A object that provides an API to access data from Tristan-mp
    particle-in-cell simulations. The specifics of your simulation should be
    defined as a class that extends this object.'''
    def __init__(self, sim, n=0):
        self._sim = sim
        self.__myKeys = []


        for key, fname in zip(sim._outputFileKey, sim._outputFileNames):
            self.__myKeys.append(key)
            tmpStr = ''
            for elm in fname.split('.')[:-1]:
                tmpStr += elm +'.'
            tmpStr += n
            setattr(self, '_'+key, h5Wrapper(os.path.join(sim.dir, tmpStr)))
    def __getattribute__(self, name):
        if name in super().getMapper():
            return getattr(getattr(self,'_'+self._sim._h5Key2FileDict[name]), name)
        else:
            return object.__getattribute__(self, name)

    def reload(self):
        for key in self.__myKeys:
            getattr(self, key).reload()


class h5Wrapper(object):
    def __init__(self, fname):
        self._fname = fname
        self.reload()

    def __getattribute__(self, name):
        if object.__getattribute__(self, name) is None:
            if name in self.__h5keys:
                with h5py.File(self._fname, 'r') as f:
                    setattr(self, name, f[name][:])
        return object.__getattribute__(self, name)

    def keys(self):
        return self.__h5keys

    def reload(self):
        with h5py.File(self._fname, 'r') as f:
            for key in f.keys():
                self.__h5keys = [key for key in f.keys()]
        for key in self.__h5keys:
            setattr(self, key, None)

if __name__=='__main__':
    import time
    import matplotlib.pyplot as plt
    mySim = TristanSim('../Iseult/output')
    plt.imshow(mySim[0].ex[0,:,:])
    plt.show()
