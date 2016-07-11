#!/usr/bin/env python

from __future__ import print_function
from jinja2 import Template

from bokeh.embed import components
from bokeh.models import Range1d
from bokeh.resources import INLINE
from bokeh.util.browser import view
from bokeh.models import Legend

import numpy as np
import pandas as pd
import glob
from cStringIO import StringIO
import re
import collections


Record = collections.namedtuple('Record', 'population generation memory time')

def parse_santa(file):
    memory = 0
    with open(file,'r') as fh:
        for line in fh:
            m = re.match('^.*Memory change:\\s+(\\d+[.]?\\d+).*$', line)
            if m:
                memory = float(m.group(1))
            m = re.match("^.*Time taken:\\s+(\\d+).*$", line)
            if m:
                time = int(m.group(1))
    # split the file path to determine population and generation values
    tokens = file.split('/')
    m = re.match('^.*pop(\\d+).*/gen(\\d+).*$', file)
    population = int(m.group(1))
    generation = int(m.group(2))
    return Record(population, generation, memory, time)


def main():
    files = glob.glob('output/*/*/santa.out')
    df = pd.DataFrame.from_records(map(parse_santa, files), columns=Record._fields)

    df.to_csv('santa.csv')
    
if __name__ == '__main__':
    main()

