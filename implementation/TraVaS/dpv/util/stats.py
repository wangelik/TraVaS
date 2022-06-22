# import table
import numpy as np
from numba import jit


# k-TSGD distribution
@jit(nopython=True)
def pTSGD(x, p, k):

    # k needs to be from Z
    assert k % 1 == 0

    # valid contributions
    if(np.abs(x) <= k and x % 1 == 0):
        c = p / (1+(1-p)-2*(1-p)**(k+1))
        prob = c*(1-p)**np.abs(x)
        return prob

    # truncated values are zero
    else:
        return 0


# k-TSGD random sampling function
@jit(nopython=True)
def rTSGD(n, p, k):

    # n needs to be int
    n = int(n)
    sample = np.zeros(n)

    # generate i.i.d uniform samples
    uni = np.empty(n)
    for idx in np.ndindex(n):
        uni[idx] = np.random.uniform(0, 1)

    # compute CDF function
    x = np.arange(-k, k+1, 1)
    prob = np.zeros(len(x))

    for i, j in enumerate(x):
        prob[i] = pTSGD(j, p, k)

    cdf = np.cumsum(prob)

    # sample by inverse CDF intervals
    for i, j in enumerate(uni):
        idx = np.argmax(j <= cdf)
        sample[i] = x[idx]

    # return sample
    return sample


# threshold probability estimator
@jit(nopython=True)
def threshold_estimate(p, k):

    # obtain true frequency options
    freq = np.arange(1, 2*k+1)

    # init probabilities
    prob = np.zeros(2*k)

    # consider all frequencies for cutoff
    for f in freq:
        for num in np.arange(-k, k+1)[:-f]:

            # add density
            prob[f-1] += pTSGD(num, p, k)

    # norm final probabilities
    prob = prob/np.sum(prob)

    # return result
    return np.sum(prob*freq)
