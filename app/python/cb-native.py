import json
import catboost as cb
import pandas as pd
import sys

from utils.sankey import *

tree_idx = int(sys.argv[1])

model_path = "data/model.json"
data_path = "data/validation-set.tsv"

model = cb.CatBoostRegressor();
model.load_model(model_path, format='json');

model_json = json.load(open(model_path, "r"))

features = get_feature_list(model_json)

data = pd.read_csv(data_path, delimiter='\t', encoding='latin-1')
X = data.drop(['query', 'url', 'box'], axis=1)

pool = cb.Pool(data=X, feature_names=features)

viz = model.plot_tree(tree_idx=tree_idx, pool=pool)

viz.render(filename='catboost-native', format='pdf', directory='public')

