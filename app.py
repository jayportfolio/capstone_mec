import pandas as pd
import streamlit as st
import numpy as np
import random

from functions_b__get_the_data_2023 import get_source_dataframe
from functions_d3__prepare_store_data_2023 import this_test_data

st.set_option('deprecation.showfileUploaderEncoding', False)

df, X_test, y_test = None, None, None
rand_index = -1

DEFAULT_MODEL = 'Decision Tree'
DATA_VERSION = None
previous_data_version = DATA_VERSION

prediction_models = {
    'XG Boost (data version 11) - Best model': 'optimised_model_XG Boost (tree)_v11',
    'XG Boost (data version 9) - Good model': 'optimised_model_XG Boost (tree)_v10',
    'KNN (data version 6) - Fastest to train, Good model': 'optimised_model_KNN_v06',
    'Catboost (data version 6)': 'optimised_model_CatBoost_v06',
    'Light Gradient Boosting (data version 6) - Good model': 'optimised_model_Light Gradient Boosting_v06',
    'Random Forests (data version 9) - Fair model': 'optimised_model_Random Forest_v09',
    'Neural Network (data version 11) - Fair model': 'optimised_model_Neural Network_v11',
    'Linear Regression (data version 11) - Poor model': 'optimised_model_Linear Regression (Ridge)_v11',
    'Linear Regression (data version 6) - Poor model': 'optimised_model_Linear Regression (Ridge)_v06',
}
#    ' (data version )': '',


#optimised_model_CatBoost_v10(no dummies)


def main():
    global X_test, y_test, rand_index, DATA_VERSION, previous_data_version
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
    if st.sidebar.button('Purge everything'):
        st.sidebar.error("I haven't added this functionality yet")
        # importing the os Library
        import os

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
            # Showing the message instead of throwig an error

    available_models = prediction_models.keys()

    selected_model_key = st.selectbox('Which model do you want to use?', available_models)
    selected_model = prediction_models[selected_model_key]

    try:
        #model_path = f'models_pretrained/{selected_model}.pkl'
        #model = pickle.load(open(model_path, 'rb'))
        from functions_gh_presentation_and_launch import load_standard_model
        model = load_standard_model(selected_model=selected_model, model_type='neural' if 'eural' in selected_model else 'standard')
        DATA_VERSION = selected_model[-2:]
        if DATA_VERSION != previous_data_version:
            X_test, y_test = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
            previous_data_version = DATA_VERSION
    except:
        #raise ValueError(f'failed to load model: {model_path}')
        raise ValueError(f'failed to load model: {selected_model}')

    #manual_parameters = st.checkbox('Use manual parameters instead of sample')
    manual_parameters = False
    if not manual_parameters:

        test_size = len(y_test)

    else:
        lati = st.slider("Input Your latitude", 51.00, 52.00)
        longi = st.slider("Input your longitude", -0.5, 0.3)
        beds = st.slider("Input number of bedrooms", 0, 6)
        baths = st.slider("Input number of bathrooms", 0, 6)

        inputs = [[lati, longi, beds, baths]]

    if st.button('Predict',):

        if not manual_parameters:
            try:
                raise InterruptedError("don't ever do this actually")
                random_instance_plus = np.loadtxt("random_instance_plus.csv", delimiter=",")
                print(random_instance_plus)
                rand_index = int(random_instance_plus[0])
                print(rand_index)
                expected = random_instance_plus[1]
                print(expected)
                inputs = [random_instance_plus[2:]]
                print([random_instance_plus[2:]])
            except:
                rand_index = random.randint(0, test_size - 1)

                DATA_VERSION = selected_model[-2:]
                X_test, y_test = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)

                print("")
                print("")
                print("")
                print("")
                print("DATA_VERSION:", DATA_VERSION)
                print("X_test:", X_test[0:1])
                print("")
                print("")
                print("")

                previous_data_version = DATA_VERSION

                inputs = [X_test[rand_index]]
                random_instance = inputs
                expected = y_test[rand_index]
                np.savetxt("random_instance.csv", random_instance, delimiter=",")
                random_instance_plus = [rand_index, expected]
                random_instance_plus.extend(random_instance[0])
                np.savetxt("random_instance_plus.csv", random_instance_plus, delimiter=",")

            #st.text(f'Actual value of property {rand_index}: {expected}')

        print("inputs:", inputs)

        result = model.predict(inputs)
        updated_res = result.flatten().astype(float)
        st.success('The predicted price for this property is £ {:.2f}'.format(updated_res[0]))
        st.warning('The actual price for this property is £ {}'.format(expected))


    if st.checkbox('Get multiple predictions (entire test set)'):
        DATA_VERSION = selected_model[-2:]
        X_train, X_test, y_train, y_test = this_test_data(VERSION=DATA_VERSION, versioned=True)
        acc = model.score(X_test, y_test)
        st.write('Accuracy of test set: ', acc)

        multiple_predictions = np.vstack((y_test.flatten(), model.predict(X_test).flatten())).T
        multiple_predictions_df = pd.DataFrame(multiple_predictions, columns=['Actual Price','Predicted Price'])
        st.write(multiple_predictions_df)
        print(type(multiple_predictions_df ))

    if not manual_parameters:
        if st.button('Get a different random property!'):
            rand_index = random.randint(0, test_size - 1)
            X_test, y_test = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
            inputs = [X_test[rand_index]]

            random_instance = inputs
            np.savetxt("random_instance.csv", random_instance, delimiter=",")
            st.text(f'sample variables ({rand_index}): {inputs[0]}')
            st.text(f'Expected prediction: {y_test[rand_index]}')

            expected = y_test[rand_index]
            np.savetxt("random_instance.csv", random_instance, delimiter=",")
            random_instance_plus = [rand_index, expected]
            random_instance_plus.extend(random_instance[0])
            print("random_instance_plus:", random_instance_plus)
            np.savetxt("random_instance_plus.csv", [random_instance_plus], delimiter=",")

    if st.checkbox('Show the underlying dataframe'):
        DATA_VERSION = selected_model[-2:]
        df, df_type = get_source_dataframe(cloud_or_webapp_run=True, version=DATA_VERSION, folder_prefix='')
        print("claiming to be colab so I can use the cloud version of data and save space")
        st.write(df)


if __name__ == '__main__':
    main()
