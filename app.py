import time

import pandas as pd
import streamlit as st
import numpy as np
import random
import matplotlib.pyplot as plt
import os

from sklearn.metrics import PredictionErrorDisplay
from sklearn.model_selection import cross_validate, cross_val_predict

from utility_functions.functions_b__get_the_data import get_source_dataframe
from utility_functions.functions_d3__prepare_store_data import this_test_data
from utility_functions.functions_gh_presentation_and_launch import load_model, get_webapp_models

RAND_INDEX_CSV = "webapp_deployment/cache/rand_index.csv"
#RANDOM_INSTANCE_CSV = "random_instance.csv"
RANDOM_INSTANCE_PLUS_CSV = "webapp_deployment/cache/random_instance_plus.csv"

st.set_option('deprecation.showfileUploaderEncoding', False)

df, X_test, y_test, feature_names = None, None, None, None
rand_index = -1

DATA_VERSION = None
previous_data_version = DATA_VERSION

prediction_models = {
    'XG Boost (data version 11) - Best model': 'optimised_model_XG Boost (tree)_v11',
    'Stacked Model [xgb,lgb,knn] (data version 6) - Great model': 'optimised_model_Stacked Model_v06',
    'KNN (data version 6) - Fastest to train, Good model': 'optimised_model_KNN_v06',
    'XG Boost (data version 10) - Good model': 'optimised_model_XG Boost (tree)_v10',
    'Catboost (data version 6) - Good model': 'optimised_model_CatBoost_v06',
    'Light Gradient Boosting (data version 6) - Good model': 'optimised_model_Light Gradient Boosting_v06',
    'Stacked Model - still in beta (data version 11)': 'optimised_model_Stacked Model_v11',
    'Random Forests (data version 9) - Fair model': 'optimised_model_Random Forest_v09',
    'Neural Network (data version 11) - Mediocre model': 'optimised_neural network m16 mega + dropout (v11)_v11',
    'Linear Regression (data version 11) - Poor model': 'optimised_model_Linear Regression (Ridge)_v11',
    'Linear Regression (data version 6) - Poor model': 'optimised_model_Linear Regression (Ridge)_v06',
}

prediction_models = get_webapp_models()

def main():
    global X_test, y_test, feature_names, rand_index, DATA_VERSION, previous_data_version

    st.markdown(
        "<h1 style='text-align: center; color: White;background-color:#e84343'>London Property Prices Predictor</h1>",
        unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: Black;'>Choose a random property and a prediction algorithm, and predict the property price</h4>",
                unsafe_allow_html=True)

    st.sidebar.header("What is this Project about?")
    st.sidebar.markdown(
        "This is a Web app that can predict the price of a London property based on features of that property.")
    st.sidebar.header("Sidebar Options")

    available_model_names = prediction_models.keys()
    # print(available_model_names)
    # print(type(available_model_names))
    # print(type(list(available_model_names)))
    # print(list(available_model_names))
    #available_model_names = [x[0] + " - " + x[1] for x in available_model_names]

    #def print_something(filter_versions):
    #    print('something')
    #date = st.selectbox('Select a day', dates, format_func=day_name, key='date', index=st.session_state['date_index'], on_change=update_date_index, args=(dates,))
    filter_versions = ['all versions', 'v06','v09','v10','v11']
    #limit_to_version = st.selectbox('Limit to version?', filter_versions, on_change=(print_something), key='date', args=(filter_versions,))

    selected_model_key = st.selectbox('Which model do you want to use?', available_model_names)

    selected_model_name, selected_model_verdict, selected_model, selected_model_version = prediction_models[selected_model_key]
    print("selected_model",selected_model)
    print("selected_model_key",selected_model_key)
    model = load_model_wrapper(selected_model, model_type='neural' if 'eural' in selected_model_key else 'standard')

    # manual_parameters = st.checkbox('Use manual parameters instead of sample')
    manual_parameters = False
    if not manual_parameters:
        DATA_VERSION = selected_model_version
        print("DATA_VERSION", DATA_VERSION)
        X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
        test_size = len(y_test)
        #pass

    else:
        lati = st.slider("Input Your latitude", 51.00, 52.00)
        longi = st.slider("Input your longitude", -0.5, 0.3)
        beds = st.slider("Input number of bedrooms", 0, 6)
        baths = st.slider("Input number of bathrooms", 0, 6)

        inputs = [[lati, longi, beds, baths]]

    if st.sidebar.button('Change the random property!'):
        test_size = change_the_random_property(DATA_VERSION, test_size)

    if st.button('Choose another random property, and Predict'):
        test_size = change_the_random_property(DATA_VERSION, test_size)
        model = predict_and_display(manual_parameters, model, selected_model, selected_model_key, selected_model_name, selected_model_version, test_size)


    if st.button('Predict'):
        model = predict_and_display(manual_parameters, model, selected_model, selected_model_key, selected_model_name, selected_model_version, test_size)

    if st.checkbox('View all available predictions (entire test set)'):
        DATA_VERSION = selected_model[-2:]
        DATA_VERSION = selected_model_version

        X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
        try:
            acc = model.score(X_test, y_test)
            st.write('Accuracy of test set: ', acc)
        except:
            pass

        y_pred = model.predict(X_test).flatten()
        multiple_predictions = np.vstack((y_test.flatten(), y_pred)).T
        multiple_predictions_df = pd.DataFrame(multiple_predictions, columns=['Actual Price', 'Predicted Price'])

        st.write(multiple_predictions_df)
        print("type(multiple_predictions_df):", type(multiple_predictions_df))

    if not manual_parameters:
        pass
        # if st.button('Get a different random property!'):
        #     rand_index, random_instance, random_instance[0] = randomise_property(DATA_VERSION, test_size)
        #     st.text(f'sample variables ({rand_index}): {random_instance[0]}')
        #     st.text(f'Expected prediction: {y_test[rand_index]}')

    if st.checkbox('Show the underlying dataframe'):
        DATA_VERSION = selected_model[-2:]
        DATA_VERSION = selected_model_version

        df, df_type = get_source_dataframe(cloud_or_webapp_run=True, version=DATA_VERSION, folder_prefix='')
        print("claiming to be colab so I can use the cloud version of data and save space")
        st.write(df)


