#!/usr/bin/env python

from __future__ import print_function
import numpy as np
import pandas as pd
import glob
from cStringIO import StringIO
import re
import collections

import seaborn as sns
import matplotlib.pyplot as plt

# avoid connecting to X server
# http://stackoverflow.com/a/2766194/1135316
import matplotlib
matplotlib.use('Agg')

# Create plots of sample counts and add them to the zip file.
def make_plot(results, plate):
    def logratio(x):
        m = x.reads.mean()
        d = x.reads/m
        return np.sign(d)*np.log2(np.abs(d))

    s = StringIO()
    clean = plate['all_zones']['clean']
    if 'samples' not in clean:
        return ''

    samples = sorted(clean['samples']['counts'].iteritems())
    df = pd.DataFrame(samples, columns=['sample', 'reads'])

    tmp = (df.join(df['sample'].str.extract('p(?P<plateno>\d+)(?P<direction>d\d+)bc(?P<barcode>\d+)', expand=False))
       .assign(direction=lambda x: ["forward" if d == "d1" else "reverse" for d in x.direction])
       .assign(label=lambda x: ["bc {}".format(bc) for bc in x.barcode])
       .assign(fc=logratio)
       .assign(x=lambda x: np.arange(x.shape[0])))
    sns.set_style("whitegrid")

    g = sns.FacetGrid(tmp, hue="direction",  size=6, aspect=1.5)
    g.map(plt.scatter, "x", "fc", s=30, alpha=.6)
    g.set_axis_labels('', 'Fold change (compared to mean)')

    axis = g.axes[0][0]
    axis.get_xaxis().set_visible(False)
    labels = tmp.query("fc > 2 | fc < -2")
    for i, row in labels.iterrows():
        axis.annotate(row.label, (row.x, row.fc), 
                      xytext=(row.x+3.2, row.fc), fontsize=12)
    plt.savefig(s)
    return s.getvalue()


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

def make_plot(df):
    sns.set_style("whitegrid")
    g = sns.FacetGrid(df, hue="generation",  size=6, aspect=1.5)
    g.map(plt.scatter, "population", "memory", s=30, alpha=.6)
    g.set_axis_labels('Population', 'Memory Size (MB)')

    s = StringIO()
    plt.savefig(s)
    return(s.getvalue())

def main():
    files = glob.glob('output/*/*/santa.out')
    df = pd.DataFrame.from_records(map(parse_santa, files), columns=Record._fields)
    
    with open('plot_output.png', 'w') as fp:
            s = make_plot(df)
            fp.write(s)

if __name__ == '__main__':
    main()

            


