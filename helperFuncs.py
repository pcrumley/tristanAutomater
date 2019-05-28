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
     ax=None, mask_empty=True, aspect='auto', origin='lower', **kwargs):
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
        plt.colorbar(im, ax=ax, label = clabel)
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
     ax=None, aspect='auto', origin='lower', **kwargs):
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
        plt.colorbar(im, ax=ax, label = clabel)
    return im

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
