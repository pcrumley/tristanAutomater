Analyze and run your *tristan-MP* simulations without boiler-plate. tristanUtils consists of two main utilities: `automater.py` a python script that will submit tristan scripts using the slurm workload manager & a python 3 class `TristanSim` which exposes the data saved by *tristan-MP*. 

All documentation of these utilities is at this project's [Github-Page](https://pcrumley.github.io/tristanUtils)

## Known issues for automater.py
Will not work for 3D runs (will work for 2D runs, 1D runs not tested but should work.)

Currently assume every job has roughly the same computational cost when doing load balancing accross slurm scripts. May want to consider a mode where more cells or particles means that more cores are dedicated to the run.


## Known issues for TristanSim class
Consider switching the trackedLecs/trackedIons objects into a pandas dataframe

## Known issues for helperFuncs
There are no helper functions yet. Need to add histograms, moments in 1D and 2D. 
