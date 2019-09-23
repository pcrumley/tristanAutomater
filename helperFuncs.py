import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as colors
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),'src/'))
from hist_helpers import *

def hist1D(x, range=None, bins=100, weights=None, xscale=None, yscale=None, ax=None, **kwargs):
    """
    Histogram takes a value and plots a line on the given ax. If ax is none,
    plt.gca() is used. All **kwargs are passed to plot() so they should be something you can send there
    """
    xvalmin = x.min() if range is None else range[0]
    xvalmax = x.max() if range is None else range[1]


    if weights is None:
        if xscale =='log' and xvalmin >0:
            hist = FastHist(np.log10(x), np.log10(xvalmin), np.log10(xvalmax), int(bins))
        else:
            hist = FastHist(x, xvalmin, xvalmax, int(bins))
    else:
        #calculate unweighed histogram
        if xscale =='log' and xvalmin >0:

            hist = FastWeightedHist(np.log10(x), weights, np.log10(xvalmin), np.log10(xvalmax), int(bins))
        else:
            hist = FastWeightedHist(x, weights, xvalmin, xvalmax, int(bins))

    if xscale =='log' and xvalmin >0:
        binEdges = np.logspace(np.log10(xvalmin), np.log10(xvalmax), int(bins)+1)
    else:
        binEdges = np.linspace(xvalmin, xvalmax, int(bins)+1)
    if ax is None:
        ax = plt.gca()
    if xscale=='log':
        ax.set_xscale('log')
    if yscale=='log':
        ax.set_yscale('log')
    # return an Line2D object like matplotlib.plot does
    return ax.plot(*stepifyHist(binEdges, hist), **kwargs)

def hist2D(x, y, xrange=None, yrange=None,  bins=[200,200],
    weights=None, cnorm = 'log', normhist=True, colorbar=True, clabel='',
     ax=None, cax = None, mask_empty=True, aspect='auto', origin='lower', **kwargs):
    """
    Histogram takes a value and plots a line on the given ax. If ax is none,
    plt.gca() is used. All **kwargs are passed to plot() so they should be something you can send there
    """
    xvalmin = x.min() if xrange is None else xrange[0]
    xvalmax = x.max() if xrange is None else xrange[1]
    yvalmin = y.min() if yrange is None else yrange[0]
    yvalmax = y.max() if yrange is None else yrange[1]

    if weights is None:
        hist = Fast2DHist(y, x, yvalmin, yvalmax, int(bins[1]), xvalmin, xvalmax, int(bins[0]))
    else:
        #calculate unweighed histogram
        hist = Fast2DWeightedHist(y, x, weights, yvalmin, yvalmax, int(bins[1]), xvalmin, xvalmax, int(bins[0]))

    ####
    #
    # Now we have the histogram, we need to turn it into an image
    #
    ###
    if normhist == True and hist.max() != 0:
        hist *= hist.max()**-1
    if mask_empty == True:
        hist[hist==0] = np.nan
    if ax is None:
        ax = plt.gca()
    im = ax.imshow(hist, extent = (xvalmin, xvalmax, yvalmin, yvalmax), origin=origin,
        aspect=aspect, **kwargs)
    if cnorm == 'log':
        im.set_norm(colors.LogNorm(vmin =im.get_clim()[0], vmax=im.get_clim()[1]))
    if colorbar:
        if cax = None:
            plt.colorbar(im, ax=ax, label = clabel)
        else:
            plt.colorbar(im, cax=cax, label = clabel)
    return im

def avg1D(x, y, range=None, bins=100, weights=None, xscale=None, yscale=None, ax=None, **kwargs):
    """
    return an array that is <y> averaged in bins of x
    """
    xvalmin = x.min() if range is None else range[0]
    xvalmax = x.max() if range is None else range[1]


    if weights is None:
        if xscale =='log' and xvalmin >0:
            hist = CalcMoments(np.log10(x), y, np.log10(xvalmin), np.log10(xvalmax), int(bins))
        else:
            hist = CalcMoments(x, y, xvalmin, xvalmax, int(bins))
    else:
        #calculate unweighed histogram
        if xscale =='log' and xvalmin >0:

            hist = CalcWeightedMoments(np.log10(x), y, weights, np.log10(xvalmin), np.log10(xvalmax), int(bins))
        else:
            hist = CalcWeightedMoments(x, y, weights, xvalmin, xvalmax, int(bins))

    if xscale =='log' and xvalmin >0:
        binEdges = np.logspace(np.log10(xvalmin), np.log10(xvalmax), int(bins)+1)
    else:
        binEdges = np.linspace(xvalmin, xvalmax, int(bins)+1)
    if ax is None:
        ax = plt.gca()
    if xscale=='log':
        ax.set_xscale('log')
    if yscale=='log':
        ax.set_yscale('log')
    # return an Line2D object like matplotlib.plot does
    return ax.plot(*stepifyMoment(binEdges, hist), **kwargs)

