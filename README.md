Analyze and run your *tristan-MP* simulations without boiler-plate. tristanUtils consists of three main utilities: `automater.py` a python script that will submit tristan scripts using the slurm workload manager, a python 3 class `TristanSim` which exposes the data saved by *tristan-MP*, and set of helper function in `helperFuncs.py`

All documentation of these utilities is at this project's [Github-Page](https://pcrumley.github.io/tristanUtils)

## Automater.py
Make it easy to submit many many small *tristan-MP* jobs. Documentation [here](https://pcrumley.github.io/tristanUtils/automater.html)

Will not work for 3D runs (will work for 2D runs, 1D runs not tested but should work.)

Currently assume every job has roughly the same computational cost when doing load balancing accross slurm scripts. May want to consider a mode where more cells or particles means that more cores are dedicated to the run.


## TristanSim class
An Object Relational Mapping (ORM) that makes it easy to access all your tristan data as attributes of an object. e.g., any value in the `i`th output step can be accessed as sim[i].ex for example. Documentation [here](https://pcrumley.github.io/tristanUtils/tristanSim.html)

Consider switching the trackedLecs/trackedIons objects into a pandas dataframe

Needs to build faster (takes 10 seconds to open a sim that is like 100 outputfiles.)

## helperFuncs
Easy way to make matplotlib plots. I have phase diagrams, 2D averages, and 1D hist and 1d averages implemented. Documentation  [here](https://pcrumley.github.io/tristanUtils/helperFunc.html). Note: documentation is incomplete.
