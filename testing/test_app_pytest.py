import pickle
from datetime import datetime, timedelta

import keras
import numpy as np
import pytest
from sklearn.pipeline import Pipeline

import utility_functions.functions_d3__prepare_store_data
from utility_functions.functions_gh_presentation_and_launch import load_model
from utility_functions.functions_d3__prepare_store_data import this_test_data

debug_mode = False

testdata_standard_model = []
for each in [
    'optimised_model_CatBoost_v06',
    'optimised_model_KNN_v06',
    # 'optimised_model_Light Gradient Boosting_v06',
    'optimised_model_Linear Regression (Ridge)_v06',
    'optimised_model_Linear Regression (Ridge)_v11',
    'optimised_model_Random Forest_v09',
    'optimised_model_XG Boost (tree)_v10',
    'optimised_model_XG Boost (tree)_v11',
]:
    testdata_standard_model.append(("models_pretrained", each, each[-2:], Pipeline))

testdata_neural_network = [
    # ("models_pretrained", "optimised_model_Neural Network_v06", '06', keras.models.Sequential),
    #    ("models_pretrained", "neural network m11 mega (v06)_v06", '06', keras.models.Sequential),
    # ("models_pretrained", "neural network m15 mega + dropout (v11)_v11", '06', keras.models.Sequential),
    #    ("models_pretrained", "neural network m15 mega + dropout (v11)_v11", '11', keras.models.Sequential),
    # ("models", "optimised_model_Neural Network m12 mega_v06", '06', keras.models.Sequential),
    # ("models", "optimised_model_Neural Network m15 mega + dropout_v09", '09', keras.models.Sequential)
    # ?? ("models_pretrained", "optimised_neural network m15 mega + dropout (v09)_v09", '09', keras.models.Sequential)
    ("models_pretrained", "optimised_neural network m16 mega + dropout (v11)_v11", '11', keras.models.Sequential)
]


@pytest.mark.parametrize("directory,selected_model,version,expected_type", testdata_standard_model)
def test_load_standard_model(directory, selected_model, version, expected_type):
    model = load_model(selected_model, directory)

    # if debug_mode:print("xgb.__version__", xgb.__version__);print(model);print(model[-1])

    assert type(model) == expected_type
    return model


@pytest.mark.parametrize("directory,selected_model,version,expected_type", testdata_standard_model)
def test_predict_using_standard_model(directory, selected_model, version, expected_type):
    model = test_load_standard_model(directory, selected_model, version, expected_type)

    X_test, y_test, feature_names = this_test_data(VERSION=version, test_data_only=True, cloud_or_webapp_run=False, versioned=True)

    y_pred = model.predict(X_test)
    assert type(y_pred) == type(y_test)
    assert len(y_pred) == len(y_test)

    ensure_predictions_are_valid(y_pred, y_test)

    # if debug_mode:print(y_pred, len(y_pred));print(y_test, len(y_test));y_pred[0] == y_test[0]


def ensure_predictions_are_valid(y_pred, y_test):
    for i in range(len(y_pred)):
        # assert y_pred[i] == y_test[i]
        maximum_wrong_factor = 4
        assert y_pred[i] < y_test[i] * maximum_wrong_factor
        assert y_pred[i] > y_test[i] / maximum_wrong_factor


@pytest.mark.parametrize("directory,selected_model,version,expected_type", testdata_neural_network)
def test_load_neural_network(directory, selected_model, version, expected_type):
    model = load_model(selected_model, directory, model_type='neural')

    assert type(model) == expected_type
    return model


@pytest.mark.parametrize("directory,selected_model,version,expected_type", testdata_neural_network)
def test_predict_using_neural_network(directory, selected_model, version, expected_type):
    model = test_load_neural_network(directory, selected_model, version, expected_type)

    X_test, y_test, feature_names = utility_functions.functions_d3__prepare_store_data.this_test_data(VERSION=version, test_data_only=True, cloud_or_webapp_run=False, versioned=True)

    debug_mode = False
    if debug_mode:
        y_test = [y_test[0]]
        X_test = [[2.0000,
              1.0000,
              0.3908,
              51.4437,
              -0.4030,
              0.0560,
              0.2986,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              0.0000,
              1.0000,
              0.0000,
              ]]
    print(X_test)
    print(len(X_test))
    print(len(X_test[0]))

    y_pred = model.predict(X_test)

    print("y_pred:", y_pred)
    print("y_test:", y_test)

    if not debug_mode:
        assert type(y_pred) == type(y_test)
        len(y_pred)
        len(y_test)
        assert len(y_pred) == len(y_test)


    ensure_predictions_are_valid(y_pred, y_test)

    # if debug_mode:print(y_pred, len(y_pred));print(y_test, len(y_test));assert y_pred[0] == y_test[0]
