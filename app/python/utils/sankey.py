import json
import pandas as pd
import colorsys
from typing import List, Tuple, Callable


def get_feature_list(model: dict) -> List[str]:
    """
    :param model: catboost model
    :return: list of feature names 
    """
    float_features = model['features_info']['float_features']
    indices = []

    for feature in range(len(float_features)):
        indices.append(float_features[feature]['feature_id'])

    return indices


def get_split_features(model: dict, tree_idx: int) -> List[str]:
    """
    :param model: catboost model 
    :param tree_idx: tree index in model
    :return: list of split features in tree
    """
    splits = model['oblivious_trees'][tree_idx]['splits']
    tree_depth = len(splits)

    split_features = []
    for layer in range(tree_depth):
        for node in range(2**layer):
            split_feature = splits[-layer-1]['float_feature_index']
            split_features.append(split_feature)

    return split_features


def get_thresholds(model: dict, tree_idx: int) -> List[float]:
    """
    :param model: catboost model
    :param tree_idx: tree index in model
    :return: list of thresholds in tree
    """
    splits = model['oblivious_trees'][tree_idx]['splits']
    tree_depth = len(splits)

    split_features = []
    for layer in range(tree_depth):
        for node in range(2 ** layer):
            split_feature = round(splits[-layer - 1]['border'], 4)
            split_features.append(split_feature)

    return split_features


def get_instance_way(model: dict, tree_idx: int, instance: pd.core.series.Series) -> List[int]:
    """
    :param model: catboost model
    :param tree_idx: tree index in model
    :param instance: data point with all features
    :return: indexes of nodes that are in the instance tree path
    """
    splits = model['oblivious_trees'][tree_idx]['splits']
    tree_dpth = len(splits)
    features = get_feature_list(model)

    instance_way = []

    idx = 0
    instance_way.append(idx)
    for layer in range(tree_dpth):
        if instance[features[splits[-(layer+1)]['float_feature_index']]] <= splits[-(layer+1)]['border']:
            idx = 2 * idx + 1
            instance_way.append(idx)
        else:
            idx = 2 * idx + 2
            instance_way.append(idx)

    return instance_way


def darken_color(color: str, percentage: int) -> str:
    """
    :param color: html color code
    :param percentage: percentage of darkening
    :return: color darkened by the percentage
    """
    # Remove '#' if present
    color = color.lstrip('#')
    # Convert to RGB value
    r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    # Calculate new RGB value
    r = round(r * (100 - percentage) / 100)
    g = round(g * (100 - percentage) / 100)
    b = round(b * (100 - percentage) / 100)
    # Convert back to hex code
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def lighten_color(color: str, percentage: int) -> str:
    """
    :param color: html color code
    :param percentage: percentage of lightening
    :return: color lightened by the percentage
    """
    # Remove '#' if present
    color = color.lstrip('#')
    # Convert to RGB value
    r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    # Calculate new RGB value
    r = round(min(255, r * (100 + percentage) / 100))
    g = round(min(255, g * (100 + percentage) / 100))
    b = round(min(255, b * (100 + percentage) / 100))
    # Convert back to hex code
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def saturate_color(color: str, percentage: int) -> str:
    """
    :param color: html color code
    :param percentage: percentage of saturing 
    :return: color satured by the percentage
    """
    # Remove '#' if present
    color = color.lstrip('#')
    # Convert to RGB value
    r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    # Convert RGB to HSL
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    # Adjust saturation
    s = min(1, max(0, s + percentage / 100))
    # Convert HSL to RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    # Convert back to hex code
    return '#{:02x}{:02x}{:02x}'.format(round(r * 255), round(g * 255), round(b * 255))