def avg2D(x, y, z, xrange=None, yrange=None,  bins=[200,200],
    weights=None, cnorm = '', colorbar=True, clabel='',
     ax=None, cax = None, aspect='auto', origin='lower', **kwargs):
    """
    Take the z average in x & y bin
    """
    xvalmin = x.min() if xrange is None else xrange[0]
    xvalmax = x.max() if xrange is None else xrange[1]
    yvalmin = y.min() if yrange is None else yrange[0]
    yvalmax = y.max() if yrange is None else yrange[1]

    if weights is None:
        hist = Calc2DMoments(y, x, z, yvalmin, yvalmax, int(bins[1]), xvalmin, xvalmax, int(bins[0]))
    else:
        #calculate unweighed histogram
        hist = Calc2DWeightedMoments(y, x, z, weights, yvalmin, yvalmax, int(bins[1]), xvalmin, xvalmax, int(bins[0]))

    ####
    #
    # Now we have the histogram, we need to turn it into an image
    #
    ###

    if ax is None:
        ax = plt.gca()
    im = ax.imshow(hist, extent = (xvalmin, xvalmax, yvalmin, yvalmax), origin=origin,
        aspect=aspect, **kwargs)
    if cnorm == 'log':
        im.set_norm(colors.LogNorm(vmin =im.get_clim()[0], vmax=im.get_clim()[1]))
    if colorbar:
        if cax = None:
            plt.colorbar(im, ax=ax, label = clabel)
        else:
            plt.colorbar(im, cax=cax, label = clabel)
    return im

class PowerNorm(colors.Normalize):

    ''' Custom color Norm: This one normalizes the negative data differently
    from the positive, and extends the power norm to negative values.  The main
    idea is that it plots the power_norm of the data.  If stretch_colors is
    true, then for diverging cmaps, the entire cmap is used, otherwise it only
    uses the amount so that -b and b are the same distance from the midpoint.'''

    def __init__(self, gamma = 1.0, vmin=None, vmax=None, clip=False, div_cmap = True, midpoint = 0.0, stretch_colors = True):
        colors.Normalize.__init__(self, vmin, vmax, clip)
        self.gamma = gamma
        self.div_cmap = div_cmap
        self.midpoint = midpoint
        self.stretch_colors = stretch_colors

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        # First see if there is a sign change:
        ans = PowerNormFunc(value, gamma = self.gamma, vmin=self.vmin, vmax=self.vmax, div_cmap = self.div_cmap,  midpoint = self.midpoint, stretch_colors = self.stretch_colors)
        if type(value) == np.ma.core.MaskedArray:
            ans.mask = value.mask
        return ans

def PowerNormFunc(data, gamma = 1.0, vmin=None, vmax=None, div_cmap = True,  midpoint = 0.0, stretch_colors = True):

    ''' Helper function for the PowerNorm  The main idea is that it norms data
    using np.sign(data-midpoint)*np.abs(data-midpoint)**gamma.  If
    stretch_colors is true, then for diverging cmaps, the entire cmap is used.
    If stretch colors is false then it so that -b+midpoint and b-midpoint are
    the same distance from the midpoint in the color space.'''

    vmin -= midpoint
    vmax -= midpoint
    left_clip = 0.0
    right_clip = 1.0
    if not stretch_colors:
        if np.sign(vmin) < 0 and np.sign(vmax) > 0:
            v_absmax = max(np.abs(vmin),np.abs(vmax))
            left_clip = 0.5*(1 - np.abs(vmin)**gamma/np.abs(v_absmax)**gamma)
            right_clip = 0.5*(1 + np.abs(vmax)**gamma/np.abs(v_absmax)**gamma)

    if div_cmap == True:
        if np.sign(vmin) != np.sign(vmax) and np.sign(vmin) != 0 and np.sign(vmax) != 0:
            x, y = [np.sign(vmin)*np.abs(vmin)**gamma,
                    0,
                    np.sign(vmax)*np.abs(vmax)**gamma],[left_clip, 0.5, right_clip]
        elif  np.sign(vmin) >= 0:
            # The data must be totally positive, extrapolate from midpoint
            x, y = [np.sign(vmin)*np.abs(vmin)**gamma, np.sign(vmax)*np.abs(vmax)**gamma], [0.5, right_clip]
        elif  np.sign(vmax) <= 0:
            # The data must be totally negative
            x, y = [np.sign(vmin)*np.abs(vmin)**gamma, np.sign(vmax)*np.abs(vmax)**gamma], [left_clip, 0.5]
    else:
        x, y = [np.sign(vmin)*np.abs(vmin)**gamma, np.sign(vmax)*np.abs(vmax)**gamma], [0, 1]
    if np.abs(midpoint)<=1E-8 and np.abs(gamma-1.0)<=1E-8:
        ans = np.ma.masked_array(np.interp(data, x, y))
    elif np.abs(gamma-1.0)<=1E-8:
        ans = np.ma.masked_array(np.interp(data-midpoint, x, y))
    else:
        ans = np.ma.masked_array(np.interp(np.sign(data-midpoint)*np.abs(data-midpoint)**gamma, x, y))
    return ans


