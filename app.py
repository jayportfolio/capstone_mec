import time

import pandas as pd
import streamlit as st
import numpy as np
import random
import matplotlib.pyplot as plt
import os

from sklearn.metrics import PredictionErrorDisplay
from sklearn.model_selection import cross_validate, cross_val_predict

from functions_b__get_the_data_2023 import get_source_dataframe
from functions_d3__prepare_store_data_2023 import this_test_data
from functions_gh_presentation_and_launch import load_model

st.set_option('deprecation.showfileUploaderEncoding', False)

df, X_test, y_test, feature_names = None, None, None, None
rand_index = -1

DATA_VERSION = None
previous_data_version = DATA_VERSION

prediction_models = {
    'XG Boost (data version 11) - Best model': 'optimised_model_XG Boost (tree)_v11',
    'Stacked Model - still in beta': 'optimised_model_Stacked Model_v11',
    'XG Boost (data version 10) - Good model': 'optimised_model_XG Boost (tree)_v10',
    'KNN (data version 6) - Fastest to train, Good model': 'optimised_model_KNN_v06',
    'Catboost (data version 6) - Good model': 'optimised_model_CatBoost_v06',
    'Light Gradient Boosting (data version 6) - Good model': 'optimised_model_Light Gradient Boosting_v06',
    'Random Forests (data version 9) - Fair model': 'optimised_model_Random Forest_v09',
    'Neural Network (data version 11) - Mediocre model': 'optimised_neural network m16 mega + dropout (v11)_v11',
    'Linear Regression (data version 11) - Poor model': 'optimised_model_Linear Regression (Ridge)_v11',
    'Linear Regression (data version 6) - Poor model': 'optimised_model_Linear Regression (Ridge)_v06',
}


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

    available_models = prediction_models.keys()

    selected_model_key = st.selectbox('Which model do you want to use?', available_models)

    selected_model = prediction_models[selected_model_key]
    model = load_model(selected_model, model_type='neural' if 'eural' in selected_model_key else 'standard')

    # manual_parameters = st.checkbox('Use manual parameters instead of sample')
    manual_parameters = False
    if not manual_parameters:
        DATA_VERSION = selected_model[-2:]
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
        X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
        test_size = len(y_test)
        rand_index, random_instance, random_instance[0] = randomise_property(DATA_VERSION, test_size)

        update_about_property(feature_names, rand_index, random_instance)

    if st.button('Predict'):
        DATA_VERSION = selected_model[-2:]
        X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
        try:
            acc = model.score(X_test, y_test)
            st.write('Accuracy of test set: ', acc)
        except:
            pass


        if not manual_parameters:
            try:
                raise InterruptedError("don't ever do this actually")
                random_instance_plus = np.loadtxt("random_instance_plus.csv", delimiter=",")
                print("random_instance_plus:", random_instance_plus)
                rand_index = int(random_instance_plus[0])
                print("rand_index:", rand_index)
                expected = random_instance_plus[1]
                print("expected:", expected)
                inputs = [random_instance_plus[2:]]
                print("[random_instance_plus[2:]]:",[random_instance_plus[2:]])

                random_instance = [X_test[rand_index]]

            except:
                try:
                    print("trying to get old rand_index of", rand_index)
                    rand_index_arr = np.loadtxt("rand_index.csv", delimiter=",")
                    print("found old rand_index", rand_index_arr)
                    rand_index = int(rand_index_arr)
                    print("loaded old rand_index of", rand_index)
                except:
                    print("couldn't retrieve the old rand_index, generating a new one")
                    rand_index = random.randint(0, test_size - 1)
                    print("new rand_index is", rand_index)
                    np.savetxt("rand_index.csv", [rand_index], delimiter=",")
                    print("saved new rand_index of", rand_index)

                DATA_VERSION = selected_model[-2:]
                X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)

                previous_data_version = DATA_VERSION

                random_instance = [X_test[rand_index]]
                inputs = random_instance
                expected = y_test[rand_index]
                np.savetxt("random_instance.csv", random_instance, delimiter=",")
                random_instance_plus = [rand_index, expected]
                random_instance_plus.extend(random_instance[0])
                np.savetxt("random_instance_plus.csv", random_instance_plus, delimiter=",")

            update_about_property(feature_names, rand_index, random_instance)

            # st.text(f'Actual value of property {rand_index}: {expected}')

        # print("inputs:", inputs)
        # print("inputs:", len(inputs))
        # print("inputs:", len(inputs[0]))

        X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=False, versioned=True)
        fake_X = [[0]*len(X_test[0]),]
        #result = model.predict(fake_X)
        result = model.predict(X_test)
        updated_res = result.flatten().astype(float)
        st.success('The predicted price for this property is £{:.0f}'.format(updated_res[0]))
        st.warning('The actual price for this property is £{:.0f}'.format(expected))

        fig, ax = plt.subplots()
        X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=False, versioned=True)
        y_pred = model.predict(X_test).flatten()

        if 'eural' in selected_model_key:
            from sklearn.metrics import r2_score
            st.write('Score:' + str(r2_score(y_test, y_pred)))

        ax.scatter(y_test, y_pred, s=25, c='blue')
        ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, c='black')
        try:
            ax.scatter(expected, updated_res[0], s=100, c='orange')
        except:
            pass
        ax.set_title("Comparing actual property values to values predicted by " + selected_model_key)
        ax.set_xlabel('Actual property price')
        ax.set_ylabel('Predicted property price')
        plt.ticklabel_format(style='plain')

        st.pyplot(fig)

    if st.checkbox('View all available predictions (entire test set)'):
        DATA_VERSION = selected_model[-2:]
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
        df, df_type = get_source_dataframe(cloud_or_webapp_run=True, version=DATA_VERSION, folder_prefix='')
        print("claiming to be colab so I can use the cloud version of data and save space")
        st.write(df)


def update_about_property(feature_names, rand_index, random_instance):
    st.sidebar.subheader("About your chosen property")
    # df, df_type = get_source_dataframe(cloud_or_webapp_run=True, version=DATA_VERSION, folder_prefix='')
    print("rand_index", rand_index)
    print("random_instance", random_instance)
    print("random_instance[0]", len(random_instance[0]))
    print("feature_names", len(feature_names))
    random_instance_df = pd.DataFrame(random_instance[0], index=feature_names)
    random_instance_df.columns = ['random=' + str(rand_index)]
    st.sidebar.table(random_instance_df)


def randomise_property(DATA_VERSION, test_size):
    global rand_index, X_test, y_test
    rand_index = random.randint(0, test_size - 1)
    X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
    random_instance = [X_test[rand_index]]
    np.savetxt("random_instance.csv", random_instance, delimiter=",")
    expected = y_test[rand_index]
    np.savetxt("random_instance.csv", random_instance, delimiter=",")
    random_instance_plus = [rand_index, expected]
    random_instance_plus.extend(random_instance[0])
    print("random_instance_plus:", random_instance_plus)
    np.savetxt("random_instance_plus.csv", [random_instance_plus], delimiter=",")
    np.savetxt("rand_index.csv", [rand_index], delimiter=",")

    return rand_index, random_instance, random_instance[0]


if __name__ == '__main__':
    main()
