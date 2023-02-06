import pickle
from tensorflow import keras

def load_model(selected_model, directory='./models_pretrained', model_type='standard'):
    if model_type == 'standard':
        model_path = f'{directory}/{selected_model}.pkl'
        model = pickle.load(open(model_path, 'rb'))
    elif model_type== 'neural':
        # model = keras.models.load_model('models/NN')
        # model = keras.models.load_model(f'models/{selected_model}')
        full_path = f'{directory}/{selected_model}'
        model = keras.models.load_model(full_path)
        print("directory", directory)
        print("selected_model", selected_model)
        print("full_path", full_path)
        model.summary()
        #raise ValueError('breakpoint')
    else:
        raise ValueError('type: ' + model_type)

    return model

# def load_model_local(selected_model):
#     if selected_model == 'Stacked Model':
#         raise ValueError ('operate stacked model')
#     global DATA_VERSION, X_test, y_test, feature_names, previous_data_version
#     try:
#         # model_path = f'models_pretrained/{selected_model}.pkl'
#         # model = pickle.load(open(model_path, 'rb'))
#         from functions_gh_presentation_and_launch import load_standard_model
#         model = load_standard_model(selected_model=selected_model, model_type='neural' if 'eural' in selected_model else 'standard')
#         DATA_VERSION = selected_model[-2:]
#         if DATA_VERSION != previous_data_version:
#             X_test, y_test, feature_names = this_test_data(VERSION=DATA_VERSION, test_data_only=True, cloud_or_webapp_run=True, versioned=True)
#             previous_data_version = DATA_VERSION
#     except:
#         # raise ValueError(f'failed to load model: {model_path}')
#         raise ValueError(f'failed to load model: {selected_model}')
#     return model
#
# def load_model_remote(selected_model, directory='./models_pretrained', model_type='standard'):
#     if model_type == 'standard':
#         model_path = f'{directory}/{selected_model}.pkl'
#         model = pickle.load(open(model_path, 'rb'))
#     elif model_type== 'neural':
#         # model = keras.models.load_model('models/NN')
#         # model = keras.models.load_model(f'models/{selected_model}')
#         full_path = f'{directory}/{selected_model}'
#         model = keras.models.load_model(full_path)
#         print("directory", directory)
#         print("selected_model", selected_model)
#         print("full_path", full_path)
#         model.summary()
#         #raise ValueError('breakpoint')
#     else:
#         raise ValueError('type: ' + model_type)
#
#
#     return model
#
