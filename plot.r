#!/usr/bin/env Rscript

# Aggregate individual distance files into one distance file.
#
# This script expects to be invoked with a bunch of paths to individual
# CSV files.
#
# e.g. aggregate_distance.r runs/300/100/500/relaxed/distance.csv runs/500/300/1500/relaxed/distance.csv
#
# except that one should expect dozens of filenames on the
# commandline.
#
# The directory paths to the distance.csv files are significant!
# They must have at least 4 components in the path and each component
# has a particular interpretation.  For example, the first numeric
# component is the time since infection for patient-1, the second is
# time of transmission, and the third is time since infection for
# patient-2


suppressPackageStartupMessages(library("optparse"))
library(ggplot2)

# given a filename, parse relevant info from the file and
# return a vector of values
parse.santa <- function(file) {
    con <- file(description=file, open="r")
    lines <- readLines(con)
    close(con)

    # find the LAST line in the log file that has the words "Memory change"
    line <- tail(lines[grepl('Memory change', lines)],1)

    # extract the numeric value fron the line.
    delta <- as.numeric(gsub("^.*Memory change:\\s+(\\d+[.]?\\d+).*$", "\\1", line))

    # split the file path to determine population and generation values
    tokens <- strsplit(file, '/')[[1]]
    generation <- as.integer(gsub('^gen(.*)$', "\\1", tokens[3]))
    population <- as.integer(gsub('^pop(.*)$', "\\1", tokens[2]))

    c(population=population, generation=generation, memory=delta)
}

## find log files
## extract data
## build dataframe
## multiple regression?
main <- function(args) {
    option_list <- list()
    # get command line options, if help option encountered print help and exit,
    # otherwise if options not found on command line then set defaults,
    parser <- OptionParser(usage = "%prog [options] files [...]", option_list=option_list)

    arguments <- parse_args(parser, args=args)
    opt <- arguments$options
    # files <- arguments$args

    files = list.files("output", 'santa.out', full.names=TRUE, recursive=TRUE)

    df <- t(sapply(files, parse.santa))

    
}



main(commandArgs(trailingOnly = TRUE))
