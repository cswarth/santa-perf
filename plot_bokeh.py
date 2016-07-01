#!/usr/bin/env python

from __future__ import print_function
from jinja2 import Template

from bokeh.embed import components
from bokeh.models import Range1d
from bokeh.resources import INLINE
from bokeh.util.browser import view

import numpy as np
import pandas as pd
import glob
from cStringIO import StringIO
import re
import collections

from bokeh.plotting import figure, ColumnDataSource, show, save
from bokeh.models import HoverTool
from bokeh.models import NumeralTickFormatter



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


def scatter_with_hover(df, x, y,
                       fig=None, cols=None, name=None, marker='x',
                       fig_width=500, fig_height=500, **kwargs):
    """
    Plots an interactive scatter plot of `x` vs `y` using bokeh, with automatic
    tooltips showing columns from `df`.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the data to be plotted
    x : str
        Name of the column to use for the x-axis values
    y : str
        Name of the column to use for the y-axis values
    fig : bokeh.plotting.Figure, optional
        Figure on which to plot (if not given then a new figure will be created)
    cols : list of str
        Columns to show in the hover tooltip (default is to show all)
    name : str
        Bokeh series name to give to the scattered data
    marker : str
        Name of marker to use for scatter plot
    **kwargs
        Any further arguments to be passed to fig.scatter

    Returns
    -------
    bokeh.plotting.Figure
        Figure (the same as given, or the newly created figure)

    Example
    -------
    fig = scatter_with_hover(df, 'A', 'B')
    show(fig)

    fig = scatter_with_hover(df, 'A', 'B', cols=['C', 'D', 'E'], marker='x', color='red')
    show(fig)

    Author
    ------
    Robin Wilson <robin@rtwilson.com>
    with thanks to Max Albert for original code example
    """

    # If we haven't been given a Figure obj then create it with default
    # size etc.
    if fig is None:
        fig = figure(width=fig_width, height=fig_height, tools=['box_zoom', 'reset'])

    # We're getting data from the given dataframe
    source = ColumnDataSource(data=df)

    # We need a name so that we can restrict hover tools to just this
    # particular 'series' on the plot. You can specify it (in case it
    # needs to be something specific for other reasons), otherwise
    # we just use 'main'
    if name is None:
        name = 'main'

    # Actually do the scatter plot - the easy bit
    # (other keyword arguments will be passed to this function)
    fig.scatter(df[x], df[y], source=source, name=name, marker=marker, **kwargs)

    # Now we create the hover tool, and make sure it is only active with
    # the series we plotted in the previous line
    hover = HoverTool(names=[name])

    if cols is None:
        # Display *all* columns in the tooltips
        hover.tooltips = [(c, '@' + c) for c in df.columns]
    else:
        # Display just the given columns in the tooltips
        hover.tooltips = [(c, '@' + c) for c in cols]

    hover.tooltips.append(('index', '$index'))

    # Finally add/enable the tool
    fig.add_tools(hover)

    return fig


def plot_lines(df, fig, x, y, group):
    tmp = df.pivot(index=x, columns=group, values=y)
    numlines=len(tmp.columns)
    mypalette=Spectral11[0:numlines]
    ts_list_of_list = []
    for i in range(0,len(tmp.columns)):
        ts_list_of_list.append(tmp.index.T)
        
    vals_list_of_list = tmp.values.T.tolist()

    fig.multi_line(ts_list_of_list, vals_list_of_list, line_width=4, line_color=mypalette)




    
import sys
from bokeh.palettes import Spectral11


def main():
    files = glob.glob('output/*/*/santa.out')
    df = pd.DataFrame.from_records(map(parse_santa, files), columns=Record._fields)

    print(df.head())
    print(df.pivot(index='population', columns='generation', values='memory').head())

    
    plots = list()

    fig = figure(title="Population vs. Memory", width=1000, height=500, tools=['box_zoom', 'reset'])
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'population', "memory", 'generation')

    fig = scatter_with_hover(df, "population", "memory", fig, marker='o', size=8, fill_color="blue")
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Population"

    fig.yaxis.axis_label = "Memory (MB)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    plots.append(fig)
    
    fig = figure(title="Generations vs. Memory", width=1000, height=500, tools=['box_zoom', 'reset'])
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'generation', "memory", 'population')

    fig = scatter_with_hover(df, "generation", "memory", fig, marker='o', fig_width=1000, size=8, fill_color="blue")
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Generations"
    fig.yaxis.axis_label = "Memory (MB)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    plots.append(fig)

    fig = figure(title="Population vs. Time", width=1000, height=500, tools=['box_zoom', 'reset'])
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'population', "time", 'generation')

    fig = scatter_with_hover(df, "population", "time", fig, marker='o', fig_width=1000, size=8, fill_color="blue")
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.yaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Population"
    fig.yaxis.axis_label = "Time (ms)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    plots.append(fig)
    
    fig = figure(title="Generations vs. Time", width=1000, height=500, tools=['box_zoom', 'reset'])
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'generation', "time", 'population')
    fig = scatter_with_hover(df, "generation", "time", fig, marker='o', fig_width=1000, size=8, fill_color="blue")
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.yaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Generation"
    fig.yaxis.axis_label = "Time (ms)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    plots.append(fig)


    script, div = components(plots)
    
    template = Template('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Bokeh Scatter Plots</title>
{{ js_resources }}
{{ css_resources }}
{{ script }}
<style>
.embed-wrapper {
width: 50%;
height: 600px;
margin: auto;
}
</style>
</head>
<body>
{% for item in div %}
<div class="embed-wrapper">
{{ item }}
</div>
{% endfor %}
</body>
</html>
''')

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    filename = 'index.html'

    html = template.render(js_resources=js_resources,
                               css_resources=css_resources,
                               script=script,
                               div=div)

    with open(filename, 'w') as f:
        f.write(html.encode('utf-8'))
    view(filename)


    
if __name__ == '__main__':
    main()

            


