# tristanAutomator
A simple way batch run tristan-mp simulations with a slurm workload manager system

The code is cofigured through the config.yaml file. After that run `python automater.py`
and it will submit the jobs for you.

## Example uses

Say you want to run the same job with mi/me = 1, 32, 124. You want all the boxes to be 50 x 50 
c/omega_pi, and you want each to be it's own slurm script taking 4 nodes. Edit the `config.yaml` file  to look something like

```
BASE_INPUT_FILE: '/PATH/TO/YOUR/input' # we take these values as the base                                                              
ROOT_DIRECTORY: '/PATH/TO/batchTristanOUT/' #don't worry about creating this dir but it will overwrite                 

paramOpts:                                                                                                                                                         
  mi : [1.,32.,124.]                                                                                                                                               
submitOpts:                                                                                                                                                        
  email: 'YourEmail@aol.com'                                                                                                                               
  jobs: 3                                                                                                                                                        
  nodesPerJob: 4                                                                                                                                                   
  coresPerNode: 28                                                                                                                                                 
  totalTime: '1:00:00'                                                                                                                                             
  # modules must be a list                                                                                                                                         
  modules: ['intel', 'intel-mpi', 'hdf5/intel-16.0/intel-mpi/1.8.16']                                                                                              
  # exec must be a list                                                                                                                                            
  exec: ['/PATH/TO/tristan-mp2d']                                                                                                          
                                                                                                                                                                   
outputOpts:                                                                                                                                                        
  interval: 45 # save every 45 omega_pi^-1                                                                                                                                                     
  last: 10000 # run will end after 10k omega_pi^-1                                                                                                                                                      
  units: 'omega_pi' # you can use 'omega_pe', 'omega_pi', or 'laps'                                                                                                
                                                                                                                                                                   
box:                                                                                                                                                               
  x: [50] # must be a list                                                                                                                                         
  y: [50] # must be a list                                                                                                                                         
  z: [] # must be a list                                                                                                                                           
  units: 'omega_pi' # you can use 'omega_pe', 'omega_pi', or 'cells'
```

Say instead you want to see what is more important,  increaing ppc0, c_omp, or filtering. You want to run all permutations of following: c_omp = 6, 8, 16, ntimes = 8, 32, 64 & ppc0 = 8, 16, 32. So there are 27 runs. You don't want to submit 27 slurm scripts, instead you want to submit 2 slurm scripts with 5 nodes each. Edit the `config.yaml` file  to look something like

```
BASE_INPUT_FILE: '/PATH/TO/YOUR/input' # we take these values as the base                                                              
ROOT_DIRECTORY: '/PATH/TO/batchTristanOUT/' #don't worry about creating this dir but it will overwrite                 

paramOpts:                                                                                                                                                         
  c_omp: [6,8,16]                                                                                                                                                     
  ppc0: [8,16,32]                                                                                                                                                   
  ntimes : [8,32,64]                                                                                                                                               
  sizex: [14] # each job will fill one node                                                                                                                                                       
  sizey: [2]          
submitOpts:                                                                                                                                                        
  email: 'YourEmail@aol.com'                                                                                                                               
  jobs: 2                                                                                                                                                        
  nodesPerJob: 5                                                                                                                                                   
  coresPerNode: 28                                                                                                                                                 
  totalTime: '1:00:00'                                                                                                                                             
  # modules must be a list                                                                                                                                         
  modules: ['intel', 'intel-mpi', 'hdf5/intel-16.0/intel-mpi/1.8.16']                                                                                              
  # exec must be a list                                                                                                                                            
  exec: ['/PATH/TO/tristan-mp2d']                                                                                                          
                                                                                                                                                                   
outputOpts:                                                                                                                                                        
  interval: 45 # save every omega_pe^-1                                                                                                                                                     
  last: 10000 # job will end after 10k omega_pe^-1                                                                                                                                                      
  units: 'omega_pe' # you can use 'omega_pe', 'omega_pi', or 'laps'                                                                                                
                                                                                                                                                                   
box:                                                                                                                                                               
  x: [50] # must be a list                                                                                                                                         
  y: [50] # must be a list                                                                                                                                         
  z: [] # must be a list                                                                                                                                           
  units: 'omega_pe' # you can use 'omega_pe', 'omega_pi', or 'cells'
```
Note, if you're developing tristan and you want to try different executables, you can change the yaml file to have `exec: ['path/2/tristan1', 'path/to/tristan2']`
Once you are happy with your config file, login to perseus, `module load anaconda3` and `python automater.py`. Check the `ROOT_DIRECTORY` for your runs.

## Known issues
Will not work for 3D runs (will work for 2D runs, 1D runs not tested but should work.)
