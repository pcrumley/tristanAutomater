import h5py
import os, re
import numpy as np

class TrackedDatabase(object):
    def __init__(self, sim, species, start = None, stop = None, keys=['x', 'y', 'u', 'v', 'w', 'gamma', 'bx', 'by', 'bz', 'ex', 'ey', 'ez']):

        ### When the tracked database is initialized it creates the database
        #
        # HERE IS THE CODE TO DO THAT. IT IS COMPLICATED AND SLOW.
        #
        ###
        outdir = os.path.join(sim.dir,'tracking_elec') if species == 'lecs' else os.path.join(sim.dir, 'tracking_ion')
        self.keys = keys
        self.keys.remove('t')
        self.tags = np.array([], dtype='int64')
        self._t = np.array([])
        for key in self.keys:
            setattr(self, '_'+ key, np.array([], dtype='f8'))

        if os.path.exists(outdir):
            tlist = sorted(filter(lambda x: x.split('.')[0] =='testprt',os.listdir(outdir)))
            tlist = list(tlist)[start:stop]
            # UPDATING ALGORITHM SO ONLY READS ONCE
            for tfile in tlist:
                with h5py.File(os.path.join(outdir,tfile) ,'r') as f:
                    tmpTags = np.empty(len(f['ind']), dtype = 'int64')
                    with f['ind'].astype('int64'):
                        tmpTags[:] = np.abs(f['ind'][:])
                    with f['proc'].astype('int64'):
                        tmpTags[:] += np.abs(f['proc'][:]*2147483648)
                    self.tags = np.append(self.tags, tmpTags)
                    self._t = np.append(self._t,np.ones(len(f['ind']))*int(tfile.split('.')[-1])*sim[0].c/sim[0].c_omp)
                    for elm in self.keys:
                        setattr(self, '_'+elm, np.append(getattr(self,'_'+elm),f[elm][:]))
            ### collapse the tags and get the breaks

            sortArgs = np.lexsort((self._t, self.tags))
            self.tags, pcounts = np.unique(self.tags, return_counts=True)
            self.breaks = np.append([0],np.cumsum(pcounts))

            #self._t = self._t[sortArgs]
            setattr(self, '_t', getattr(self,'_t')[sortArgs])
            for elm in self.keys:
                setattr(self, '_'+elm, getattr(self,'_'+elm)[sortArgs])

            # Produce a mask and an order
            self._mask = np.ones(len(self.tags),dtype='bool')
            self._order = np.arange(len(self.tags))

                

    ### Now we need to overload things like __len__ and 
    ### __getitem__ so it looks like a list
    def __len__(self):
        #return np.sum(self._mask)
        return len(self._order)
    def sort(self, func):
        tmpFunc= lambda x:func(self[x])
        ### rearranges the ordering so you can get 10 most energetic prtl e.g.
        self._order = np.array(sorted(range(len(self)), key=tmpFunc))
        
    def mask(self, func):
        ### rearranges the ordering so you can get 10 most energetic prtl e.g.
        self._mask = list(map(func, self))
        self._order = self._order[self._mask]

    def unmask(self):
        ### rearranges the ordering so you can get 10 most energetic prtl e.g.
        self._mask = np.ones(len(self.tags), dtype='bool')
        self._order = np.arange(len(self.tags))

    def __getitem__(self, val):
        if isinstance(val, slice):
            start = 0 if val.start is None else val.start%len(self)
            stop = len(self) if val.stop is None else val.stop%len(self)
            step = 1 if val.step is None else val.step
            return [TrackedPrtl(self,self._order[i]) for i in range(start, stop, step)]
        return TrackedPrtl(self, self._order[val])

class TrackedPrtl(object):
    def __init__(self, database, num):
        self.t = database._t[database.breaks[num]:database.breaks[num+1]]
        sortArg = np.argsort(self.t)
        #self.t= self.t[sortArg]
        for key in database.keys:
            setattr(self, key, (getattr(database, '_'+key)[database.breaks[num]:database.breaks[num+1]]))#[sortArg])

if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir))
    from tristanSim  import TristanSim
    from helperFuncs import *

    import matplotlib.pyplot as plt
    

    outdir = '../../batchTristan'
    runs = []
    # runs will be a list a tristan simulations instances
    # that reside in outdir



    runNames = [] #the directory name that automater created.
    for elm in os.listdir(outdir):
        elm = os.path.join(outdir, elm)
        if os.path.isdir(elm):
            elm = os.path.join(elm,'output')
            if os.path.exists(elm):
                runs.append(TristanSim(elm))
                runNames.append(os.path.split(os.path.split(elm)[0])[-1])

    ###
    #
    # EXAMPLE OF TRACKING PARTICLES
    #
    ###

    # you'll find all of the tracked particles in a trackedLecs and
    # trackedIon object. The first call builds the database which may take
    # awhile. It is saved afterwards. Let's plot a single tracked electron
    # for these runs we didn't track the ions.

    # Let's focus just on one run for simplicity

    myRun = runs[0]
    lecsDB = myRun.trackedLecs
    # let's check that data are stored properly
    firstOut = np.sort(lecsDB._t[lecsDB.breaks[0]:lecsDB.breaks[1]])
    isGood = True
    for p in lecsDB:
        isGood *= np.all(np.sort(p.t)==firstOut)
        plt.plot(p.t, '.')
    print(isGood)
    plt.show()
    # plot t vs gamma for a random prtl
    choice = np.random.randint(len(myRun.trackedLecs))
    randPrtl = myRun.trackedLecs[choice]

    # Each prtl has the following attributes: 'x', 'y', 'u', 'v', 'w',
    # 'gamma', 'bx', 'by', 'bz', 'ex', 'ey', 'ez'
    plt.plot(randPrtl.t)#, randPrtl.x)
    plt.show()
    # First sort by energy. You can pass any function here
    myRun.trackedLecs.sort(lambda x: np.max(x.gamma))
    # now plot the botton N
    for prtl in myRun.trackedLecs[:-10]:
        plt.plot(prtl.t, prtl.gamma, 'lightgray')

    for prtl in myRun.trackedLecs[-10:]:
        plt.plot(prtl.t, prtl.gamma, 'k')

    plt.show()

    # You can also apply a mask to your particle to choose ones
    # matching a certain criteria. You can pass any function
    # that returns a truthy value
    myRun.trackedLecs.mask(lambda x: np.max(x.gamma)>10.1)
    plt.subplot(211)
    for prtl in myRun.trackedLecs:
        plt.plot(prtl.t, prtl.gamma)
    # Masks are applied successively. However you can unmask.
    # Let's plot all the other prtls
    myRun.trackedLecs.unmask()
    myRun.trackedLecs.mask(lambda x: np.max(x.gamma)<10.1)
    plt.subplot(212)
    for prtl in myRun.trackedLecs:
        plt.plot(prtl.t, prtl.gamma)

    plt.show()

