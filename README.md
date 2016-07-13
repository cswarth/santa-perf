# Santa performance measures

[Wercker Application]: https://app.wercker.com/project/bykey/cc49c35fea162f30d47d1b27e10e47fb
[Wercker Build Widget]: https://app.wercker.com/status/cc49c35fea162f30d47d1b27e10e47fb/s/master "wercker status"
[SANTA Repo]: http://github.com/santa-dev/santa
[SANTA page]: http://cswarth.github.io/santa-perf/index.html

[![Wercker Build Widget]][Wercker Application]

 Scripts and graphs for exploring [SANTA][SANTA Repo] memory and runtime performance.

`SConstruct` is an `SCons` configuration file used to configure and run multiple instances of `SANTA` and collect performance measures.
The `Nestly` extension to `SCons` is used to explore the parameter space of population size and number of generations.

Once all the various SANTA runs are complete, `mkcsv.py` is used to parse the log files and statistics into a CSV file, `santa.csv`.
`plot_bokeh.py` is then used to plot the collected statistics and produce an HTNL fiel that can be viewed in your web browser.

Uses Bokeh python package to build plots for [SANTA][SANTA Repo] performance measures.
When the `santa.csv` file in this repo is changed, the [SANTA Perfomance web page][SANTA page] 
will be updated.

Click on the build badge above to see the current status of the automated wercker build.