def predict_and_display(manual_parameters, model, selected_model, selected_model_key, selected_model_name, selected_model_version, test_size):
    global DATA_VERSION, X_test, y_test, feature_names, rand_index, previous_data_version
    DATA_VERSION = selected_model[-2:]
    DATA_VERSION = selected_model_version
    X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
    try:
        acc = model.score(X_test, y_test)
        st.write('Accuracy of test set: ', acc)
    except:
        pass
    if not manual_parameters:
        try:
            raise InterruptedError("don't ever do this actually")
            random_instance_plus = np.loadtxt(RANDOM_INSTANCE_PLUS_CSV, delimiter=",")
            print("random_instance_plus:", random_instance_plus)
            rand_index = int(random_instance_plus[0])
            print("rand_index:", rand_index)
            expected = random_instance_plus[1]
            print("expected:", expected)
            inputs = [random_instance_plus[2:]]
            print("[random_instance_plus[2:]]:", [random_instance_plus[2:]])

            random_instance = [X_test[rand_index]]

        except:
            try:
                print("trying to get old rand_index of", rand_index)
                rand_index_arr = np.loadtxt(RAND_INDEX_CSV, delimiter=",")
                print("found old rand_index", rand_index_arr)
                rand_index = int(rand_index_arr)
                print("loaded old rand_index of", rand_index)
            except:
                print("couldn't retrieve the old rand_index, generating a new one")
                rand_index = random.randint(0, test_size - 1)
                print("new rand_index is", rand_index)
                np.savetxt(RAND_INDEX_CSV, [rand_index], delimiter=",")
                print("saved new rand_index of", rand_index)

            DATA_VERSION = selected_model[-2:]
            DATA_VERSION = selected_model_version

            X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)

            previous_data_version = DATA_VERSION

            random_instance = [X_test[rand_index]]
            inputs = random_instance
            expected = y_test[rand_index]
            # np.savetxt(RANDOM_INSTANCE_CSV, random_instance, delimiter=",")
            random_instance_plus = [rand_index, expected]
            random_instance_plus.extend(random_instance[0])
            np.savetxt(RANDOM_INSTANCE_PLUS_CSV, random_instance_plus, delimiter=",")

        update_about_property(feature_names, rand_index, random_instance)

        # st.text(f'Actual value of property {rand_index}: {expected}')
    # print("inputs:", inputs)
    # print("inputs:", len(inputs))
    # print("inputs:", len(inputs[0]))
    model = load_model_wrapper(selected_model, model_type='neural' if 'eural' in selected_model_key else 'standard')
    X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=False, versioned=True)
    print("length of test instance(1): ", len(X_test[0]))
    random_instance = [X_test[rand_index]]
    print("length of test instance(2): ", len(X_test[0]))
    print("length of test instance(3): ", len([X_test[rand_index]]))
    print("test instance(3): ", [X_test[rand_index]])
    print("length of test instance(4): ", len(random_instance))
    fake_X = [[0] * len(X_test[0]), ]
    # result = model.predict(fake_X)
    print("length of test instance(5): ", len(fake_X))
    print(fake_X)
    print(len(fake_X), len(fake_X[0]), type(fake_X), type(fake_X[0]))
    print(random_instance)
    print(len(random_instance), len(random_instance[0]), type(random_instance), type(random_instance[0]))
    random_instance = [random_instance[0].tolist()]
    print(random_instance)
    print(len(random_instance), len(random_instance[0]), type(random_instance), type(random_instance[0]))
    # result = model.predict(X_test)
    result = model.predict(random_instance)
    updated_res = result.flatten().astype(float)
    st.success('The predicted price for this property is £{:.0f}'.format(updated_res[0]))
    st.warning('The actual price for this property is £{:.0f}'.format(expected))
    fig, ax = plt.subplots()
    # X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=False, versioned=True)
    # model = load_model_wrapper(selected_model, model_type='neural' if 'eural' in selected_model_key else 'standard')
    y_pred = model.predict(X_test).flatten()
    if 'eural' in selected_model_key:
        from sklearn.metrics import r2_score
        st.write('Score:', r2_score(y_test, y_pred))
        try:
            st.write('Accuracy of test set: ', acc)
        except:
            pass
    ax.scatter(y_test, y_pred, s=25, c='silver')
    # ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, c='black')
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], lw=2, c='black')
    difference = abs(expected - updated_res[0])
    if difference < 10000:
        colour = 'lime'
    elif difference < 80000:
        colour = 'orange'
    else:
        colour = 'red'
    try:
        ax.scatter(expected, updated_res[0], s=100, c=colour)
    except:
        pass
    ax.set_title("Comparing actual property values to values predicted by " + selected_model_name)
    ax.set_xlabel('Actual property price')
    ax.set_ylabel('Predicted property price')
    plt.ticklabel_format(style='plain')
    st.pyplot(fig)
    return model


