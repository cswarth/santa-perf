#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import re
import sys
import collections
import argparse
import pandas as pd
import time as _time
import datetime


Record = collections.namedtuple('Record', 'population length memory time')

def parse_results(file, verbose=False):
    memory = parse_memory(file)
    etime = parse_time(os.path.join(os.path.dirname(file), 'time.txt'))

    # split the file path to determine population and length values
    tokens = file.split('/')
    m = re.match(r'^.*pop(\d+).*/len(\d+).*$', file)
    population = int(m.group(1))
    len = int(m.group(2))

    return Record(population, len, memory, etime)


def parse_memory(file, verbose=False):
    memory = None
    try:
        with open(file,'r') as fh:
            for line in fh:
                m = re.match(r'^Memory used\s+=\s+(\d+[.\d+]?)\s+(.*)$', line)
                m = re.match(r'^Memory used\s+=\s+(\d+(\.\d+)?)\s+(.*)', line)
                if m:
                    memory = float(m.group(1))
                    units = m.group(3)
                    multiple = {
                        'MiB':1024*1024,
                        'KB': 1024,
                        'B': 1}[units]
                    memory = int(memory * multiple)
                    break
    except IOError:
        pass
    return memory
    
def parse_time(file):
    """
    parse the output of `time --verbose` to extract the elapsed wall clock time.
    """        
    # Command being timed: "java -mx512m -Djava.util.logging.config.file=logging.properties -jar /shared/silo_researcher/Matsen_F/MatsenGrp/working/cwarth/santa-wercker/dist/santa.jar -population=1000 -samplesize=10 -generations=10000 -seed=1465407525161 santa_config.xml"
    # User time (seconds): 63.32
    # System time (seconds): 0.71
    # Percent of CPU this job got: 248%
    # Elapsed (wall clock) time (h:mm:ss or m:ss): 0:25.80
    # Average shared text size (kbytes): 0
    # Average unshared data size (kbytes): 0
    # Average stack size (kbytes): 0
    # Average total size (kbytes): 0
    # Maximum resident set size (kbytes): 130164
    # Average resident set size (kbytes): 0
    # Major (requiring I/O) page faults: 0
    # Minor (reclaiming a frame) page faults: 100269
    # Voluntary context switches: 23123
    # Involuntary context switches: 10442
    # Swaps: 0
    # File system inputs: 0
    # File system outputs: 544
    # Socket messages sent: 0
    # Socket messages received: 0
    # Signals delivered: 0
    # Page size (bytes): 4096
    # Exit status: 0

    elapsed = None
    try:
        with open(file,'r') as fh:
            for line in fh:
                m = re.match(r'^.*wall\s+clock.*:\s+(.*)', line)
                if m:
                    # save elapsed time as string formatted seconds
                    # note: don't parse with `time` package, as
                    # time-tuples don't carry microseconds and won't
                    # understand '%f' formatting.  Use datetime package instead.
                
                    elapsed = datetime.datetime.strptime(m.group(1), '%M:%S.%f')
                    elapsed = elapsed.strftime('%S.%f')
                    break
    except IOError:
        pass

    return elapsed


def main():
    '''
    Parse a generic template and insert sequences from a FASTA file into the middle,
    separated by the appropriate XML tags.
    '''
    def existing_file(fname):
        """
        Argparse type for an existing file
        """
        if not os.path.isfile(fname):
            raise ValueError("Invalid file: " + str(fname))
        return fname

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-o', '--output', default=None,
                            help='name of output graph file')
    parser.add_argument('-v', '--verbose', default=None,
                            help='verbose output')
    parser.add_argument('results', nargs='+', help='result files', type=existing_file)
    a = parser.parse_args()

    records = [parse_results(r, a.verbose) for r in a.results]
    df = pd.DataFrame.from_records(records, columns=records[0]._fields)
    if a.output is not None:
        df.to_csv(a.output, index=False)
    if a.verbose or a.output is None:
        print(df)

if __name__ == '__main__':
    main()

