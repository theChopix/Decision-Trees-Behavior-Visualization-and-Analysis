import plotly.graph_objects as go
import pandas as pd
import json
import re

import sys
from utils.sankey import *

tree_idx = int(sys.argv[1])
ftre = sys.argv[2]
mark = sys.argv[3]
cons = sys.argv[4]
color1 = sys.argv[5]
color0 = sys.argv[6]

data_path = "data/validation-set.tsv"
data = pd.read_csv(data_path, delimiter='\t')

model_path = "data/model.json"
model = json.load(open(model_path, "r"))

tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

filter_data = None
if mark == '=':
    def filter_data(d): return d[d[ftre] == float(cons)]
elif mark == '>':
    def filter_data(d): return d[d[ftre] > float(cons)]
elif mark == '<':
    def filter_data(d): return d[d[ftre] < float(cons)]
elif mark == 'equals':
    def filter_data(d): return d[d[ftre] == cons]
elif mark == 'consists':
    def filter_data(d): return d[d[ftre].str.contains(cons, regex=False)]
elif mark == 'regexp':
    def filter_data(d): return d[d[ftre].str.contains(r'' + cons, regex=True)]
num_instances = len(filter_data(data))
total = len(data)

# Attributes into the main part of the figure
_sources, _targets, _colors = get_sources_targets_colors_nlink(
    link=4, tree_depth=tree_depth, color_codes=[color1, color0])
_values = get_values_4link(model, tree_idx, data, filter_data)
node_values = get_node_values(link=4, link_values=_values, tree_depth=tree_depth)
_x = get_x(tree_depth)
_y = get_y(node_values, tree_depth)
_node_customdata = get_node_customdata_4link(
    link_values=_values, node_values=node_values, model=model, tree_idx=tree_idx)
_link_customdata = get_link_customdata_4link(
    link_values=_values, model=model, tree_idx=tree_idx)

# Legend attributes
leg_sources, leg_targets, leg_weights = get_legend_sources_targets_values(
    tree_depth)
leg_node_labels = get_legend_node_labels(model, tree_idx)
leg_x = get_legend_x(tree_depth)
leg_y = get_legend_y(tree_depth)

fig = go.Figure(
    data=[
        # Legend part of the figure
        go.Sankey(
            arrangement="fixed",
            domain={
                'x': [0, 1],
                'y': [0.9, 0.95],
            },
            node=dict(
                pad=5,
                thickness=6,
                color="white",
                line=dict(color="grey", width=0.5),
                label=leg_node_labels,
                x=leg_x,
                y=leg_y,
                hoverinfo='skip',
            ),
            link=dict(
                hoverinfo='skip',
                source=leg_sources,
                target=leg_targets,
                value=leg_weights,
                color="white"
            )
        ),
        # Main part of the figure
        go.Sankey(
            arrangement="fixed",
            domain={
                'x': [0, 1],
                'y': [0, 0.85],
            },
            node=dict(
                pad=5,
                thickness=6,
                color="#989898",
                x=_x,
                y=_y,
                customdata=_node_customdata,
                hovertemplate="%{customdata[0]}%<br>  <b>box_1</b>: %{customdata[1]} / %{customdata[2]}%; <b>queried</b>: %{customdata[3]} / %{customdata[4]}%<br>  <b>box_0</b>: %{customdata[5]} / %{customdata[6]}%; <b>queried</b>: %{customdata[7]} / %{customdata[8]}%<br>%{customdata[9]}%{customdata[10]}"
            ),
            link=dict(
                color=_colors,
                source=_sources,
                target=_targets,
                value=_values,
                customdata=_link_customdata,
                hovertemplate="%{customdata[0]}%<br><b>%{customdata[1]}</b><br>split feature: <b>%{customdata[2]}</b><br><b>%{customdata[3]} %{customdata[4]}</b>"
            )
        )
    ]
)

str_cons = "'" + str(cons) + "'" if ftre == 'query' or ftre == 'url' else str(cons)

title = "Visualization of Decision Tree of <b>Index " + \
    str(tree_idx) + "</b> with Ways of Instances Meeting Condition<br> condition: <b>" + ftre + " " + \
    mark + " " + str_cons + "</b> (" + str(num_instances) + " instances out of " + str(total) + " in the dataset)"
fig.update_layout(title_text=title)

fig.write_html("public/diagram.html")
