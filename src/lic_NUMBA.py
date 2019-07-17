# A NUMBA based implementation of the code found here:
# https://scipy-cookbook.readthedocs.io/items/LineIntegralConvolution.html
import numpy as np
from numpy import ones
from numba import jit, guvectorize, float64, int32

@jit
def advance(vx, vy, xyArr, fxfyArr, w, h):
    if vx>=0:
        tx = (1-fxfyArr[1])/vx
    else:
        tx = -fxfyArr[1]/vx
    if vy>=0:
        ty = (1-fxfyArr[0])/vy
    else:
        ty = -fxfyArr[0]/vy
    if tx<ty:
        if vx>=0:
            xyArr[1]+=1
            fxfyArr[1]=0
        else:
            xyArr[1]-=1
            fxfyArr[1]=1
        fxfyArr[0]+=tx*vy
    else:
        if vy>=0:
            xyArr[0]+=1
            fxfyArr[0]=0
        else:
            xyArr[0]-=1
            fxfyArr[0]=1
        fxfyArr[1]+=ty*vx
    if xyArr[1]>=w:
        xyArr[1]=w-1 # FIXME: other boundary conditions?
    if xyArr[1]<0:
        xyArr[1]=0 # FIXME: other boundary conditions?
    if xyArr[0]<0:
        xyArr[0]=0 # FIXME: other boundary conditions?
    if xyArr[0]>=h:
        xyArr[0]=h-1 # FIXME: other boundary conditions?


@jit(nopython=True)
def line_integral_convolution(vx, vy, texture, kernel):
    h = vx.shape[0]
    w = vx.shape[1]
    kernellen = kernel.shape[0]
    if h!=vy.shape[0] or w != vy.shape[1] :
        raise ValueError('Vx and Vy must the same shape')
    if h!=texture.shape[0] or w != texture.shape[1] :
        raise ValueError('The texture must have the same shape as the vectors')
    result = np.zeros((h,w),dtype=np.float32)

    xyArr = np.ones(2, dtype=np.int32)
    fxfyArr = np.empty(2, dtype=np.float64)
    for i in range(h):
        for j in range(w):
            xyArr[0] = i
            xyArr[1] = j
            fxfyArr[0] = 0.5
            fxfyArr[1] = 0.5

            k = kernellen//2
            #print i, j, k, x, y
            result[i,j] += kernel[k]*texture[xyArr[0],xyArr[1]]
            while k<kernellen-1:
                advance(vx[xyArr[0],xyArr[1]],vy[xyArr[0],xyArr[1]],
                        xyArr, fxfyArr, w, h)
                k+=1
                #print i, j, k, x, y
                result[i,j] += kernel[k]*texture[xyArr[0],xyArr[1]]
            xyArr[0] = i
            xyArr[1] = j
            fxfyArr[0] = 0.5
            fxfyArr[1] = 0.5

            while k>0:
                advance(vx[xyArr[0],xyArr[1]],vy[xyArr[0],xyArr[1]],
                        xyArr, fxfyArr, w, h)
                k-=1
                #print i, j, k, x, y
                result[i,j] += kernel[k]*texture[xyArr[0],xyArr[1]]
    return result
if __name__ == "__main__":

    import numpy as np
    import pylab as plt

    #import lic_internal

    dpi = 100
    size = 700
    video = False

    vortex_spacing = 0.5
    extra_factor = 2.

    a = np.array([1,0])*vortex_spacing
    b = np.array([np.cos(np.pi/3),np.sin(np.pi/3)])*vortex_spacing
    rnv = int(2*extra_factor/vortex_spacing)
    vortices = [n*a+m*b for n in range(-rnv,rnv) for m in range(-rnv,rnv)]
    vortices = [(x,y) for (x,y) in vortices if -extra_factor<x<extra_factor and -extra_factor<y<extra_factor]


    xs = np.linspace(-1,1,size).astype(np.float64)[None,:]
    ys = np.linspace(-1,1,size).astype(np.float64)[:,None]

    vectors = np.zeros((size,size,2),dtype=np.float64)
    for (x,y) in vortices:
        rsq = (xs-x)**2+(ys-y)**2
        vectors[...,0] +=  (ys-y)/rsq
        vectors[...,1] += -(xs-x)/rsq

    texture = np.random.rand(size,size).astype(np.float64)


    frame=0
    kernellen=31
    kernel = np.sin(np.arange(kernellen)*np.pi/kernellen)
    kernel = kernel.astype(np.float64)

    image = line_integral_convolution(vectors[:,:,0], vectors[:,:,1], texture, kernel)

    plt.clf()
    plt.axis('off')
    plt.figimage(image)
    plt.gcf().set_size_inches((size/float(dpi),size/float(dpi)))
    plt.show()
    #plt.savefig("flow-image.png",dpi=dpi)

    import sys
    sys.path.append('/perseus/scratch/gpfs/pcrumley/tristanAutomater/')
    sys.path.append('/perseus/scratch/gpfs/pcrumley/tristanAutomater/src')
    from tristanSim import TristanSim
    from tracked_particles import TrackedDatabase
    from matplotlib.colors import Normalize

    homeDir = '/home/pcrumley/tig/Projects/TransRelShocks/Runs/gamBeta3ParaWTracking/output'
    #homeDir = '/perseus/scratch/gpfs/pcrumley/ShockWTrackingStamepde/output'
    s=TristanSim(homeDir)

    #bx = s[-1].bx[0,:,1600:6000]
    #by = s[-1].by[0,:,1600:6000]
    #bz = s[-1].bz[0,:,1600:6000]
    #dens = s[-1].dens[0,:,1600:6000]
    bx = s[-1].bx[0,:,5*1105:-3000]
    by = s[-1].by[0,:,5*1105:-3000]
    dens = s[-1].dens[0,:,5*1105:-3000]
    #bz[bz<-.2]=-0.5
    #bz[bz>33]=33
    #bz = np.sqrt(np.abs(bz))*np.sign(bz)
    
    
    texture = np.random.rand(by.shape[0],by.shape[1]).astype(np.float64)
    #texture *= bz
    kernellen=51
    kernel = np.sin(np.arange(kernellen)*np.pi/kernellen)
    kernel = kernel.astype(np.float64)

    weights = line_integral_convolution(bx, by, texture, kernel)
    alphas = Normalize(None, None, clip=True)(np.sign(weights-np.average(weights))*np.sqrt(np.abs(weights-np.average(weights))))
    alphas[alphas<.6] = .15
    alphas[alphas>.75] = .9

    bw = plt.cm.binary
    colors = Normalize(None, None)(np.sign(weights-np.average(weights))*np.abs(weights-np.average(weights))**.33  ) 
    colors = bw(colors)
    colors[..., -1] = alphas
    #print(np.min(image), np.max(image))
    #image[image<0.5]=np.nan
    #plt.imshow(bz)
    plt.imshow(dens, clim=(0,5*8))
    plt.imshow(colors)#, cmap='binary', alpha=.75)
    
    plt.show()
    
