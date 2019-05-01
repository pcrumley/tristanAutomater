import numpy as np
import h5py, os

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


class Particles(object):
    '''A base object that holds the info of one type of particle in the simulation
    '''
    __prtl_types = []
    def __init__(self, sim, name):
        self.sim = sim
        self.name = name
        self.__prtl_types.append(name)
        self.quantities = []

    def loadPrtlData(self, key):
        try:
            with h5py.File(os.path.join(self.sim.dir,'prtl.tot.'+self.sim.n),'r') as f:
                return f[key][::self.sim.xtraStride]
        except IOError:
            return np.array([])


    @classmethod
    def get_prtls(cls):
        return cls.__prtl_types

class Ions(Particles):
    '''The ion subclass'''
    def __init__(self, sim, name='ions'):
        Particles.__init__(self, sim, name)
    @cachedProperty
    def x(self):
        return self.loadPrtlData('xi')/self.sim.comp

    @cachedProperty
    def y(self):
        return self.loadPrtlData('yi')/self.sim.comp

    @cachedProperty
    def z(self):
        return self.loadPrtlData('zi')/self.sim.comp

    @cachedProperty
    def px(self):
        return self.loadPrtlData('ui')

    @cachedProperty
    def py(self):
        return self.loadPrtlData('vi')

    @cachedProperty
    def pz(self):
        return self.loadPrtlData('wi')

    @cachedProperty
    def charge(self):
        return self.loadPrtlData('chi')

    @cachedProperty
    def gamma(self):
        # an example of a calculated quantity
        return np.sqrt(self.px**2+self.py**2+self.pz**2+1)

    @cachedProperty
    def KE(self):
        # an example of a calculated quantity could use
        return (self.gamma-1)


    @cachedProperty
    def proc(self):
        return self.loadPrtlData('proci')

    @cachedProperty
    def index(self):
        return self.loadPrtlData('indi')


class Electrons(Particles):
    '''The electron subclass'''
    def __init__(self, sim, name='electrons'):
        Particles.__init__(self, sim, name)
    @cachedProperty
    def x(self):
        return self.loadPrtlData('xe')/self.sim.comp

    @cachedProperty
    def y(self):
        return self.loadPrtlData('ye')/self.sim.comp

    @cachedProperty
    def z(self):
        return self.loadPrtlData('ze')/self.sim.comp

    @cachedProperty
    def px(self):
        return self.loadPrtlData('ue')

    @cachedProperty
    def py(self):
        return self.loadPrtlData('ve')

    @cachedProperty
    def pz(self):
        return self.loadPrtlData('we')

    @cachedProperty
    def charge(self):
        return self.loadPrtlData('che')

    @cachedProperty
    def gamma(self):
        # an example of a calculated quantity could use
        return np.sqrt(self.px**2+self.py**2+self.pz**2+1)

    @cachedProperty
    def KE(self):
        # an example of a calculated quantity could use
        return (self.gamma-1)*self.sim.me/self.sim.mi

    @cachedProperty
    def proc(self):
        return self.loadPrtlData('proce')

    @cachedProperty
    def index(self):
        return self.loadPrtlData('inde')
