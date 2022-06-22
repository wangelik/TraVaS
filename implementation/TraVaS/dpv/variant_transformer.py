# import table
import warnings
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog
from pm4py.util import variants_util
from dpv.util.stats import rTSGD


# noise engine for variant frequencies
def noisify(variants, noise, k):

    # init new variant containers
    traces_orig = dict()
    traces_priv = dict()

    # obtain variant names
    var_keys = list(variants.keys())

    # add iid noise to variant frequencies
    for i, var in enumerate(var_keys):

        if type(variants[var]) is list:
            ct = len(variants[var]) + noise[i]
        else:
            ct = int(variants[var]) + noise[i]

        # apply thresholding
        if ct > k:
            traces_orig[var] = (len(variants[var]) if type(variants[var]) is list else int(variants[var]))
            traces_priv[var] = int(ct)

    # return results
    return traces_orig, traces_priv


# private trace variant transformer
def private_transform(log, p, k):

    # obtain variants from event log
    if type(log) is EventLog:
        variants = variants_filter.get_variants(log)

    elif type(log) is dict:
        variants = log

    else:
        warnings.warn("[!] log type not identified.")
        variants = log

    # generate noise
    noise = rTSGD(len(variants), p, k)

    # create DP variant lists
    traces_orig, traces_priv = noisify(variants, noise, k)

    # return results
    return traces_orig, traces_priv


# public trace variant transformer
def public_transform(log):

    # init new pm4py event log
    plog = EventLog()

    # obtain variant names
    var_keys = list(log.keys())

    # rebuild raw trace log
    for var in var_keys:
        ct = int(log[var])

        # account for frequencies
        for i in range(ct):
            trace = variants_util.variant_to_trace(var, parameters=None)
            plog.append(trace)

    # return result
    return plog