def tristanSpect(o, species='lec', spectType = 'Energy', normed = False, restSpect = False, xLeft = -10000, xRight=+100000, ax = None, **kwargs):
    c_omp = o.c_omp
    istep = o.istep
    xsl = o.xsl/c_omp
    gamma = o.gamma
    #massRatio = o.mi/o.me
    momentum=np.sqrt((gamma+1)**2-1.)
    spectKey = 'spec'
    if species == 'lec':
        spectKey += 'e'
    else:
        spectKey += 'p'
    if restSpect:
        spectKey += 'rest'
    spec = np.copy(getattr(o, spectKey))

    for i in range(len(xsl)):
        spec[:,i] *= gamma

    ###############################
    ###### energy spectra, f=(dN/dE)/N
    ###############################
    dgamma = np.empty(len(gamma))
    delta=np.log10(gamma[-1]/gamma[0])/len(gamma)
    for i in range(len(dgamma)):
        dgamma[i]=gamma[i]*(10**delta-1.)

    indLeft = xsl.searchsorted(xLeft)
    indRight = xsl.searchsorted(xRight, side='right')

    if indLeft >= indRight:
        indLeft = indRight
        indRight += 1


    # energy distribution, f(E)=(dn/dE)/N
    fE=np.empty(len(gamma))
    norm = np.ones(len(xsl))


    # total particles in each linear x bin
    for i in range(len(norm)):
        norm[i]=sum(spec[:,i])

    for k in range(len(fE)):
        fE[k]=sum(spec[k][indLeft:indRight])

    if sum(norm[indLeft:indRight]) > 0:
        if normed:
            fE *= 1.0/sum(norm[indLeft:indRight])

        eDist=np.copy(fE)
        fE *= dgamma**(-1)
        fmom=fE/(4*np.pi*momentum)/(gamma+1)
        momDist=fmom*momentum**4

        if ax is None:
            ax = plt.gca()
        ax.set_yscale('log')
        ax.set_xscale('log')
        if spectType != 'Energy':
            return ax.plot(momentum, momDist, **kwargs)

        else:
            return ax.plot(gamma, eDist, **kwargs)


if __name__=='__main__':
    from tristanSim import TristanSim
    mySim = TristanSim('../Iseult/output')

    xmin = min(mySim[0].gammae.min(),mySim[0].gammai.min())
    xmax = max(mySim[0].gammae.max(),mySim[0].gammai.max())
    hist1D(mySim[0].gammae-1, range=(xmin,xmax), bins=200, xscale='log', yscale='log', c='r', label ='lecs')
    hist1D(mySim[0].gammai-1, range=(xmin,xmax), bins=200, xscale='log', yscale='log', c='b', label ='ions')
    plt.xlabel('$\gamma-1$')
    plt.ylabel('$EdN/dE$')
    plt.legend()
    plt.show()


    hist2D(mySim[0].xi, mySim[0].gammai-1, clabel='$f_i(p)$')
    plt.xlabel('$x_i$')
    plt.ylabel('$KE_i$')
    plt.show()

    avg1D(mySim[0].xi, mySim[0].gammai-1)
    plt.xlabel('$x_i$')
    plt.ylabel(r'$\langle \gamma_i-1 \rangle$')
    plt.show()

    avg2D(mySim[0].xe, mySim[0].ye, mySim[0].gammae-1, cnorm = 'log', bins = [100,50], clabel=r'$\langle KE \rangle$')
    plt.xlabel('$x_e$')
    plt.ylabel('$y_e$')
    plt.show()

    tristanSpect(mySim[1])
    plt.show()
