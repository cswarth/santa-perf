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




# install any missing packages
# http://stackoverflow.com/a/19873732/1135316
if (!suppressMessages(require("pacman"))) install.packages("pacman")
suppressPackageStartupMessages(pacman::p_load(optparse, ggplot2, ggvis, dplyr, htmltools))

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

    # find the LAST line in the log file that has the words "Time taken"
    line <- tail(lines[grepl('Time taken', lines)],1)

    # extract the numeric value fron the line.
    time.taken <- as.numeric(gsub("^.*Time taken:\\s+(\\d+).*$", "\\1", line))
    
    # split the file path to determine population and generation values
    tokens <- strsplit(file, '/')[[1]]
    generation <- as.integer(gsub('^gen(.*)$', "\\1", tokens[3]))
    population <- as.integer(gsub('^pop(.*)$', "\\1", tokens[2]))

    c(population=population, generation=generation, memory=delta, time=time.taken)
}

add_title <- function(vis, ..., properties=NULL, title = "Plot Title") 
{
    # recursively merge lists by name
    # http://stackoverflow.com/a/13811666/1135316
    merge.lists <- function(a, b) {
        a.names <- names(a)
        b.names <- names(b)
        m.names <- sort(unique(c(a.names, b.names)))
        sapply(m.names, function(i) {
                   if (is.list(a[[i]]) & is.list(b[[i]])) merge.lists(a[[i]], b[[i]])
                   else if (i %in% b.names) b[[i]]
                   else a[[i]]
               }, simplify = FALSE)
    }

    # default properties make title 'axis' invisible
    default.props <- axis_props(
        ticks = list(strokeWidth=0),
        axis = list(strokeWidth=0),
        labels = list(fontSize = 0),
        grid = list(strokeWidth=0)
        )
    # merge the default properties with user-supplied props.
    axis.props <- do.call(axis_props, merge.lists(default.props, properties))

    # don't step on existing scales.
    vis <- scale_numeric(vis, "title", domain = c(0,1), range = 'width')
    axis <- ggvis:::create_axis('x', 'title', orient = "top",  title = title, properties = axis.props, ...)
    ggvis:::append_ggvis(vis, "axes", axis)
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
    df <- data.frame(t(sapply(files, parse.santa)))  %>% mutate(id=1:nrow(.)) %>% mutate(generation=factor(generation))


    # function for displaying hover text
    hover_text <- function(x) {
        if(is.null(x)) return(NULL)
        row <- df %>% filter(id==x$id)
        text <- as.character(withTags( 
            table(class='hover',
                  tr(td("Memory:"),td(style=css(text.align="right"), paste0(row$memory, " MB"))),
                  tr(td("Population:"),td(style=css(text.align="right"), row$population)),
                  tr(td("Generations:"),td(style=css(text.align="right"), row$generation)))))
        return(text)
    }
    
    # Larger point and outline when hovering
    df %>% 
        ggvis(x = ~population, key := ~id,
              size.hover := 200, stroke := NA,
              stroke.hover := "red", strokeWidth := 3) %>%
        layer_points(y = ~memory, fill = ~generation) %>%
        add_axis("y", title = "Memory (MB)", title_offset=50, properties = axis_props(title=list(fontSize=16))) %>%
        add_axis("x", title = "Population", title_offset=40,
                 properties = axis_props(title=list(fontSize=16),
                     labels = list(fontSize = 12))) %>%
        add_title(title = "Memory Size as a function of Population",
                  properties = axis_props(title=list(fontSize=20))) %>%
        add_legend(scales=c("fill"), title="Generations") %>%
        export_svg(file = "plot.svg")
    # %>% add_tooltip(hover_text, "hover")

}



main(commandArgs(trailingOnly = TRUE))



