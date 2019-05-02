TristanSim is an object that exposes an API to access *tristan-MP* simulations. 
All of the data attributes are lazily evaluated, so the first time you access it, 
they load from disk, but the next time it is cached.

## Code structure & implementation

### Basic Tristan Outputs
The TristanSim object takes a path to a directory upon initialization. Then it looks in that directory for any 
file matching names `flds.tot.*`, `prtl.tot.*`, `param.*` and `spect.*`. If all 4 files are present it creates 
and output point for this timestep. Here's a quick example:
```python
from tristanSim import TristanSim
myRun = TristanSim('/path/to/tristan/output/')
```
The simulation object has been built. All output points are accessible in `myRun.output`


Since the output attribute is just a list, we can access any of the output points using simple
list operators. e.g., `len(myRun.output)` gives the number of output files, access the first 
one by `myRun.output[0]` or you can iterate over them.
```python
for out in myRun.output:
    # Do something for each output point here
```

To access the data on the disk you have to look at one of the objects in an output point. For instance 
```python
out4 = myRun.output[4]
out4.fields 
# Fields is a pointer to the 5th flds.tot file in your output dir
# you can see the attributes saved to the disk here by
print(out4.fields.keys()) 
# you can get any of those attributes by typing e.g.,
out4.fields.ex
```
`fields.ex` is lazily evaluated. The first time it is read from the hdf5 file, but afterwards it is in memory. If you want to delete it and reload `out4.fields.reload()` Then you can access it from teh disk by typing `out4.fields.ex`.

`out4.prtl`, `out4.spect` and `out4.param` are similarly defined. If you want to add additional hdf5 output files to look for, you can do so in the `__init__()` function of the TristanSim class.

### Fancy Examples
If you have a suite of runs you had run with [automater.py](automater.md), 
this class comes in handy. 

Building an iterable list of all your runs in a directory:
```python
import matplotlib.pyplot as plt
import numpy as np
from tristanSim import TristanSim

# Point to the directory where the suite of runs
# In this example I have 9 different simulations saved in
# ../batchTristan
outdir = '../batchTristan'

# Let's create a list that will hold all our simulation 
# instances.
runs = []

# We'll also name each run based on the directory it resides.
runNames = [] 

for elm in os.listdir(outdir):
    elm = os.path.join(outdir, elm)
    if os.path.isdir(elm):
        elm = os.path.join(elm,'output')
        if os.path.exists(elm):
            runs.append(TristanSim(elm))
            runNames.append(os.path.split(os.path.split(elm)[0])[-1])

# Now, any run can be accessed 
# e.g. runs[4], with a name runNames[4]
# to access the 3rd output time of run4: e.g. runs[4].output[3]
```

Plotting ex of the 5th output timestep of each simulation in a 3x3 grid 

```python
# Here's an example of plotting the 5th time step of ex of each run
# in a 3 x 3 grid. Because of how I set up the automater, all are at the
# same physical time.

fig = plt.figure()
axes = fig.subplots(3,3).flatten()
#print(axes)
j = 0
for run, name in zip(runs, runNames):
    ax = axes[j]
    istep = run.output[5].param.istep
    comp = run.output[5].param.c_omp
    ex = run.output[5].flds.ex[0,:,:]
    ax.imshow(ex,extent=(0, ex.shape[1]*istep/comp, 0, ex.shape[0]*istep/comp), origin = 'lower')
    ax.set_title(name)
    #plt.colorbar()
    j += 1
    if j == 18:
        break
#plt.savefig('test.png')
plt.show()
```

Let's plot all the total electron energy as function of time for each run, where the colors, line-styles,
and marker styles depend on c_omp, ppc and ntimes.

```python
# First get all of the unique values of c_omp, ppc and ntimes from our suite of runs.

c_omp_val = list(set([run.output[0].param.c_omp for run in runs]))
ppc_val = list(set([run.output[0].param.ppc0 for run in runs]))
ntimes_val = list(set([run.output[0].param.ntimes for run in runs]))

# Lists that store what the linestyles will be.
ms = ['.', 'x', '4', '8']
ls = ['-', '--', ':', '-.']
color = ['b', 'r', 'g', 'y']

fig = plt.figure()
for run in runs:
    # In this example, we have fast moving test particles that have negative indices we don't want to count
    # towards this energy.
    plt.plot([o.param.time for o in run.output], 
    [np.average(o.prtl.gammae[o.prtl.inde>0]-1) for o in run.output],
             c = color[ppc_val.index(run.output[0].param.ppc0)],
             linestyle = ls[ntimes_val.index(run.output[0].param.ntimes)],
             marker = ms[c_omp_val.index(run.output[0].param.comp)], markersize = 10)
plt.show()
```

### Tracking Prtls.

UPDATE THIS SECTION!

```python
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
# plot t vs gamma for a random prtl
choice = np.random.randint(len(myRun.trackedLecs))
randPrtl = myRun.trackedLecs[choice]
# Each prtl has the following attributes: 'x', 'y', 'u', 'v', 'w', 
# 'gamma', 'bx', 'by', 'bz', 'ex', 'ey', 'ez'
plt.plot(randPrtl.t, randPrtl.gamma)
plt.show()
# This is nice, but let's say you want to find the 10 highest energy
# prtls you saved.
# First sort by energy. You can pass any function here
myRun.trackedLecs.sort(lambda x: np.max(x.gamma))
# now plot the botton N
for prtl in myRun.trackedLecs[:-10]:
    plt.plot(prtl.t, prtl.gamma, 'lightgray')
for prtl in myRun.trackedLecs[-10:]:
    plt.plot(prtl.t, prtl.gamma, 'k')
plt.show()
```
