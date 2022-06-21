# import table
import numpy as np
import random
from opyenxes.classification.XEventNameClassifier import XEventNameClassifier
from diffprivlib.mechanisms import Laplace, LaplaceTruncated
from privatize_occured import exp_mech as exp

# general settings
TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"


# render variants DP private
def privatize_tracevariants(log, epsilon, delta, P, N):

    event_int_mapping = create_event_int_mapping(log=log)
    
    # transform log into event view and get prefix frequencies
    print("Retrieving true prefix frequencies", end='')
    known_prefix_frequencies = get_prefix_frequencies_from_log(log)
    events = list(event_int_mapping.keys())
    events.remove(TRACE_START)
    print("Done")

    final_frequencies = {}
    trace_frequencies = {"": 0}

    for n in range(1, N + 1):

        # get prefix_frequencies, using either known frequency, or frequency of parent, or 0
        trace_frequencies = get_prefix_frequencies_length_n(trace_frequencies, events, n, known_prefix_frequencies)

        # exp_mech
        trace_frequencies = privatize_trace_variants(trace_frequencies, epsilon, delta)

        # prune
        if n < N:
            trace_frequencies = prune_trace_frequencies(trace_frequencies, P)

        # add finished traces to output, remove from list, sanity checks
        new_frequencies = {}

        for entry in trace_frequencies.items():
            if TRACE_END in entry[0]:
                final_frequencies[entry[0]] = entry[1]
            elif n == N:
                final_frequencies[entry[0][:-3]] = entry[1]
            else:
                new_frequencies[entry[0]] = entry[1]

        trace_frequencies = new_frequencies

    return final_frequencies


# create event mapper (helper)
def create_event_int_mapping(log):

    classifier = XEventNameClassifier()
    event_name_list = []

    for trace in log[0]:
        for event in trace:
            event_name = classifier.get_class_identity(event)
            if not str(event_name) in event_name_list:
                event_name_list.append(event_name)

    event_int_mapping = {}
    event_int_mapping[TRACE_START] = 0
    current_int = 1

    for event_name in event_name_list:
        event_int_mapping[event_name] = current_int
        current_int = current_int + 1

    event_int_mapping[TRACE_END] = current_int

    return event_int_mapping


# obtain prefix counts (helper)
def get_prefix_frequencies_from_log(log):

    classifier = XEventNameClassifier()
    prefix_frequencies = {}

    for trace in log[0]:
        current_prefix = ""

        for event in trace:
            current_prefix = current_prefix + classifier.get_class_identity(event) + EVENT_DELIMETER

            if current_prefix in prefix_frequencies:
                frequency = prefix_frequencies[current_prefix]
                prefix_frequencies[current_prefix] += 1
            else:
                prefix_frequencies[current_prefix] = 1

        current_prefix = current_prefix + TRACE_END

        if current_prefix in prefix_frequencies:
            frequency = prefix_frequencies[current_prefix]
            prefix_frequencies[current_prefix] += 1
        else:
            prefix_frequencies[current_prefix] = 1

    return prefix_frequencies


# limit prefix counts with length constraints (helper)
def get_prefix_frequencies_length_n(trace_frequencies, events, n, known_prefix_frequencies):

    prefixes_length_n = {}

    for prefix, frequency in trace_frequencies.items():
        for new_prefix in pref(prefix, events, n):

            if new_prefix in known_prefix_frequencies:
                new_frequency = known_prefix_frequencies[new_prefix]
                prefixes_length_n[new_prefix] = new_frequency
            else:
                prefixes_length_n[new_prefix] = 0

    return prefixes_length_n


# privatize frequencies (helper)
def privatize_trace_variants(trace_frequencies, epsilon, delta):

    non_zero_set = []
    zero_set = []

    for trace_frequency in trace_frequencies.items():
        if trace_frequency[1] == 0:
            zero_set.append(trace_frequency[0])
        else:
            non_zero_set.append(trace_frequency[0])

    output_universes = np.linspace(0,len(zero_set), num=len(zero_set)+1, dtype=int)
    chosen_universe = exp.exp_mech(output_universes, epsilon)

    for x in random.sample(zero_set, chosen_universe):
        non_zero_set.append(x)
        zero_set.remove(x)

    return apply_laplace_noise_tf(trace_frequencies, non_zero_set, epsilon, delta)


# prune variants (helper)
def prune_trace_frequencies(trace_frequencies, P):

    pruned_frequencies = {}

    for entry in trace_frequencies.items():
        if entry[1] >= P or TRACE_END in entry[0]:
            pruned_frequencies[entry[0]] = entry[1]

    return pruned_frequencies


# extract prefixes from events (helper)
def pref(prefix, events, n):

    prefixes_length_n = []

    if not TRACE_END in prefix:

        for event in events:
            current_prefix = ""
            if event == TRACE_END:
                current_prefix = prefix + event
            else:
                current_prefix = prefix + event + EVENT_DELIMETER
            prefixes_length_n.append(current_prefix)

    return prefixes_length_n


# insert laplace noise (helper)
def apply_laplace_noise_tf(trace_frequencies, non_zero_set, epsilon, delta):

    for trace_frequency in non_zero_set:

        mech = Laplace(epsilon=epsilon, delta=delta, sensitivity=1)

        if trace_frequencies[trace_frequency] == 0:
            noise = 0
            while noise <= 0:
                noise = round(mech.randomise(0))
        else:
            noise = round(mech.randomise(0))

        trace_frequencies[trace_frequency] = trace_frequencies[trace_frequency] + noise

        if trace_frequencies[trace_frequency] < 0:
            trace_frequencies[trace_frequency] = 0

    return trace_frequencies
