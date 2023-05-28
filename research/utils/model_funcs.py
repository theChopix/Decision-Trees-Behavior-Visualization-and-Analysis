import json

def get_feature_list(model_path):
    """
    :param model_path: path to model json file
    :return: list of feature names 
    """
    model = json.load(open(model_path, "r"))

    float_features = model['features_info']['float_features']
    indices = []

    for feature in range(len(float_features)):
        indices.append(float_features[feature]['feature_id'])

    return indices

# SANKEY
def get_sources(model_path, tree_idx):
    """
    source-nodes of edges in SANKEY graphs

    :param model_path: path to model json file
    :param tree_idx: index of tree in gradient boosting machine
    :return: list of source nodes indices in perfect balanced binary tree
    """
    model = json.load(open(model_path, "r"))
    tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

    n_nodes = 2 ** (tree_depth + 1) - 1
    n_leafs = 2 ** tree_depth

    sources = []
    for i in range(n_nodes - n_leafs):
        sources.append(i)
        sources.append(i)

    return sources


# SANKEY
def get_weights(model_path, tree_idx):
    """
    weights in each edge/path (from node to node) in SANKEY graphs

    :param model_path: path to model json file
    :param tree_idx: index of tree in gradient boosting machine
    :return: list of weights in edges
    """
    model = json.load(open(model_path, "r"))
    tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

    n_nodes = 2 ** (tree_depth + 1) - 1
    leaf_weights = model['oblivious_trees'][0]['leaf_weights']
    n_leafs = len(leaf_weights)
    n_intnodes = n_nodes - n_leafs

    node_weights = [0.] * n_intnodes
    weights = node_weights + leaf_weights

    for i in range(n_intnodes):
        idx = (n_intnodes - 1) - i
        weights[idx] = weights[2 * idx + 1] + weights[2 * idx + 2]

    weights.pop(0)
    return weights


# SANKEY
def get_targets(model_path, tree_idx):
    """
    target-nodes for edges in SANKEY graphs in SANKEY graphs

    :param model_path: path to model json file
    :param tree_idx: index of tree in gradient boosting machine
    :return: list of target nodes indices in perfect balanced binary tree
    """
    model = json.load(open(model_path, "r"))
    tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

    n_nodes = 2 ** (tree_depth + 1) - 1
    n_leafs = 2 ** tree_depth

    targets = []
    for i in range(n_nodes - n_leafs):
        targets.append(2 * i + 1)
        targets.append(2 * i + 2)

    return targets


# SANKEY
def get_labels(model_path, tree_idx):
    """
    labels for nodes in SANKEY graphs - thresholds/borders in internal nodes and classification values in leafs

    :param model_path: path to model json file
    :param tree_idx: index of tree in gradient boosting machine
    :return:
    """
    model = json.load(open(model_path, "r"))
    splits = model['oblivious_trees'][tree_idx]['splits']
    leaf_values = model['oblivious_trees'][tree_idx]["leaf_values"]
    tree_depth = len(splits)

    intnodes_labels = []
    for i in range(tree_depth):
        nodes_layer = 2 ** i
        for j in range(nodes_layer):
            if j == 0:
                feature_index = splits[-i - 1]["float_feature_index"]
                threshold = round(splits[-i - 1]["border"], 3)
                label = str(feature_index) + ", value > " + str(threshold)
                intnodes_labels.append(label)
            else:
                # intnodes_labels.append("")
                feature_index = splits[-i - 1]["float_feature_index"]
                threshold = round(splits[-i - 1]["border"], 3)
                label = str(feature_index) + ", value > " + str(threshold)
                intnodes_labels.append(label)

    leaf_labels = ["value = " + str(round(leaf_value, 3))
                   for leaf_value in leaf_values]
    labels = intnodes_labels + leaf_labels
    return labels


# SANKEY
def get_colors(model_path, tree_idx):
    """
    codes of colors (meeting the split condition) in SANKEY graphs

    :param model_path: path to model json file
    :param tree_idx: index of tree in gradient boosting machine
    :return: codes of colors in tree
    """
    model = json.load(open(model_path, "r"))
    tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

    n_edges = int(2 ** (tree_depth + 1) - 2)

    colors = []
    for i in range(int(n_edges / 2)):
        colors.append("#d0d4cd")
        colors.append("#aeb0ac")

    return colors
