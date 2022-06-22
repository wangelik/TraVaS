# import table
import numpy as np
import warnings
from Levenshtein import distance as ls_dist
from pyemd import emd
from ortools.graph import pywrapgraph as graph
from pm4py.objects.log.obj import EventLog
from dpv.util.converter import log_to_activity, log_to_variant, remove_intersect, trace_encode


# EMD log utility
def emd_utility(log_orig, variants_priv, clean=False):

    # check log type and obtain original variants
    if type(log_orig) is EventLog:
        variants_orig = log_to_variant(log_orig)

    elif type(log_orig) is dict:
        variants_orig = log_orig

    else:
        warnings.warn("[!] log type not identified.")
        variants_orig = log_orig

    # apply absolute intersection removal
    if clean == 'absolute':
        variants_orig, variants_priv = remove_intersect(variants_orig, variants_priv)
        sum_orig = sum(variants_orig.values())
        sum_priv = sum(variants_priv.values())

    # apply frequency intersection removal
    elif clean == 'freq':
        variants_orig, variants_priv = remove_intersect(variants_orig, variants_priv, mode='freq')
        sum_orig = 1
        sum_priv = 1

    # use original variants
    else:
        sum_orig = sum(variants_orig.values())
        sum_priv = sum(variants_priv.values())

    # compute variant numbers
    l_orig = len(variants_orig)
    l_priv = len(variants_priv)

    # obtain unique activities
    activities = dict.fromkeys(log_to_activity(log_orig), 0)

    # init optimization containers
    n = np.maximum(l_orig, l_priv)
    freq_orig = np.zeros(n)
    freq_priv = np.zeros(n)
    cost = np.zeros((n, n))

    # compute relative trace frequencies
    freq_orig[0:l_orig] = np.array(list(variants_orig.values()))/sum_orig
    freq_priv[0:l_priv] = np.array(list(variants_priv.values()))/sum_priv

    # define unique encoding scheme
    for idx, act in enumerate(activities):
        activities[act] = chr(idx)

    # construct cost matrix
    for i, var_orig in enumerate(variants_orig):
        for j, var_priv in enumerate(variants_priv):

            # encode traces
            trace_orig, len_orig = trace_encode(var_orig, activities)
            trace_priv, len_priv = trace_encode(var_priv, activities)

            # compute cost
            dist = ls_dist(trace_orig, trace_priv) / np.maximum(len_orig, len_priv)
            cost[i][j] = dist

    # run optimizer
    utility = 1-emd(freq_orig, freq_priv, cost)

    # return result
    return utility


# absolute log difference cost
def log_diff(log_orig, variants_priv, clean=True, penalty=10, debug=False):

    # check log type and obtain original variants
    if type(log_orig) is EventLog:
        variants_orig = log_to_variant(log_orig)

    elif type(log_orig) is dict:
        variants_orig = log_orig

    else:
        warnings.warn("[!] log type not identified.")
        variants_orig = log_orig

    # check if logs are the same
    if variants_orig == variants_priv:
        return 0

    # apply intersection removal
    if clean is True:
        variants_orig, variants_priv = remove_intersect(variants_orig, variants_priv)

    # obtain unique activities
    activities = dict.fromkeys(log_to_activity(log_orig), 0)

    # define unique encoding scheme
    for idx, act in enumerate(activities):
        activities[act] = chr(idx)

    # init counts, cost and optimizer
    n_orig = len(variants_orig)
    n_priv = len(variants_priv)
    ct_orig = sum(variants_orig.values())
    ct_priv = sum(variants_priv.values())
    ct_diff = np.abs(ct_orig-ct_priv)
    cost = np.zeros((n_orig+1, n_priv+1))
    min_cost_flow = graph.SimpleMinCostFlow()

    # construct cost matrix
    for i, var_orig in enumerate(variants_orig):
        for j, var_priv in enumerate(variants_priv):

            # encode traces
            trace_orig, len_orig = trace_encode(var_orig, activities)
            trace_priv, len_priv = trace_encode(var_priv, activities)

            # compute cost
            dist = ls_dist(trace_orig, trace_priv)
            cost[i][j] = dist

    # build network with private trashbin
    if ct_orig > ct_priv:
        sup_nodes = np.arange(n_orig)
        rec_nodes = np.arange(n_priv+1) + sup_nodes[-1] + 1
        transfer = list(variants_orig.values()) + [-x for x in variants_priv.values()] + [-ct_diff]
        capacities = np.repeat(list(variants_orig.values()), n_priv+1).reshape((-1, n_priv+1))
        cost[:, -1] = np.max(cost) + penalty

    # build network with original trashbin
    elif ct_orig < ct_priv:
        sup_nodes = np.arange(n_orig+1)
        rec_nodes = np.arange(n_priv) + sup_nodes[-1] + 1
        transfer = list(variants_orig.values()) + [ct_diff] + [-x for x in variants_priv.values()]
        capacities = np.repeat(list(variants_orig.values()) + [ct_diff], n_priv).reshape((-1, n_priv))
        cost[-1, :] = np.max(cost) + penalty

    # build plain network
    else:
        sup_nodes = np.arange(n_orig)
        rec_nodes = np.arange(n_priv) + sup_nodes[-1] + 1
        transfer = list(variants_orig.values()) + [-x for x in variants_priv.values()]
        capacities = np.repeat(list(variants_orig.values()), n_priv).reshape((-1, n_priv))

    # add all network links
    for i in np.arange(len(sup_nodes)):
        for j in np.arange(len(rec_nodes)):
            min_cost_flow.AddArcWithCapacityAndUnitCost(int(sup_nodes[i]), int(rec_nodes[j]), int(capacities[i][j]), int(cost[i][j]))

    # add supplies
    for i in np.arange(len(transfer)):
        min_cost_flow.SetNodeSupply(int(i), int(transfer[i]))

    # optimize min cost flow
    status = min_cost_flow.Solve()

    # if solution exists
    if status == min_cost_flow.OPTIMAL:

        # save min cost
        opt = min_cost_flow.OptimalCost()

        # enable debug output
        if debug is True:

            # print total cost
            print(f'[+] Total cost = {opt}')

            # print detailed solution
            for arc in range(min_cost_flow.NumArcs()):

                if min_cost_flow.Flow(arc) > 0:
                    print(f'[-] variant {min_cost_flow.Tail(arc)}'
                            f' assigned to variant {min_cost_flow.Head(arc)}'
                            f' with cost = {min_cost_flow.UnitCost(arc)}'
                            f' and frequency {min_cost_flow.Flow(arc)}')

    # if error happened
    else:
        print(f'[!] Error while solving: {status}')
        opt = -1

    # return result
    return opt
