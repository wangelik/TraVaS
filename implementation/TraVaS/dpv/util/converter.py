# import table
import numpy as np
import warnings
from statistics import mode
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog
from dpv.util.stats import threshold_estimate


# parameter conversion
def param_transform(eps, delta=0.1):

    p = 1 - np.exp(-eps)
    k = 1/eps * np.log( (np.exp(eps)+2*delta-1) / ((np.exp(eps)+1)*delta) )
    k = int(np.ceil(k))

    # return parameters
    return p, k


# log to activity conversion
def log_to_activity(log, delim=','):

    # obtain activities from event log
    if type(log) is EventLog:
        activities = attributes_filter.get_attribute_values(log, "concept:name")
        activities = list(activities.keys())

    # obtain activities from variant log
    elif type(log) is dict:
        activities = []

        for var in log:
            activities += var.split(delim)

        activities = list(set(activities))

    # consider other log formats
    else:
        warnings.warn("[!] log type not identified.")
        activities = attributes_filter.get_attribute_values(log, "concept:name")
        activities = list(activities.keys())

    # return result
    return activities


# log to variant conversion
def log_to_variant(log, compress=True, prune=False, delim=','):

    # obtain variants
    variants = variants_filter.get_variants(log)

    # compute frequencies
    for var in variants:

        # accept full traces
        if prune is False:
            if compress is True:
                variants[var] = len(variants[var])

        # prune traces to finite length
        else:
            trace_len = len(var.split(delim))

            if trace_len <= int(prune):
                if compress is True:
                    variants[var] = len(variants[var])

            else:
                variants[var] = 'del'

    # remove pruned traces
    variants = {var: val for var, val in variants.items() if val != 'del'}

    # return result
    return variants


# downscale variant frequencies
def downscale(variants, type='all', s=1):

    # compute mode of frequencies
    div = mode(variants.values())

    # scale all frequencies by mode
    if type == 'all':
        scaled_variants = {var: round(ct/div) for var, ct in variants.items()}

    # only scale thresholded values
    elif type == 'smart':
        scaled_variants = {var: (s if ct == div else ct) for var, ct in variants.items()}

    # fall back to normal variants
    else:
        scaled_variants = variants

    # return result
    return scaled_variants


# variant log merger
def merge(logs, p, k, mask=False):

    # create set union of variants
    variant_names = {var for log in logs for var in set(log)}

    # init merged variants container
    merged_variants = dict.fromkeys(variant_names, 0)

    # construct aggregate statistics
    for var_name in variant_names:
        for log in logs:

            # estimate frequency from log
            if var_name in log:
                merged_variants[var_name] += log[var_name]

            # estimate frequency from threshold
            else:
                merged_variants[var_name] += threshold_estimate(p, k)

    # compute mean estimates
    merged_variants = {var: round(val/len(logs)) for var, val in merged_variants.items()}

    # return result
    return merged_variants


# variant log intersection remover
def remove_intersect(log_a, log_b, mode='absolute'):

    # copy input logs for editing
    log_l = log_a.copy()
    log_r = log_b.copy()

    # normalize variant numbers
    if mode == 'freq':
        norm_l = sum(log_l.values())
        norm_r = sum(log_r.values())
        log_l = {key: val/norm_l for key, val in log_l.items()}
        log_r = {key: val/norm_r for key, val in log_r.items()}

    # visit all variants of intersection
    for var in set(log_a) & set(log_b):

        # subtract intersection
        common_val = min(log_l[var], log_r[var])
        log_l[var] -= common_val
        log_r[var] -= common_val

        # remove zero frequencies
        if log_l[var] == 0:
            del log_l[var]

        if log_r[var] == 0:
            del log_r[var]

    # return results
    return log_l, log_r


# trace encoder
def trace_encode(trace, mapping, delim=','):

    # extract activities from trace
    trace = trace.split(delim)
    trace_len = len(trace)

    # encode activities uniquely
    trace_enc = [enc for act in trace for key, enc in mapping.items() if act == key]
    trace_enc = ''.join(trace_enc)

    # return result
    return trace_enc, trace_len
