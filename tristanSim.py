import re, os, h5py
import numpy as np
from particles import Ions, Electrons, cachedProperty
from tracked_particles import TrackedDatabase

class TristanSim(object):
    def __init__(self, dirpath=None, xtraStride = 1):
        self.__allTrackKeys = ['t', 'x', 'y', 'u', 'v', 'w', 'gamma', 'bx', 'by', 'bz', 'ex', 'ey', 'ez']
        self.trackKeys = self.__allTrackKeys
        self.dir = str(dirpath)
        self.xtraStride = xtraStride
        self.output = [OutputPoint(self.dir, n=x, xtraStride = self.xtraStride) for x in self.getFileNums()]
    @property
    def trackKeys(self):
        return self.__trackKeys

    @trackKeys.setter
    def trackKeys(self, args):
        self.__trackKeys = []
        for arg in args:
            if arg in self.__allTrackKeys:
                self.__trackKeys.append(arg)

    def getFileNums(self):
        try:
            # create a bunch of regular expressions used to search for files
            f_re = re.compile('flds.tot.*')
            prtl_re = re.compile('prtl.tot.*')
            s_re = re.compile('spect.*')
            param_re = re.compile('param.*')

            # Create a dictionary of all the paths to the files
            self.pathDict = {'flds': [], 'prtl': [], 'param': [], 'spect': []}
            self.pathDict['flds']= [item for item in filter(f_re.match, os.listdir(self.dir))]
            self.pathDict['prtl']= [item for item in filter(prtl_re.match, os.listdir(self.dir))]
            self.pathDict['spect']= [item for item in filter(s_re.match, os.listdir(self.dir))]
            self.pathDict['param']= [item for item in filter(param_re.match, os.listdir(self.dir))]

            ### iterate through the Paths and just get the .nnn number
            for key in self.pathDict.keys():
                for i in range(len(self.pathDict[key])):
                    try:
                        self.pathDict[key][i] = int(self.pathDict[key][i].split('.')[-1])
                    except ValueError:
                        self.pathDict[key].pop(i)
                    except IndexError:
                        pass

            ### GET THE NUMBERS THAT HAVE ALL 4 FILES:
            allFour = set(self.pathDict['param'])
            for key in self.pathDict.keys():
                allFour &= set(self.pathDict[key])
            allFour = sorted(allFour)
            return list(allFour)
        except OSError:
            return []

    @cachedProperty
    def trackedLecs(self):
        return TrackedDatabase(self, 'lecs', keys = self.trackKeys)
    @cachedProperty
    def trackedIons(self):
        return TrackedDatabase(self, 'ions', keys = self.trackKeys)

    
class OutputPoint(object):
    '''A object that provides an API to access data from Tristan-mp
    particle-in-cell simulations. The specifics of your simulation should be
    defined as a class that extends this object.'''
    #params = ['comp','bphi','btheta',]
    def __init__(self, dirpath=None, n=1, xtraStride = 1):
        self.dir = str(dirpath)
        self.xtraStride = xtraStride

        self.n=str(n).zfill(3)
        ### add the ions
        self.ions = Ions(self, name='ions') # NOTE: the name must match the attritube name
        # e.g. self.ions ===> name ='ions'
        ### add the electrons
        self.lecs = Electrons(self, name='lecs')


    def loadParam(self, key):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f[key][0]
        except IOError:
            return np.nan

    # Fields
    def loadFieldQuantity(self, key):
        try:
            with h5py.File(os.path.join(self.dir,'flds.tot.'+self.n),'r') as f:
                return f[key][:,:,:]
        except IOError:
            return np.array([])

    
    @cachedProperty
    def ex(self):
        return self.loadFieldQuantity('ex')

    @cachedProperty
    def ey(self):
        return self.loadFieldQuantity('ey')

    @cachedProperty
    def ez(self):
        return self.loadFieldQuantity('ez')

    @cachedProperty
    def bx(self):
        return self.loadFieldQuantity('bx')

    @cachedProperty
    def by(self):
        return self.loadFieldQuantity('by')

    @cachedProperty
    def bz(self):
        return self.loadFieldQuantity('bz')
    @cachedProperty
    def jx(self):
        return self.loadFieldQuantity('jx')

    @cachedProperty
    def jy(self):
        return self.loadFieldQuantity('jy')

    @cachedProperty
    def jz(self):
        return self.loadFieldQuantity('jz')

    @cachedProperty
    def dens(self):
        return self.loadFieldQuantity('dens')

    # SOME SIMULATION WIDE PARAMETERS
    @cachedProperty
    def comp(self):
        return self.loadParam('c_omp')

    @cachedProperty
    def bphi(self):
        return self.loadParam('bphi')

    @cachedProperty
    def btheta(self):
        return self.loadParam('btheta')

    @cachedProperty
    def sigma(self):
        return self.loadParam('sigma')

    @cachedProperty
    def c(self):
        return self.loadParam('c')

    @cachedProperty
    def delgam(self):
        return self.loadParam('delgam')

    @cachedProperty
    def gamma0(self):
        return self.loadParam('gamma0')

    @cachedProperty
    def istep(self):
        return self.loadParam('istep')

    @cachedProperty
    def me(self):
        return self.loadParam('me')

    @cachedProperty
    def mi(self):
        return self.loadParam('mi')

    @cachedProperty
    def mx(self):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f['mx'][:]
        except IOError:
            return np.array([])

    @cachedProperty
    def mx0(self):
        return self.loadParam('mx0')

    @cachedProperty
    def my(self):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f['my'][:]
        except IOError:
            return np.array([])

    @cachedProperty
    def my0(self):
        return self.loadParam('my0')

    @cachedProperty
    def mz0(self):
        return self.loadParam('mz0')

    @cachedProperty
    def ntimes(self):
        return self.loadParam('ntimes')

    @cachedProperty
    def ppc0(self):
        return self.loadParam('ppc0')

    @cachedProperty
    def qi(self):
        return self.loadParam('qi')

    @cachedProperty
    def sizex(self):
        return self.loadParam('sizex')
    @cachedProperty
    def sizey(self):
        return self.loadParam('sizey')

    @cachedProperty
    def stride(self):
        return self.loadParam('stride')

    @cachedProperty
    def time(self):
        return self.loadParam('time')

    @cachedProperty
    def walloc(self):
        return self.loadParam('walloc')

    @cachedProperty
    def xinject2(self):
        return self.loadParam('xinject2')


if __name__=='__main__':
    import time
    import matplotlib.pyplot as plt
    mySim = TristanSim('../batchTristan/c_omp_8_ppc0_16_ntimes_32_mx0_320_my0_320tristan-mp2d/output')
    #mySim.build_tracked_prtls('lecs')
    #mySim.build_tracked_prtls('ions')
    print(mySim.output[0].ions.x)
    print(mySim.output[0].ex)
    tic = time.time()
    print(mySim.trackedLecs.tags[0])
    #func = lambda p: np.max(p.gamma)
    #print(func(mySim.trackedLecs[0]))
    mySim.trackedLecs.sort(lambda p: p.gamma[-1])

    for prtl in mySim.trackedLecs[0:-10]:
        plt.plot(prtl.t, prtl.gamma, 'lightgray')
    for prtl in mySim.trackedLecs[-10:]:
        plt.plot(prtl.t, prtl.gamma, 'k')

    plt.show()
    toc = time.time()
    print(toc-tic)
    tic = time.time()
    print(mySim.trackedLecs.tags[0])
    toc = time.time()
    print(toc-tic)

