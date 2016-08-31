#!/usr/bin/xvfb-run Rscript 

# script to make plots from data in `results.csv`.
#
# usage:
#     $ scons
#     $ bin/parseresults.py -o results.csv $(find output -type f -name santa.out) >results.csv
#     $ plot_results.r
#
# Once the simulations have been run (scons) and the results have been aggregated (parseresults.py),
# tis routine can be called multiple times to remake or tweak the plots.
#
# Plot images in `bypopulation.png` and `byseqlen.png`
#
# note the funky shebang usage above.  `xvfb-run` sets up a virtual
# X11 framebuffer.  This allows us to run plotting packages in R like
# `ggplot` that would otherwise fail for lack of a working X11 server.
#

suppressWarnings(library(readr))
suppressMessages(library(dplyr))
suppressWarnings(library(ggplot2))


df <- read_csv('results.csv')
df <- df %>% filter(complete.cases(.)) %>% mutate(population=factor(population)) %>% mutate(length=factor(length))
ggplot(df, aes(x=length, y=time, color=population, group=population)) + 
  theme_bw() + 
  labs(title='Run time as function of sequence length') +
  xlab('Sequence length (nt)') +
  ylab('Run time (sec)') +
  geom_line(aes(color=population), size=1) + 
  geom_point(aes(color=population),size=1.1) +
  labs(color = "Population size")
ggsave(filename='bypopulation.png', width=8, height=5, units='in')

ggplot(df, aes(x=population, y=time, color=length, group=length)) + 
  theme_bw() + 
  labs(title='Runtime as function of population size') +
  xlab('Population size') +
  ylab('Runtime (sec)') +
  geom_line(aes(color=length), size=1) + 
  geom_point(aes(color=length),size=1.1) +
  labs(color = "Sequence len")
ggsave(filename='byseqlen.png', width=8, height=5, units='in')



