# TraVaS
This repository provides the codebase and all experimental results of the "TraVaS: Differentially Private Trace Variant Selection for Process Mining" project.
For the experiments, two event logs (BPIC2013 [4], Sepsis [5]) were anonymized by two
(&epsilon;, &delta;)-DP methods of TraVaS (TraVaS and uTraVaS), a benchmark [1], and the extension of the benchmark (SaCoFa [2]). 
The private logs have then been evaluated against two data utility metrics (relative log similarity and absolute log difference) and two result utility metrics (fitness and precision).
Due to the underlying probabilistic nature, each privacy parameter combination was executed 10 times, values are the averages of 10 runs.  
More detailed information can be found in the respective document.

## Structure
The data is structured as follows. For each event log a specific folder within `experiments` contains:
* The original XES log file
* A `run.ipynb` jupyter notebook (to recreate main data and graphics)
* A `plots.ipynb` jupyter notebook (to recreate paper and supplementary plots)
* The folders `TraVaS`, `uTraVaS`, `Benchmark`, and `SaCoFa` (for Sepsis, BPIC2013)
* PDF files as final evaluation plots (data utility and result utility)

The folders of privacy preservation techniques contain two types of files:
* variants_[*method*]\_[*epsilon*]\_[*delta*]_[*repetition*].json (privatized log)
* [*measure*]_[*method*].txt (averaged evaluation data for all (&epsilon;, &delta;) combinations)

In addition, we provide both codebases for *TraVaS* and *SaCoFa* in the `implementation` folder.  
Further explanations and supplementary results are listed within the folder `supplementary`.

## Notes
In particular, the data utility metrics can be computationally expensive to compute. Hence, we advise to ensure sufficient CPU- and memory resources.  
Any feedback is expected to arrive at `frederik.wangelik@rwth-aachen.de` or `majid.rafiei@pads.rwth-aachen.de`.

## References

[1] Mannhardt, F., Koschmider, A., Baracaldo, N. et al.: "Privacy-Preserving Process Mining." Bus. Inf. Syst. Eng. 61, 595–614 (2019).

[2] Fahrenkog-Petersen, Stephan A., et al. "SaCoFa: Semantics-aware Control-flow Anonymization for Process Mining." 2021 3rd International Conference on Process Mining (ICPM). IEEE, (2021).

[3] F. van Dongen, B.: "BPI Challenge 2012" 4TU.ResearchData. Dataset. (2012)

[4] Steeman, W.: "BPI Challenge 2013, incidents" 4TU.ResearchData. Dataset. (2013)

[5] Mannhardt F.: "Sepsis Cases - Event Log" Dataset. (2016)