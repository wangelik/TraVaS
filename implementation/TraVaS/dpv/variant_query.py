# import table
import numpy as np
import warnings
from diffprivlib.mechanisms import Laplace, LaplaceTruncated
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog
from dpv.util.converter import log_to_activity


# DP variant bruteforcer
def variant_query(log, eps, cutoff=3, prune=5, delta=0, bound=False):

    # check log type and obtain variants
    if type(log) is EventLog:
        variants = variants_filter.get_variants(log)

    elif type(log) is dict:
        variants = log

    else:
        warnings.warn("[!] log type not identified.")
        variants = log

    # obtain activities
    activities = log_to_activity(log)

    # init containers
    trace_list = dict()
    prefixes = activities
    pref_tmp = []

    # variant length iterations
    for i in range(cutoff):

        # loop through prefixes of len i+1 (exploiting disjoint sets)
        for pref in prefixes:

            # init
            pref_ct = 0
            n = 0

            # generate noise
            if delta == 0:
                ct = round(np.random.laplace(loc=0, scale=1./eps))
                pref_noise = round(np.random.laplace(loc=0, scale=1./eps))

            # for delta > 0 and no bounds
            elif delta > 0 and bound is False:
                mech = Laplace(epsilon=eps, delta=delta, sensitivity=1)
                ct = round(mech.randomise(0))
                pref_noise = round(mech.randomise(0))

            # for delta > 0 and bound information
            else:
                mech = LaplaceTruncated(epsilon=eps, delta=delta, sensitivity=1, lower=0, upper=bound)
                ct = round(mech.randomise(0))
                pref_noise = round(mech.randomise(0))

            # check all variants in log
            for var in variants:

                # extract trace frequency
                if type(variants[var]) is list:
                    var_freq = len(variants[var])
                else:
                    var_freq = int(variants[var])

                # exact trace match
                if var == pref:
                    n = var_freq
                    ct = ct + n

                # prefix found
                if var.startswith(pref):
                    pref_ct += var_freq

            # prune final traces
            if ct > prune:
                trace_list[pref] = ct

            # prune prefix tree
            pref_ct = pref_ct - n + pref_noise

            if pref_ct > prune:
                pref_tmp.append(pref)

        # rebuild prefix tree
        if i < cutoff-1:

            prefixes = []

            for filt in pref_tmp:
                for act in activities:
                    prefixes.append(filt+','+act)

            pref_tmp = []

    # clean single events
    trace_list = {key: trace_list[key] for key in trace_list if ',' in key}

    # return result
    return trace_list
