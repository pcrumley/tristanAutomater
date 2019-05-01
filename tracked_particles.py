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
        if os.path.exists(outdir):
            tlist = sorted(filter(lambda x: x.split('.')[0] =='testprt',os.listdir(outdir)))
            tlist = list(tlist)[start:stop]
            # First build all the tags
            for tfile in tlist:
                with h5py.File(os.path.join(outdir,tfile) ,'r') as f:
                    tag = np.empty(len(f['ind']), dtype = 'int64')
                    with f['ind'].astype('int64'):
                        tag[:] = np.abs(f['ind'][:])
                    with f['proc'].astype('int64'):
                        tag[:] += np.abs(f['proc'][:]*2147483648)
                    self.tags = np.union1d(self.tags, tag)
                   
            # Produce a mask and an order
            #self._mask = np.ones(len(self.tags),type='bool')
            self._order = np.arange(len(self.tags))

            # GET THE LOCATION OF ALL THE BREAKS
            n = np.zeros(len(self.tags), dtype = 'int64')
            for tfile in tlist:
                with h5py.File(os.path.join(outdir, tfile) ,'r') as f:
                    tag = np.empty(len(f['ind']), dtype = 'int64')
                    with f['ind'].astype('int64'):
                        tag[:] = np.abs(f['ind'][:])
                    with f['proc'].astype('int64'):
                        tag[:] += np.abs(f['proc'][:]*2147483648)
                        tag = np.sort(tag)
                    inTime = np.take(tag, np.searchsorted(tag, self.tags), mode='wrap')==self.tags
                n += inTime
            self.breaks = np.append([0],np.cumsum(n))
            offset = np.zeros(len(self.tags), dtype = 'int64')
            # Now we build all the arrays to get unfolded data
            self._t = np.zeros(int(np.sum(n)))
            
            for key in self.keys:
                setattr(self, '_'+ key, np.ones(int(np.sum(n))))
            for tfile in tlist:
                with h5py.File(os.path.join(outdir, tfile) ,'r') as f:
                    tcur=int(tfile.split('.')[-1])*sim.output[0].c/sim.output[0].comp
                    tag = np.empty(len(f['ind']), dtype = 'int64')
                    with f['ind'].astype('int64'):
                        tag[:] = np.abs(f['ind'][:])
                    with f['proc'].astype('int64'):
                        tag[:] += np.abs(f['proc'][:]*2147483648)
                    #Get the starting loc of the array
                    allLocation=np.searchsorted(self.tags, tag)
                    curloc = np.take(self.breaks, allLocation)
                    curloc += np.take(offset, allLocation)

                    self._t[curloc] = tcur
                    for elm in self.keys:
                        getattr(self,'_'+elm)[curloc] = f[elm][:]

                tag = np.sort(tag)
                inTime = np.take(tag, np.searchsorted(tag, self.tags),mode='wrap')==self.tags
                offset += inTime

    ### Now we need to overload things like __len__ and 
    ### __getitem__ so it looks like a list
    def __len__(self):
        #return np.sum(self._mask)
        return len(self.tags)
    def sort(self, func):
        tmpFunc= lambda x:func(self[x])
    ### rearranges the ordering so you can get 10 most energetic prtl e.g.
        self._order = sorted(range(len(self)), key=tmpFunc)

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
        for key in database.keys:
            setattr(self, key, getattr(database, '_'+key)[database.breaks[num]:database.breaks[num+1]])
