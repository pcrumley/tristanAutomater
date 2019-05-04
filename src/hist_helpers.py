from numba import jit
from numpy import ones, zeros
import numpy as np

def stepifyHist(bins, hist):
    tmp_bin = np.dstack((bins, bins)).flatten()
    tmp_hist = np.concatenate((np.array([0]),np.dstack((hist, hist)).flatten(), np.array([0])))
    return tmp_bin, tmp_hist

def stepifyMoment(bins, hist):
    tmp_bin = np.dstack((bins, bins)).flatten()[1:-1]
    tmp_hist = np.dstack((hist, hist)).flatten()
    return tmp_bin, tmp_hist
@jit(nopython=True)#
def FastHist(x1, min1, max1, bnum1):
    hist= zeros(bnum1)
    b1_w = ((max1-min1)/bnum1)**-1
    if len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    hist[int(j)] += 1
    return hist

@jit(nopython=True)#
def FastWeightedHist(x1, weights, min1, max1, bnum1):
    hist= zeros(bnum1)
    b1_w = ((max1-min1)/bnum1)**-1
    if (len(weights) == len(x1)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    hist[int(j)] += weights[i]
    return hist

@jit(nopython=True)#
def Fast2DHist(x1, x2, min1, max1, bnum1, min2,max2, bnum2):
    hist= zeros((bnum1, bnum2))
    b1_w = ((max1-min1)/bnum1)**-1
    b2_w =((max2-min2)/bnum2)**-1
    if (len(x1) == len(x2)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    if x2[i]>=min2:
                        if x2[i]==max2:
                            k =bnum2-1
                        else:
                            k = (x2[i]-min2)*b2_w
                        if k<bnum2:
                            hist[int(j),int(k)] += 1
    return hist
@jit(nopython=True)#
def Fast2DWeightedHist(x1, x2, weights, min1, max1, bnum1, min2,max2, bnum2):
    hist= zeros((bnum1, bnum2))
    b1_w = ((max1-min1)/bnum1)**-1
    b2_w =((max2-min2)/bnum2)**-1
    if (len(x1) == len(x2)) and (len(x1) == len(weights)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    if x2[i]>=min2:
                        if x2[i]==max2:
                            k =bnum2-1
                        else:
                            k = (x2[i]-min2)*b2_w
                        if k<bnum2:
                            hist[int(j),int(k)] += weights[i]
    return hist

@jit(nopython = True, cache = True)
def CalcMoments(x1, x2, min1, max1, bnum1):
    x2Average = zeros(bnum1)
    counts = zeros(bnum1)
    b1_w = bnum1/(max1 - min1)
    if (len(x2) == len(x1)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1 - 1
                else:
                    j = (x1[i] - min1) * b1_w
                if j<bnum1:
                    counts[int(j)] += 1
                    x2Average[int(j)] += x2[i]

    counts[counts==0] = np.nan
    return x2Average/counts

@jit(nopython=True)#
def CalcWeightedMoment(x1, x2, weights, min1, max1, bnum1):
    x2Average = zeros(bnum1)
    counts = zeros(bnum1)
    b1_w = bnum1/(max1 - min1)
    if (len(x2) == len(x1)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1 - 1
                else:
                    j = (x1[i] - min1) * b1_w
                if j<bnum1:
                    counts[int(j)] += weights[i]
                    x2Average[int(j)] += x2[i]
    counts[counts==0] = np.nan
    return x2Average/counts

@jit(nopython=True)#
def Calc2DMoments(x1, x2, x3, min1, max1, bnum1, min2,max2, bnum2):
    counts= zeros((bnum1, bnum2))
    x3Average = zeros((bnum1, bnum2))
    b1_w = ((max1-min1)/bnum1)**-1
    b2_w =((max2-min2)/bnum2)**-1
    if (len(x1) == len(x2)) and (len(x2) == len(x3)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    if x2[i]>=min2:
                        if x2[i]==max2:
                            k =bnum2-1
                        else:
                            k = (x2[i]-min2)*b2_w
                        if k<bnum2:
                            counts[int(j),int(k)] += 1.0
                            x3Average[int(j),int(k)] += x3[i]
    #counts[counts==0] = 1
    for i in range(bnum1):
        for j in range(bnum2):
            if counts[int(i),int(j)]==0:
                counts[int(i),int(j)] = np.nan  
    return x3Average/counts

@jit(nopython=True)#
def Calc2DWeightedMoments(x1, x2, x3, weights, min1, max1, bnum1, min2,max2, bnum2):
    counts= zeros((bnum1, bnum2))
    x3Average = zeros((bnum1, bnum2))
    b1_w = ((max1-min1)/bnum1)**-1
    b2_w =((max2-min2)/bnum2)**-1
    if (len(x1) ==len(x2)) and (len(x1) ==len(weights)) and (len(x1) ==len(x3)) and len(x1)>0:
        for i in range(len(x1)):
            if x1[i]>=min1:
                if x1[i] == max1:
                    j = bnum1-1
                else:
                    j = (x1[i]-min1)*b1_w
                if j<bnum1:
                    if x2[i]>=min2:
                        if x2[i]==max2:
                            k =bnum2-1
                        else:
                            k = (x2[i]-min2)*b2_w
                        if k<bnum2:
                            x3Average[int(j),int(k)] += x3[i]
                            counts[int(j),int(k)] += weights[i]
    for i in range(bnum1):
        for j in range(bnum2):
            if counts[int(i),int(j)]==0:
                counts[int(i),int(j)] = np.nan
    return x3Average/counts
