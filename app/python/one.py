import plotly.graph_objects as go
import pandas as pd
import json

import sys
from utils.sankey import *

tree_idx = int(sys.argv[1])
inst_idx = int(sys.argv[2])
color1 = sys.argv[3]
color0 = sys.argv[4]

data_path = "data/validation-set.tsv"
data = pd.read_csv(data_path, delimiter='\t')

model_path = "data/model.json"
model = json.load(open(model_path, "r"))

tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

instance = data.iloc[inst_idx]

query = instance['query']
url = instance['url']
box = instance['box']

# Attributes into the main part of the figure
_sources, _targets, _colors = get_sources_targets_colors_nlink(
    link=2, tree_depth=tree_depth, color_codes=[color1, color0])  # ["#F6E8A6", "#B7BEBE"]
_colors = modify_2link_colors_with_instance(model, tree_idx, instance, _colors)
_values = get_values_2link(model, tree_idx, data)
node_values = get_node_values(link=2, link_values=_values, tree_depth=tree_depth)
_x = get_x(tree_depth)
_y = get_y(node_values, tree_depth)
_node_customdata = get_node_customdata_2link(
    link_values=_values, node_values=node_values, model=model, tree_idx=tree_idx)
_link_customdata = get_link_customdata_2link(
    link_values=_values, model=model, tree_idx=tree_idx)
_link_customdata = modify_link_customdata_2link_with_instance(
    model, tree_idx, instance, _link_customdata)

# Legend Attributes
leg_sources, leg_targets, leg_values = get_legend_sources_targets_values(
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
                color="white",
                source=leg_sources,
                target=leg_targets,
                value=leg_values,
                hoverinfo='skip',
            )
        ),
        # Main part of the figure
        go.Sankey(
            arrangement="fixed",
            domain={
                'x': [0, 1],
                'y': [0, 0.85]
            },
            node=dict(
                pad=5,
                thickness=6,
                color="#989898",
                x=_x,
                y=_y,
                customdata=_node_customdata,
                hovertemplate="%{customdata[0]}%<br>  <b>box_1</b>: %{customdata[1]} / %{customdata[2]}%<br>  <b>box_0</b>: %{customdata[3]} / %{customdata[4]}%<br>%{customdata[5]}%{customdata[6]}",
            ),
            link=dict(
                source=_sources,
                target=_targets,
                value=_values,
                color=_colors,
                customdata=_link_customdata,
                hovertemplate="%{customdata[0]}%<br><b>%{customdata[1]}</b><br>split feature: <b>%{customdata[2]}</b><br><b>%{customdata[3]} %{customdata[4]}</b> %{customdata[5]}"
            )
        )
    ]
)

title = "Visualization of Decision Tree of <b>Index " + \
    str(tree_idx) + "</b> with Way of Instance of <b>Index " + \
    str(inst_idx) + "</b> with <b>box_" + str(int(box)) + "</b><br> query: <b>[" + \
    query + "]</b>; url: <b>" + url + "</b>"

fig.update_layout(title_text=title)

fig.write_html("public/diagram.html")
