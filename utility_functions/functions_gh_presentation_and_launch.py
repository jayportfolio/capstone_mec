import pickle
from tensorflow import keras
import pandas as pd

def main():
    keys = get_webapp_models()
    print(keys)
    print(keys.keys())

def get_webapp_model_names():
    webapp_models_path = "model_list/webapp_final_models"

#    dff = pd.read_json(prefix_dir_results_root + '/results.json')
    dff = pd.read_json('process/F_evaluate_model/results.json')

    models = {}

    from os import listdir
    from os.path import isfile, join
    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))] #os.path's isfile() can be used to only list files:
    onlyfiles = [f for f in listdir(webapp_models_path) if ('(v' in f and not isfile(join(webapp_models_path, f))) or '.pkl' in f]
    for i, each in zip(range(len(onlyfiles)), onlyfiles):
        try:
            print(f"{i+1}: {each}")
            key = each.replace('optimised_', '').replace('model_', '').replace('.pkl', '')\
                .replace('_v06', ' (v06)').replace('_v09', ' (v09)').replace('_v10', ' (v10)').replace('_v11', ' (v11)')\
                .replace('(v06)_v06', ' (v06)').replace('(v09)_v09', ' (v09)').replace('(v10)_v10', ' (v10)').replace('(v11)_v11', ' (v11)')\
                .replace('(v06) (v06)', ' (v06)').replace('(v09) (v09)', ' (v09)').replace('(v10) (v10)', ' (v10)').replace('(v11) (v11)', ' (v11)')\
                .replace('(no dummies)','') \
                .replace('(v10) (v10)','(v10)') \
                .replace('(v06) (v06)', ' (v06)').replace('(v09) (v09)', ' (v09)').replace('(v10) (v10)', ' (v10)').replace('(v11) (v11)', ' (v11)')\
                .replace('  ',' ')\
                .lower()
            print(f"      " + key)
            score = dff[[key]].loc["best score"].values[0]
            models[key] = score
        except KeyError as e:
            print('failed for:', i, each)
            print('failed for:', i, each)
            print(e)
    sorted_models = dict(sorted(models.items(), key=lambda item: item[1], reverse=True))
    print(sorted_models)
    print()

    return sorted_models.keys()


def get_webapp_models():
    webapp_models_path = "model_list/webapp_final_models"

    dff = pd.read_json('process/F_evaluate_model/results.json')

    model_names = {}
    models = {}

    from os import listdir
    from os.path import isfile, join
    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))] #os.path's isfile() can be used to only list files:
    onlyfiles = [f for f in listdir(webapp_models_path) if ('(v' in f and not isfile(join(webapp_models_path, f))) or '.pkl' in f]
    for i, each in zip(range(len(onlyfiles)), onlyfiles):
        try:
            print(f"{i+1}: {each}")
            key = each.replace('optimised_', '').replace('model_', '').replace('.pkl', '')\
                .replace('_v06', ' (v06)').replace('_v09', ' (v09)').replace('_v10', ' (v10)').replace('_v11', ' (v11)')\
                .replace('(v06)_v06', ' (v06)').replace('(v09)_v09', ' (v09)').replace('(v10)_v10', ' (v10)').replace('(v11)_v11', ' (v11)')\
                .replace('(v06) (v06)', ' (v06)').replace('(v09) (v09)', ' (v09)').replace('(v10) (v10)', ' (v10)').replace('(v11) (v11)', ' (v11)')\
                .replace('(no dummies)','') \
                .replace('(v10) (v10)','(v10)') \
                .replace('(v06) (v06)', ' (v06)').replace('(v09) (v09)', ' (v09)').replace('(v10) (v10)', ' (v10)').replace('(v11) (v11)', ' (v11)')\
                .replace('  ',' ')\
                .lower()
            print(f"      " + key)
            score = dff[[key]].loc["best score"].values[0]
            model_names[(key, each)] = score
        except KeyError as e:
            print('failed for:', i, each)
            print('failed for:', i, each)
            print(e)
    sorted_models = dict(sorted(model_names.items(), key=lambda item: item[1], reverse=True))
    print(sorted_models)

    for each in sorted_models.keys():
        models[each[0]] = each[1]
    print()

    return models




def load_model(selected_model, directory='./model_list/webapp_final_models', model_type='standard'):
    if model_type == 'standard':
        model_path = f'{directory}/{selected_model}.pkl'.replace('.pkl.pkl','.pkl')
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

if __name__ == '__main__':
    main()
