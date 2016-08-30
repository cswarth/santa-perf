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
from datetime import timedelta


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
    """
    Extract memory statistics from SANTA output.

    Looks for lines like "Memory used = 1.6 MiB" and parses both the
    numeric value and the units (which may vary).

    Returns integer number of bytes used after accounting for
    units.
    """
    memory = None
    try:
        with open(file,'r') as fh:
            for line in fh:
                m = re.match(r'^Memory used\s+=\s+(\d+(\.\d+)?)\s+(.*)$', line)
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

    Looks for lines like "Elapsed (wall clock) time (h:mm:ss or m:ss): 0:25.80" and parses the time signature.

    Returns real value seconds.
    """        
    elapsed = None
    try:
        with open(file,'r') as fh:
            for line in fh:
                m = re.match(r'^.*wall\s+clock.*:\s+(?P<timestr>.*)', line)
                if m:
                    # note: don't parse with `time` package, as
                    # time-tuples don't carry microseconds and won't
                    # understand '%f' formatting.  Use datetime package instead.
                    d = re.match(r'((?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)(\.(?P<microseconds>\d+))?', m.group('timestr'))
                    d = dict([(k, int(v)) for (k,v) in d.groupdict().iteritems() if v])

                    # have to fixup fractional seconds into microseconds.
                    if d.get('microseconds'):
                        d['microseconds'] = (d['microseconds']/100.0)*1e6
                    elapsed = timedelta(**d).total_seconds()
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

