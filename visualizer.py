from tristanSim  import TristanSim
import yaml, os
import matplotlib.pyplot as plt

"""
yamlFile='config.yaml'
with open(yamlFile, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        #print(config)
    except yaml.YAMLError as exc:
        print(exc)
        
outdir = config['ROOT_DIRECTORY']
"""

outdir = '../batchTristan'
runs = []
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

# Here's an example of plotting the 5th time step of ex of each run in a 6 x 3 grid

plt.plot(runs[5][2].bx[0,3,:])
plt.show()

fig = plt.figure()
axes = fig.subplots(6,3).flatten()
print(axes)
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
