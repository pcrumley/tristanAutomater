from tristanSim  import TristanSim
import yaml, os
import matplotlib.pyplot as plt
import numpy as np

yamlFile='config.yaml'
with open(yamlFile, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        #print(config)
    except yaml.YAMLError as exc:
        print(exc)
        
#outdir = config['ROOT_DIRECTORY']

outdir = '../batchTristan'
runs = []
# runs will be a list that looks like this 
#[[  run1_t1, run1_t2, run1_t3...],
#[run2_t1, run2_t2, ...]
#[runN_t1, runN_t2, ...]]

# So any can be accessed as run5 = runs[4]
# and or run5Time3 = runs[4][2]

runNames = []
for elm in os.listdir(outdir):
    elm = os.path.join(outdir, elm)
    if os.path.isdir(elm):
        runNames.append(os.path.split(elm)[-1])
        elm = os.path.join(elm,'output')
        if os.path.exists(elm):
            runs.append([TristanSim(elm, n = x) for x in TristanSim(elm).get_file_nums()])

# TristanSim is an object that exposes an API to access tristan.
# The cool thing is nothing is loaded until it is accessed for first time, then it is cached.

# fields are accessed via sim.ex [ex, ey, ez, bx, by, bz, dens...]
# particle values are accessed like sim.ions.x or sim.lecs.y etc..

# Here's an example of plotting the 5th time step of ex of each run
# in a 6 x 3 grid. Because of how I set up the searcher, all are at the
# same physical time.

fig = plt.figure()
axes = fig.subplots(6,3).flatten()
#print(axes)
j = 0
for run, name in zip(runs, runNames):
    ax = axes[j]
    istep = run[3].istep
    comp = run[3].comp
    ex = run[3].ex[0,:,:]
    ax.imshow(ex,extent=(0, ex.shape[1]*istep/comp, 0, ex.shape[0]*istep/comp), origin = 'lower')
    ax.set_title(name)
    #plt.colorbar()
    j += 1
#plt.savefig('test.png')
plt.show()


### As another example, let's plot all the total electron energy
## as function of time for each run

# I know I changed c_omp, ntimes and ppc. get from YAML

c_omp_val = config['paramOpts']['c_omp']
ppc_val = config['paramOpts']['ppc0']
ntimes_val = config['paramOpts']['ntimes']

# Some arrays that change what the lines will look like
ms = ['.', 'x', '4', '8']
ls = ['-', '--', ':', '-.']
color = ['b', 'r', 'g', 'y']

fig = plt.figure()
for run in runs:
    plt.plot([t.time for t in run], [np.average(t.lecs.KE) for t in run],
             c = color[ppc_val.index(run[0].ppc0)],
             linestyle = ls[ntimes_val.index(run[0].ntimes)],
             marker = ms[c_omp_val.index(run[0].comp)], markersize = 10)
plt.show()
