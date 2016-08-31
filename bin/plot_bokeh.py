#!/usr/bin/env python
# to deploy to gh-pages, use the function `gh=deploy` defined in ~.bash_profile
# first copy index.html tp the `site/` directory
# Cribbed from https://gist.github.com/cobyism/4730490
#    git subtree push --prefix site origin gh-pages

from __future__ import print_function

from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.util.browser import view
from bokeh.models import Legend
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Spectral11

import os
import sys
import getpass
import argparse
import datetime
import collections
import pandas as pd
from cStringIO import StringIO
from jinja2 import Environment, FileSystemLoader

from collections import OrderedDict


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
        
def mkplots(df):
    plots = OrderedDict()

    fig = figure(title="Population vs. Memory", width=1000, height=500, tools=['box_zoom', 'reset'], toolbar_location="above")
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'population', "memory", 'length')
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Population"
    fig.yaxis.axis_label = "Memory (MB)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    fig.xaxis.formatter = NumeralTickFormatter(format="0,0")
    plots[fig.title.text] = fig
    
    fig = figure(title="Genome length vs. Memory", width=1000, height=500, tools=['box_zoom', 'reset'], toolbar_location="above")
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'length', "memory", 'population')
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Length"
    fig.yaxis.axis_label = "Memory (MB)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    fig.xaxis.formatter = NumeralTickFormatter(format="0,0")
    plots[fig.title.text] = fig

    fig = figure(title="Population vs. Time", width=1000, height=500, tools=['box_zoom', 'reset'], toolbar_location="above")
    fig.title.text_font_size='16pt'
    plot_lines(df, fig, 'population', "time", 'length')
    fig.xaxis.formatter=NumeralTickFormatter(format="00")
    fig.yaxis.formatter=NumeralTickFormatter(format="00")
    fig.xaxis.axis_label = "Population"
    fig.yaxis.axis_label = "Time (ms)"
    fig.xaxis.axis_label_text_font_size='16pt'
    fig.yaxis.axis_label_text_font_size='16pt'
    fig.xaxis.formatter = NumeralTickFormatter(format="0,0")
    fig.yaxis.formatter = NumeralTickFormatter(format="0,0")
    plots[fig.title.text] = fig


    return plots

# Capture parent directory above 'templates/'
THIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

def main():
    p = argparse.ArgumentParser()
    p.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    p.add_argument('outfile', nargs='?', default="site/index.html")
    p.add_argument('-t', '--template', default='template.jinja',
            help="""Jinja2 Tempate file[default: %(default)]""")
    p.add_argument('-v', '--view', default=False,
            help="""Launch browser to view output: %(default)]""")
    a = p.parse_args()

    df = pd.read_csv(a.infile)

    plots = mkplots(df)

    script, div = components(plots)
    
    js_resources = CDN.render_js()
    css_resources = CDN.render_css()
    env = Environment(loader=FileSystemLoader(THIS_DIR),
                          trim_blocks=True)
    # Alias str.format to strformat in template
    env.filters['strformat'] = str.format
    template = env.get_template(a.template)

    html = template.render( date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            command=" ".join(sys.argv),
                            workdir=os.getcwd(),
                            user=getpass.getuser(),
                            title="Santa Performance Plots",
                            js_resources=js_resources,
                            css_resources=css_resources,
                            script=script,
                            div=div)

    with open(a.outfile, "w") as f:
        f.write(html.encode('utf-8'))

    # to deploy to gh-pages, use the function `gh=deploy` defined in ~.bash_profile
    # first copy index.html tp the `site/` directory
    # Cribbed from https://gist.github.com/cobyism/4730490
    #    git subtree push --prefix site origin gh-pages
    if a.view:
        view(a.outfile)


    
if __name__ == '__main__':
    main()

            


