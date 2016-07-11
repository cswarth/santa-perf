#!/usr/bin/env python
# to deploy to gh-pages, use the function `gh=deploy` defined in ~.bash_profile
# first copy index.html tp the `site/` directory
# Cribbed from https://gist.github.com/cobyism/4730490
#    git subtree push --prefix site origin gh-pages

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

from bokeh.plotting import figure, ColumnDataSource, show, save
from bokeh.models import HoverTool
from bokeh.models import NumeralTickFormatter


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



def plot_lines(df, fig, x, y, group):
    legends = []
    groups = df.groupby(by=[group])
    numlines = len(groups)
    colors=Spectral11[0:numlines]
    for i, (key, grp) in enumerate(groups):
        grp = grp.sort_values(by=x,axis=0)
        name = str(key)
        source = ColumnDataSource(data=grp)
        line = fig.line(x, y,  source=source, line_width=4, line_color=colors[i])
        point = fig.circle(x, y,  source=source, name=name, size=8, fill_color=colors[i])
        legends.append((name, [line]))

        hover = HoverTool(names=[name])
        hover.tooltips = [(c, '@' + c) for c in grp.columns]
        hover.tooltips.append(('index', '$index'))
        fig.add_tools(hover)

    # place a legend outside the plot area
    # http://bokeh.pydata.org/en/dev/docs/user_guide/styling.html#outside-the-plot-area
    legend = Legend(legends=legends, location=(0, -30), name="foppo")

    fig.add_layout(legend, 'right')


    return fig
        
     
import sys
from bokeh.palettes import Spectral11


def main():
    files = glob.glob('output/*/*/santa.out')
    df = pd.DataFrame.from_records(map(parse_santa, files), columns=Record._fields)

    plots = list()

    fig = figure(title="Population vs. Memory", width=1000, height=500, tools=['box_zoom', 'reset'], toolbar_location="above")
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'population', "memory", 'generation')
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Population"
    fig.yaxis.axis_label = "Memory (MB)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    fig.xaxis.formatter = NumeralTickFormatter(format="0,0")

    plots.append(fig)
    
    
    fig = figure(title="Generations vs. Memory", width=1000, height=500, tools=['box_zoom', 'reset'], toolbar_location="above")
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'generation', "memory", 'population')
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Generations"
    fig.yaxis.axis_label = "Memory (MB)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    fig.xaxis.formatter = NumeralTickFormatter(format="0,0")

    plots.append(fig)

    fig = figure(title="Population vs. Time", width=1000, height=500, tools=['box_zoom', 'reset'], toolbar_location="above")
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'population', "time", 'generation')
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.yaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Population"
    fig.yaxis.axis_label = "Time (ms)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    fig.xaxis.formatter = NumeralTickFormatter(format="0,0")
    fig.yaxis.formatter = NumeralTickFormatter(format="0,0")

    plots.append(fig)
    
    fig = figure(title="Generations vs. Time", width=1000, height=500, tools=['box_zoom', 'reset'], toolbar_location="above")
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'generation', "time", 'population')
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.yaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Generation"
    fig.yaxis.axis_label = "Time (ms)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    fig.xaxis.formatter = NumeralTickFormatter(format="0,0")
    fig.yaxis.formatter = NumeralTickFormatter(format="0,0")
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

    # to deploy to gh-pages, use the function `gh=deploy` defined in ~.bash_profile
    # first copy index.html tp the `site/` directory
    # Cribbed from https://gist.github.com/cobyism/4730490
    #    git subtree push --prefix site origin gh-pages

    view(filename)


    
if __name__ == '__main__':
    main()

            


