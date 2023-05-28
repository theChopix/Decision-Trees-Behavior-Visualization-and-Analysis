import pandas as pd


def get_validation_data(data_path):
    """
    Validation data used to train the model

    :param data_path: path to data in tsv file
    :return: data in the form of X (features) and y (targets)
    """
    data = pd.read_csv(data_path, delimiter='\t', encoding='latin-1')
    X = data.drop(['query', 'url', 'box'], axis=1)
    y = data['box']
    features_names = data.columns.values[3:]
    return X, y, features_names

