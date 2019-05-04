### Helper functions
UPDATE THIS, but for now, working examples.

```python
from tristanSim  import TristanSim
from helperFuncs import hist1D, hist2D, avg1D, avg2D
import os
import matplotlib.pyplot as plt
import numpy as np

###
# Some helper functions. So far we have hist1d, avg1,
# hist2D, avg2D.
###

# Use TristanSim class to get access to data.
myRun = TristanSim('/Path/To/Output/')

# Further documentation explanation may follow but for now,
# See these examples

# you can take a histogram of particle quantity as
hist1D(myRun[0].xe)
plt.show()

# admittedly this isn't much better than plt.hist, except about 20 faster.
# you can pass the hist1D any kwargs that go to plt.plot(), and you can
# pass and Axes object if you want. As in plt.plot(). hist1D returns
# as Line2D object.

# Here's a spectrum
fig, ax = plt.subplots()
xmin = min(myRun[0].gammae.min(),myRun[0].gammai.min())
xmax = max(myRun[0].gammae.max(),myRun[0].gammai.max())
hist1D(myRun[0].gammae-1, ax = ax, range=(xmin,xmax), 
  bins=200, xscale='log', yscale='log', c='r', label ='lecs')
hist1D(myRun[0].gammai-1, ax = ax, range=(xmin,xmax), 
  bins=200, xscale='log', yscale='log', c='b', label ='ions')
plt.xlabel('$\gamma-1$')
plt.ylabel('$EdN/dE$')
plt.legend()
plt.show()

# Much more valuable is the ability to make phase plots.

hist2D(myRun[0].xi, myRun[0].gammai-1, clabel='$f_i(p)$')
plt.xlabel('$x_i$')
plt.ylabel('$KE_i$')
plt.show()

# And you can average over a y quantity in bins of x. Here is the average
# ion energy as function of distance.

avg1D(myRun[0].xi, myRun[0].gammai-1)
plt.xlabel('$x_i$')
plt.ylabel(r'$\langle \gamma_i-1 \rangle$')
plt.show()

# Or you can do the same in 2D. (now electrons).
avg2D(myRun[0].xe, myRun[0].ye, myRun[0].gammae-1, 
  cnorm = 'log', bins = [100,50], clabel=r'$\langle KE \rangle$')
plt.xlabel('$x_e$')
plt.ylabel('$y_e$')
plt.show()
```
