import pickle
from tensorflow import keras


def load_standard_model(selected_model, directory='./models_pretrained', model_type='standard'):
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

