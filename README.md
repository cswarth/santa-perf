# Santa performance measures

[Wercker Application]: https://app.wercker.com/project/bykey/cc49c35fea162f30d47d1b27e10e47fb
[Wercker Build Widget]: https://app.wercker.com/status/cc49c35fea162f30d47d1b27e10e47fb/s/master "wercker status"
[SANTA Repo]: http://github.com/santa-dev/santa
[SANTA page]: http://cswarth.github.io/santa-perf/index.html

[![Wercker Build Widget]][Wercker Application]

![Grouped by population size](figures/bypopulation.svg =800x500)
![Grouped by sequence length](figures/byseqlen.svg =800x500)

## Basic usage


To gather statistics and build plots that explore [SANTA][SANTA Repo] memory and runtime performance,
```
	$ scons -j 10
	$ bin/parseresults.py -o results.csv $(find output -type f -name santa.out) >results.csv
	$ plot_results.r
```
Running the simulations under various combinations of population size and sequence length will take several hours to complete.
Two optimizations are included to hopefully make this process faster.  The SConstrct file uses the SLURM command srun to launch jobs on the Hutch center cluster resources.  Also, because the heavy lifting is offloaded to
Since the haevy 

This will leave plot images in `bypopulation.png` and `byseqlen.png`

## non-portable pipeline

## basic outline

No attempt has been made to make this code portable to environments outside the Hutch.  The SConstruct file uses SLURM commands to launch jobs on the Hutch compit resources.

`SConstruct` is an `SCons` configuration file used to configure and
run multiple instances of `SANTA` and collect performance measures.
The `Nestly` package is used to explore the combinatoric parameter
space of population size and number of generations.

Once all the various SANTA runs are complete, `parseresults.py` is used to
parse the log files and statistics into a CSV file, `santa.csv`.



## web-aware plots

`plot_bokeh.py` can plot the collected statistics and
produce an HMTL file that can be viewed in your web browser.

Uses Bokeh python package to build plots for [SANTA][SANTA Repo]
performance measures.  When the `results.csv` file in this repo is
changed, the [SANTA Perfomance web page][SANTA page] will be updated.

Click on the build badge above to see the current status of the automated wercker build.


