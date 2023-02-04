import pandas as pd
import streamlit as st
import numpy as np
import random
import matplotlib.pyplot as plt
import os

from functions_b__get_the_data_2023 import get_source_dataframe
from functions_d3__prepare_store_data_2023 import this_test_data

st.set_option('deprecation.showfileUploaderEncoding', False)

df, X_test, y_test, feature_names = None, None, None, None
rand_index = -1

DEFAULT_MODEL = 'Decision Tree'
DATA_VERSION = None
previous_data_version = DATA_VERSION

prediction_models = {
    'XG Boost (data version 11) - Best model': 'optimised_model_XG Boost (tree)_v11',
    'XG Boost (data version 10) - Good model': 'optimised_model_XG Boost (tree)_v10',
    'KNN (data version 6) - Fastest to train, Good model': 'optimised_model_KNN_v06',
    'Catboost (data version 6) - Good model': 'optimised_model_CatBoost_v06',
    #'Light Gradient Boosting (data version 6) - Good model': 'optimised_model_Light Gradient Boosting_v06',
    'Random Forests (data version 9) - Fair model': 'optimised_model_Random Forest_v09',
    #'Neural Network (data version 11) - Fair model': 'optimised_model_Neural Network_v11',
    'Neural Network (data version 6) - Fair model': 'neural network m11 mega (v06)_v06',
    'Neural Network (data version 11) - Fail model': 'neural network m15 mega + dropout (v11)_v06',
    'Neural Network (data version 11) - Bad model': 'neural network m15 mega + dropout (v11)_v11',
    'Linear Regression (data version 11) - Poor model': 'optimised_model_Linear Regression (Ridge)_v11',
    'Linear Regression (data version 6) - Poor model': 'optimised_model_Linear Regression (Ridge)_v06',
}


#    ' (data version )': '',


# optimised_model_CatBoost_v10(no dummies)


def main():
    global X_test, y_test, feature_names, rand_index, DATA_VERSION, previous_data_version
    fake_being_cloud_or_webapp_run = True

    st.markdown(
        "<h1 style='text-align: center; color: White;background-color:#e84343'>London Property Prices Predictor</h1>",
        unsafe_allow_html=True)
    st.markdown(
        "<h3 style='text-align: center; color: Black;'>Insert your property parameters here, or choose a random pre-existing property.</h3>",
        unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: Black;'>Sub heading here</h4>",
                unsafe_allow_html=True)

    st.sidebar.header("What is this Project about?")
    st.sidebar.markdown(
        "This is a Web app that would predict the price of a London property based on parameters.")
    st.sidebar.header("Sidebar Options")
    include_nulls = st.sidebar.checkbox('include rows with any nulls ')


    available_models = prediction_models.keys()

    selected_model_key = st.selectbox('Which model do you want to use?', available_models)
    selected_model = prediction_models[selected_model_key]


    model = load_model(selected_model)

    # manual_parameters = st.checkbox('Use manual parameters instead of sample')
    manual_parameters = False
    if not manual_parameters:
        test_size = len(y_test)

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

        print("")
        print("")
        print("")
        print("")
        print("")
        print("")
        print("inputs:", inputs)
        print("inputs:", len(inputs))
        print("inputs:", len(inputs[0]))

        # X_test, y_test, feature_names = functions_d3__prepare_store_data_2023.this_test_data(VERSION=version, test_data_only=True, cloud_or_webapp_run=False, versioned=True)
        #
        # y_pred = model.predict(X_test)
        # assert type(y_pred) == type(y_test)
        # assert len(y_pred) == len(y_test)

        model.summary()

        X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=False, versioned=True)
        fake_X = [[0]*len(X_test[0]),]
        print("fake_X", fake_X)
        print("X_test", X_test)
        result = model.predict(fake_X)
        result = model.predict(X_test)
        updated_res = result.flatten().astype(float)
        st.success('The predicted price for this property is £{:.0f}'.format(updated_res[0]))
        st.warning('The actual price for this property is £{:.0f}'.format(expected))

        fig, ax = plt.subplots()
        X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=False, versioned=True)
        y_pred = model.predict(X_test).flatten()
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
        acc = model.score(X_test, y_test)
        st.write('Accuracy of test set: ', acc)

        y_pred = model.predict(X_test).flatten()
        multiple_predictions = np.vstack((y_test.flatten(), y_pred)).T
        multiple_predictions_df = pd.DataFrame(multiple_predictions, columns=['Actual Price', 'Predicted Price'])

        st.write(multiple_predictions_df)
        print("type(multiple_predictions_df):", type(multiple_predictions_df))

    if not manual_parameters:
        if st.button('Get a different random property!'):
            rand_index, random_instance, random_instance[0] = randomise_property(DATA_VERSION, test_size)
            st.text(f'sample variables ({rand_index}): {random_instance[0]}')
            st.text(f'Expected prediction: {y_test[rand_index]}')

    if st.checkbox('Show the underlying dataframe'):
        DATA_VERSION = selected_model[-2:]
        df, df_type = get_source_dataframe(cloud_or_webapp_run=True, version=DATA_VERSION, folder_prefix='')
        print("claiming to be colab so I can use the cloud version of data and save space")
        st.write(df)


    if st.sidebar.button('Purge cache'):
        #st.sidebar.error("I haven't added this functionality yet")

        for deletable_file in [
            'train_test/X_test.csv', 'train_test/X_test_no_nulls.csv', 'train_test/_train.csv',
            'train_test/X_train_no_nulls.csv',
            'train_test/y_test.csv', 'train_test/y_test_no_nulls.csv', 'train_test/y_train.csv',
            'train_test/y_train_no_nulls.csv',
            'models_pretrained/model_Decision Tree.pkl',
            'models_pretrained/model_Deep Neural Network.pkl',
            'models_pretrained/model_HistGradientBoostingRegressor.pkl',
            'models_pretrained/model_Linear Regression.pkl',
            'models_pretrained/model_Linear Regression (Keras).pkl',
            'random_instance.csv',
            'random_instance_plus.csv',
            # functions.FINAL_RECENT_FILE,
            # functions.FINAL_RECENT_FILE_SAMPLE,
        ]:
            # checking if file exist or not
            if (os.path.isfile(deletable_file)):

                # os.remove() function to remove the file
                os.remove(deletable_file)

                # Printing the confirmation message of deletion
                print("File Deleted successfully:", deletable_file)
            else:
                print("File does not exist:", deletable_file)
            # Showing the message instead of throwing an error


def load_model(selected_model):
    global DATA_VERSION, X_test, y_test, feature_names, previous_data_version
    try:
        # model_path = f'models_pretrained/{selected_model}.pkl'
        # model = pickle.load(open(model_path, 'rb'))
        from functions_gh_presentation_and_launch import load_standard_model
        model = load_standard_model(selected_model=selected_model, model_type='neural' if 'eural' in selected_model else 'standard')
        DATA_VERSION = selected_model[-2:]
        if DATA_VERSION != previous_data_version:
            X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
            previous_data_version = DATA_VERSION
    except:
        # raise ValueError(f'failed to load model: {model_path}')
        raise ValueError(f'failed to load model: {selected_model}')
    return model


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
    np.savetxt("rand_index", [rand_index], delimiter=",")

    return rand_index, random_instance, random_instance[0]


if __name__ == '__main__':
    main()