def change_the_random_property(DATA_VERSION, test_size):
    global X_test, y_test, feature_names, rand_index
    X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
    test_size = len(y_test)
    rand_index, random_instance, random_instance[0] = randomise_property(DATA_VERSION, test_size)
    update_about_property(feature_names, rand_index, random_instance)
    return test_size


def update_about_property(feature_names, rand_index, random_instance):
    st.sidebar.subheader("About your chosen property")
    # df, df_type = get_source_dataframe(cloud_or_webapp_run=True, version=DATA_VERSION, folder_prefix='')
    print("rand_index", rand_index)
    print("random_instance", random_instance)
    print("random_instance[0]", len(random_instance[0]))
    print("feature_names", len(feature_names), feature_names[0], '...', feature_names[-1])
    random_instance_df = pd.DataFrame(random_instance[0], index=feature_names)
    random_instance_df.columns = ['random=' + str(rand_index)]
    st.sidebar.table(random_instance_df)


def randomise_property(DATA_VERSION, test_size):
    global rand_index, X_test, y_test
    rand_index = random.randint(0, test_size - 1)
    X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
    random_instance = [X_test[rand_index]]
    #np.savetxt(RANDOM_INSTANCE_CSV, random_instance, delimiter=",")
    expected = y_test[rand_index]
    #np.savetxt(RANDOM_INSTANCE_CSV, random_instance, delimiter=",")
    random_instance_plus = [rand_index, expected]
    random_instance_plus.extend(random_instance[0])
    print("random_instance_plus:", random_instance_plus)
    np.savetxt(RANDOM_INSTANCE_PLUS_CSV, [random_instance_plus], delimiter=",")
    np.savetxt(RAND_INDEX_CSV, [rand_index], delimiter=",")

    return rand_index, random_instance, random_instance[0]


#@st.cache
def load_model_wrapper(selected_model, model_type):
    return load_model(selected_model, model_type=model_type)


if __name__ == '__main__':
    main()
