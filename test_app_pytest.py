import pickle
from datetime import datetime, timedelta

import keras
import pytest
from sklearn.pipeline import Pipeline

import functions_d3__prepare_store_data_2023
from functions_gh_presentation_and_launch import load_standard_model

debug_mode = False

testdata_standard_model = []
for each in [
    'optimised_model_KNN_v06',
    'optimised_model_XG Boost_v06',
    'optimised_model_Decision Tree_v06',
    'optimised_model_CatBoost_v06',
    'optimised_model_Linear Regression (Ridge)_v06',
]:
    testdata_standard_model.append(("models_pretrained", each, '06', Pipeline))

for each in [
    'optimised_model_XG Boost (tree)_v11',
    'optimised_model_Linear Regression (Ridge)_v11',
]:
    testdata_standard_model.append(("models_pretrained", each, '11', Pipeline))

testdata_neural_network = [
    ("models_pretrained", "optimised_model_Neural Network_v06", '06', keras.models.Sequential),
    # ("models", "optimised_model_Neural Network m12 mega_v06", '06', keras.models.Sequential),
    # ("models", "optimised_model_Neural Network m15 mega + dropout_v09", '09', keras.models.Sequential)
]


@pytest.mark.parametrize("directory,selected_model,version,expected_type", testdata_standard_model)
def test_load_standard_model(directory, selected_model, version, expected_type):
    model = load_standard_model(selected_model, directory)

    #if debug_mode:print("xgb.__version__", xgb.__version__);print(model);print(model[-1])

    assert type(model) == expected_type
    return model


@pytest.mark.parametrize("directory,selected_model,version,expected_type", testdata_standard_model)
def test_predict_using_standard_model(directory, selected_model, version, expected_type):
    model = test_load_standard_model(directory, selected_model, version, expected_type)

    X_test, y_test = functions_d3__prepare_store_data_2023.this_test_data(VERSION=version, test_data_only=True, cloud_or_webapp_run=False, versioned=True)

    y_pred = model.predict(X_test)
    assert type(y_pred) == type(y_test)
    assert len(y_pred) == len(y_test)

    #if debug_mode:print(y_pred, len(y_pred));print(y_test, len(y_test));y_pred[0] == y_test[0]

@pytest.mark.parametrize("directory,selected_model,version,expected_type", testdata_neural_network)
def test_load_neural_network(directory, selected_model, version, expected_type):

    model = load_standard_model(selected_model, directory, model_type='neural')

    assert type(model) == expected_type
    return model


@pytest.mark.parametrize("directory,selected_model,version,expected_type", testdata_neural_network)
def test_predict_using_neural_network(directory, selected_model, version, expected_type):
    model = test_load_neural_network(directory, selected_model, version, expected_type)

    X_test, y_test = functions_d3__prepare_store_data_2023.this_test_data(VERSION=version, test_data_only=True, cloud_or_webapp_run=False)

    y_pred = model.predict(X_test)
    assert type(y_pred) == type(y_test)
    assert len(y_pred) == len(y_test)

    #if debug_mode:print(y_pred, len(y_pred));print(y_test, len(y_test));assert y_pred[0] == y_test[0]
