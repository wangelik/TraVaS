# import table
import numpy as np
from diffprivlib.tools import count_nonzero as priv_count
from diffprivlib.mechanisms import Laplace, LaplaceTruncated
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.variants import variants_filter
from dpv.util.stats import rTSGD


# dfr extractor
def dfr_extract(log, priv=False, k=False, p=False):

    # retrieve activity names
    activities = attributes_filter.get_attribute_values(log, "concept:name")

    # prepare dfr database
    dfr = dict()
    for act_pre in activities.keys():

        # insert start and stop flags
        dfr['start,'+act_pre] = 0
        dfr[act_pre+',end'] = 0

        for act_post in activities.keys():
            dfr[act_pre+','+act_post] = 0

    # obtain trace variants
    variants = variants_filter.get_variants(log)

    # generate noise
    if priv is True:
        noise = rTSGD(len(variants), p, k)

    # fill dfr database from traces
    for idx, (var, l) in enumerate(zip(variants.keys(), variants.values())):

        # compute trace multiplier
        if priv is True:
            mul = int(len(l) + noise[idx])
            if mul <= k:
                continue

        else:
            mul = len(l)

        # obtain trace activities
        arr = var.split(',')
        for i, act in enumerate(arr):

            # activity is start
            if i == 0:
                dfr['start,'+act] += mul

            # activity is end
            elif i == len(arr)-1:
                dfr[arr[i-1]+','+act] += mul
                dfr[act+',end'] += mul

            # activity is between
            else:
                dfr[arr[i-1]+','+act] += mul

    # return result
    return dfr


# dfr private query engine
def dfr_query(dfr_orig, eps, delta=0, bound=False):

    # init dfr databases
    dfr_arr = np.array([])
    dfr_priv = dfr_orig.copy()

    # construct full dfr database (exploiting disjoint sets)
    for dfr_key in dfr_orig:

        # for delta == 0
        if delta == 0:

            # prepare query storage
            if dfr_orig[dfr_key] > 0:
                dfr_arr = np.append(dfr_arr, np.repeat(dfr_key, dfr_orig[dfr_key]))

            # run private queries
            ct = priv_count(dfr_arr == dfr_key, epsilon=eps)

        # for delta > 0 and no bounds
        elif delta > 0 and bound is False:
            mech = Laplace(epsilon=eps, delta=delta, sensitivity=1)
            ct = round(mech.randomise(dfr_orig[dfr_key]))

        # for delta > 0 and bound information
        else:
            mech = LaplaceTruncated(epsilon=eps, delta=delta, sensitivity=1, lower=0, upper=bound)
            ct = round(mech.randomise(dfr_orig[dfr_key]))

        # save count
        dfr_priv[dfr_key] = ct

    # return result
    return dfr_priv


# dfr sensitivities
def dfr_sensitivity(log):

    # obtain trace variants
    variants = variants_filter.get_variants(log)

    # compute sequence length
    act = []
    for var in variants:
        act.append(len(var.split(',')))

    # return result
    return np.mean(act), max(act)