def get_node_values(link: int, link_values: List[int], tree_depth: int) -> List[int]:
    """
    :param link: number of links 
    :param values:
    :param tree_depth:
    :return:
    """
    node_values = []
    for i in range(len(link_values) // (2*link)):
        node_values.append(sum(link_values[2*link*i:2*link*i+2*link]))

    # tree_depth = 0
    l_values = link_values[-link*(2**tree_depth):]

    for i in range(2**tree_depth):
        node_values.append(sum(l_values[i*link:i*link + link]))

    return node_values


def add_br_after_dot(str: str) -> str:
    return str.replace(".", "<br>.")


def add_br_after_each_letter(str: str) -> str:
    return "<br>".join(str)


def get_features_tresholds_nodetree_structure(model: dict, tree_idx: int) -> Tuple[List[str], List[float]]:
    """
    For better manipulation feature names and thresholds prepared in list such that its possible to get to them by node indexes

    :param model: catboost model
    :param tree_idx: tree index
    :return: list of features, list of thresholds
    """
    splits = model['oblivious_trees'][tree_idx]['splits']
    tree_depth = len(splits)

    ord_features = get_feature_list(model)

    features = []
    thresholds = []

    for layer in range(tree_depth):
        for node in range(2**layer):
            features.append(
                ord_features[splits[-(layer+1)]['float_feature_index']])
            thresholds.append(round(splits[-(layer+1)]['border'], 4))

    return features, thresholds


def get_sources_targets_colors_nlink(link: int, tree_depth: int, color_codes: List[str]) -> Tuple[List[int], List[int], List[str]]:
    """
    Get attributes for building diagram (all modes)

    :param link: 2 or 4 branch links
    :param tree_depth: tree depth
    :param color_codes: chosen combination of colors
    :return: attributes (sources, targets, colors)
    """

    if link == 4:
        color_codes = [color_codes[0], darken_color(
            color_codes[0], 15), darken_color(color_codes[1], 15), color_codes[1]]

    sources = []
    targets = []
    colors = []

    src_idx = 0
    tar_idx = 1
    for i in range(tree_depth):
        for j in range(2**i):
            for k in range(2*link):
                if k == link:
                    tar_idx += 1
                sources.append(src_idx)
                targets.append(tar_idx)
                colors.append(color_codes[k % link])
            src_idx += 1
            tar_idx += 1

    return sources, targets, colors


def modify_2link_colors_with_instance(model: dict, tree_idx: int, instance: pd.core.series.Series, colors: List[str]) -> List[str]:
    """
    Update coloring of links (branches) with instance way in one-instance mode

    :param model: catboost model
    :param tree_idx: tree index
    :param instance: data point
    :param colors: original colors
    :return: modified colors
    """
    instance_way = get_instance_way(model, tree_idx, instance)
    box = int(instance['box'])

    idx = 0
    for i in range(len(instance_way) - 1):
        idx = 4*instance_way[i]
        if instance_way[i+1] % 2 == 0:
            idx += 2
        # colors[idx] = darken_color(colors[idx], 20)
        colors[idx + 1 - box] = darken_color(colors[idx + 1 - box], 30)

    return colors


def get_values_2link(model: dict, tree_idx: int, data: pd.core.frame.DataFrame) -> List[int]:
    """
    Get values for branch width design in multiple-instances mode (4link) using validation data

    :param model: catboost model for split functions 
    :param tree_idx: tree index
    :param data: validation dataset
    :return: widths of links (parts of branches)
    """
    splits = model['oblivious_trees'][tree_idx]['splits']
    feature_indices = get_feature_list(model)

    tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

    weights = []

    def get_weights_by_index(target_idx):
        prev_node = target_idx

        tree_way = [prev_node]

        while prev_node != 0:
            prev_node = (prev_node - 1) // 2
            tree_way.append(prev_node)

        tree_way.reverse()
        tmp_data = data.copy()

        for i in range(len(tree_way) - 1):
            if tree_way[i+1] % 2 == 1:
                tmp_data = tmp_data[tmp_data[feature_indices[splits[-(
                    i+1)]['float_feature_index']]] <= splits[-(i+1)]['border']]
            else:
                tmp_data = tmp_data[tmp_data[feature_indices[splits[-(
                    i+1)]['float_feature_index']]] > splits[-(i+1)]['border']]

        tar_1 = len(tmp_data[tmp_data['box'] == 1.0])
        tar_0 = len(tmp_data[tmp_data['box'] == 0.0])
        return tar_1, tar_0

    for node_idx in range(2**(tree_depth + 1) - 2):
        tar_1, tar_0 = get_weights_by_index(node_idx+1)
        
        if tar_1 + tar_0 == 0:
            tar_1 = 1

        weights.append(tar_1)
        weights.append(tar_0)

    return weights


def get_values_4link(model: dict, tree_idx: int, data: pd.core.frame.DataFrame, filter: Callable[[pd.core.frame.DataFrame], pd.core.frame.DataFrame]) -> List[int]:
    """
    Get values for branch width design in multiple-instances mode (4link) using validation data

    :param model: catboost model for split functions 
    :param tree_idx: tree index
    :param data: validation dataset
    :param filter: filter function used in multiple-instances mode
    :return: widths of links (parts of branches)
    """
    splits = model['oblivious_trees'][tree_idx]['splits']
    feature_indices = get_feature_list(model)

    tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

    weights = []

    def get_weights_by_index(target_idx):
        prev_node = target_idx

        tree_way = [prev_node]

        while prev_node != 0:
            prev_node = (prev_node - 1) // 2
            tree_way.append(prev_node)

        tree_way.reverse()
        tmp_data = data.copy()

        for i in range(len(tree_way) - 1):
            if tree_way[i+1] % 2 == 1:
                tmp_data = tmp_data[tmp_data[feature_indices[splits[-(
                    i+1)]['float_feature_index']]] <= splits[-(i+1)]['border']]
            else:
                tmp_data = tmp_data[tmp_data[feature_indices[splits[-(
                    i+1)]['float_feature_index']]] > splits[-(i+1)]['border']]

        tar_1 = tmp_data[tmp_data['box'] == 1.0]
        tar_1_i = len(filter(tar_1))
        tar_1 = len(tar_1) - tar_1_i

        tar_0 = tmp_data[tmp_data['box'] == 0.0]
        tar_0_i = len(filter(tar_0))
        tar_0 = len(tar_0) - tar_0_i

        return tar_1, tar_1_i, tar_0_i, tar_0

    for node_idx in range(2**(tree_depth + 1) - 2):
        tar_1, tar_1_i, tar_0_i, tar_0 = get_weights_by_index(node_idx+1)
        
        if tar_1 + tar_1_i + tar_0_i + tar_0 == 0:
            tar_1 += 1
            
        weights.append(tar_1)
        weights.append(tar_1_i)
        weights.append(tar_0_i)
        weights.append(tar_0)

    return weights


def get_x(tree_depth: int) -> List[float]:
    """
    Get x coords of individual nodes in diagram based on tree depth (node positioning)

    :param tree_depth: tree depth
    :return: x coordinates
    """
    # tree_depth = len(model['oblivious_trees'][tree_idx]['splits'])

    ret = []
    base = 0.001
    add = 1.0 / tree_depth
    for i in range(tree_depth+1):
        for j in range(2**i):
            ret.append(base)
        base += add

    return ret


def get_y(node_values: List[int], tree_depth: int) -> List[float]:
    """
    Get y coords of individual nodes in diagram based on widths of branches (node positioning)

    :param node_values: node weights (numbers of data samples in nodes)
    :param tree_depth: tree depth
    :return: y coordinates
    """
    num_instances = node_values[0]

    node_idx = 0

    y = []
    for layer in range(tree_depth + 1):
        cum_sum = 0
        for node in range(2**layer):
            val = (cum_sum + (node_values[node_idx]/2)) / num_instances
            y.append(round(val, 6))
            # y.append((cum_sum) / num_instances)
            # y.append(0.5)

            cum_sum += node_values[node_idx]
            node_idx += 1
    return y


# ############## HOVERLABEL functions (customdata) ###############
# could be without node_values (node_values can be derived from link_values)
def get_node_customdata_2link(link_values: List[int], node_values: List[int], model: dict, tree_idx: int) -> List[List]:
    """
    Get customdata for node hoverlabels in general/one-instance mode (2link) from link widths and node weights

    :param link_values: widths of links (parts of branches) in tree
    :param node_values: node weights (numbers of data samples in nodes)
    :param model: catboost model 
    :param tree_idx: tree index
    :return: customdata further used in hoverlabels
    """
    split_features, thresholds = get_features_tresholds_nodetree_structure(
        model, tree_idx)
    
    leaf_values = model['oblivious_trees'][tree_idx]['leaf_values']

    total = node_values[0]
    custom_data = []

    custom_data.append([round(100*(node_values[0]/total), 2),
                        link_values[0] + link_values[2],
                        round(
                            100*((link_values[0] + link_values[2])/node_values[0]), 2),
                        link_values[1] + link_values[3],
                        round(
                            100*((link_values[1] + link_values[3])/node_values[0]), 2),
                        "split feature: <b>" + split_features[0] + "</b><br>",
                        "threshold: <b>" + str(thresholds[0]) + "</b>"])

    for node_idx in range(len(node_values)-1):
        node_value = node_values[node_idx+1]
        box_1 = link_values[node_idx*2]
        box_0 = link_values[(node_idx*2)+1]
        if node_idx + 1 < len(split_features):
            split_feature = "split feature: <b>" + \
                split_features[node_idx + 1] + "</b><br>"
            threshold = "threshold: <b>" + \
                str(thresholds[node_idx + 1]) + "</b>"
        else:
            split_feature = "value: <b>" + str(round(leaf_values[(node_idx + 1) - len(split_features)], 4)) + "</b>"
            threshold = ""

        custom_data.append([round(100*(node_value/total), 2),
                            box_1,
                            round(100*(box_1/node_value), 2),
                            box_0,
                            round(100*(box_0/node_value), 2),
                            split_feature,
                            threshold])

    return custom_data


def get_node_customdata_4link(link_values: List[int], node_values: List[int], model: dict, tree_idx: int) -> List[List]:
    """
    Get customdata for node hoverlabels in multiple-instances mode (4link) from link widhts and node weights

    :param link_values: widths of links (parts of branches) in tree
    :param node_values: node weights (numbers of data samples in nodes)
    :param model: catboost model
    :param tree_idx: tree index
    :return: customdata further used in hoverlabels
    """
    split_features, thresholds = get_features_tresholds_nodetree_structure(
        model, tree_idx)
    
    leaf_values = model['oblivious_trees'][tree_idx]['leaf_values']

    total = node_values[0]
    custom_data = []

    def save_div(a, b):
        return 0 if b == 0 else a/b

    box_1 = sum(link_values[:2]) + sum(link_values[4:6])
    box_0 = sum(link_values[2:4]) + sum(link_values[6:8])
    box_1_q = link_values[1] + link_values[5]
    box_0_q = link_values[2] + link_values[6]

    custom_data.append([round(100*(node_values[0]/total), 2),
                        box_1,
                        round(100*((box_1)/node_values[0]), 2),
                        box_1_q,
                        round(100*(save_div(box_1_q, box_1)), 2),
                        box_0,
                        round(100*((box_0)/node_values[0]), 2),
                        box_0_q,
                        round(100*(save_div(box_0_q, box_0)), 2),
                        "split feature: <b>" + split_features[0] + "</b><br>",
                        "threshold: <b>" + str(thresholds[0]) + "</b>"])

    for node_idx in range(len(node_values)-1):
        node_value = node_values[node_idx+1]
        box_1 = link_values[4*node_idx] + link_values[4*node_idx+1]
        box_0 = link_values[4*node_idx+2] + link_values[4*node_idx+3]
        box_1_q = link_values[4*node_idx+1]
        box_0_q = link_values[4*node_idx+2]
        if node_idx + 1 < len(split_features):
            split_feature = "split feature: <b>" + \
                split_features[node_idx + 1] + "</b><br>"
            threshold = "threshold: <b>" + \
                str(thresholds[node_idx + 1]) + "</b>"
        else:
            split_feature = "value: <b>" + str(round(leaf_values[(node_idx + 1) - len(split_features)], 4)) + "</b>"
            threshold = ""

        custom_data.append([round(100*(node_value/total), 2),
                            box_1,
                            round(100*(box_1/node_value), 2),
                            box_1_q,
                            round(100*(save_div(box_1_q, box_1)), 2),
                            box_0,
                            round(100*(box_0/node_value), 2),
                            box_0_q,
                            round(100*(save_div(box_0_q, box_0)), 2),
                            split_feature,
                            threshold])

    return custom_data


def get_link_customdata_2link(link_values: List[int], model: dict, tree_idx: int) -> List[List]:
    """
    Get customdata for branch hoverlabels in general/one-instance mode (2link) from link widths

    :param link_values: widths of links (parts of branches) in tree
    :param model: catboost model
    :param tree_idx: tree index
    :return: customdata further used in hoverlabels
    """
    split_features, thresholds = get_features_tresholds_nodetree_structure(
        model, tree_idx)

    link_split_features = []
    link_thresholds = []

    for feature in split_features:
        link_split_features += [feature] * 4

    for threshold in thresholds:
        link_thresholds += [threshold] * 4

    total = sum(link_values[:4])

    customdata = []
    for link_idx in range(len(link_values)):
        box = "box_0" if link_idx % 2 else "box_1"
        mark = "=<" if link_idx % 4 < 2 else ">"
        node_value = link_values[link_idx]+link_values[link_idx -
                                                       1] if link_idx % 2 else link_values[link_idx]+link_values[link_idx+1]
        customdata.append([round(100*link_values[link_idx]/total, 2),
                           box,
                           link_split_features[link_idx],
                           mark,
                           link_thresholds[link_idx]
                           ])
    return customdata


def get_link_customdata_4link(link_values: List[int], model: dict, tree_idx: int) -> List[List]:
    """
    Get customdata for branch hoverlabels in multiple-instances mode (4link) from link widths

    :param link_values: widths of links (parts of branches) in tree
    :param model: catboost model
    :param tree_idx: tree index
    :return: customdata futher used in hoverlabels
    """
    split_features, thresholds = get_features_tresholds_nodetree_structure(
        model, tree_idx)

    link_split_features = []
    link_thresholds = []

    for feature in split_features:
        link_split_features += [feature] * 8

    for threshold in thresholds:
        link_thresholds += [threshold] * 8

    total = sum(link_values[:8])

    box_labels = ["box_1 non-queried", "box_1 queried",
                  "box_0 queried", "box_0 non-queried"]
    customdata = []
    for link_idx in range(len(link_values)):
        box = box_labels[link_idx % 4]
        mark = "=<" if link_idx % 8 < 4 else ">"
        customdata.append([round(100*link_values[link_idx]/total, 2),
                           box,
                           link_split_features[link_idx],
                           mark,
                           link_thresholds[link_idx]
                           ])
    return customdata


def modify_link_customdata_2link_with_instance(model: dict, tree_idx: int, instance: pd.core.series.Series, customdata: List[List]) -> List[List]:
    """
    Add instance's values in customdata (for hoverlabels) in one-instance mode

    :param model: catboost model
    :param tree_idx: tree index
    :param instance: data point
    :param customdata: original customdata
    :return: modified customdata
    """
    instance_way = get_instance_way(model, tree_idx, instance)
    box = int(instance['box'])
    instance_indices = []

    idx = 0
    for i in range(len(instance_way) - 1):
        idx = 4*instance_way[i]
        if instance_way[i+1] % 2 == 0:
            idx += 2
        instance_indices.append(idx + 1 - box)

    for j in range(len(customdata)):
        if j in instance_indices:
            feature = customdata[j][2]
            instance_value = round(instance[feature], 4)
            customdata[j].append(
                "[instance's value: <b>" + str(instance_value) + "</b>]")
        else:
            customdata[j].append("")

    return customdata


# ############## LEGEND functions ###############
def get_legend_sources_targets_values(tree_depth: int) -> Tuple[List[int], List[int], List[int]]:
    """
    :param tree_depth: depth tree
    :return: attributes needed for creation of 'legend diagram'
    """
    sources = list(range(tree_depth))
    targets = [i+1 for i in sources]
    values = (tree_depth) * [10]

    return sources, targets, values


def get_legend_node_labels(model: dict, tree_idx: int) -> List[str]:
    """
    :param model: catboost model
    :param tree_idx: tree index
    :return: formated 
    """
    splits = model['oblivious_trees'][tree_idx]['splits']
    features = get_feature_list(model)
    tree_depth = len(splits)

    labels = []
    for layer in range(tree_depth):
        labels.append("feature:<br><b>" +
                      add_br_after_dot(
                          features[splits[-(layer+1)]["float_feature_index"]])
                      + "</b><br>threshold:<br><b>" +
                      str(round(splits[-(layer+1)]["border"], 4)) + "</b>")

    labels.append("")
    return labels


def get_legend_x(tree_depth: int) -> List[float]:
    """
    :param tree_depth: tree depth
    :return: x coords
    """
    ret = []
    base = 0.001

    add = 1.0 / tree_depth
    for i in range(tree_depth+1):
        ret.append(base)
        base += add

    return ret


def get_legend_y(tree_depth: int) -> List[float]:
    """
    :param tree_depth: tree depth
    :return: y coords 
    """
    return [0.0] * (tree_depth + 1)


