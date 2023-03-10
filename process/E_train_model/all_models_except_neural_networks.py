#!/usr/bin/env python
# coding: utf-8


# 
# ## Stage: Decide which algorithm and version of the data we are going to use for model training
# 
# Additionally, choose:
# * if we'll skip scaling the data
# * if we'll use full categories instead of dummies
# * what fraction of the data we'll use for testing (0.1)
# * if the data split will be randomised (it won't!)

import os

import pandas as pd
from pandas import DataFrame
import numpy as np
import seaborn as sns
import pickle
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler

import sys
# import ast
import math
from time import time
import json
from datetime import datetime
from termcolor import colored
import argparse

FILENAME = 'all_models_except_neural_networks'

import sys
import subprocess
import pkg_resources

warnings = []

required = {'tabulate', 'tabulate'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    warning_message = 'Had to install missing packages:' + str(missing)
    print(warning_message)
    warnings.append(warning_message)
    

def get_commandline_or_userinput(user_params, user_question, which_arg):
    userparam_choices = list(user_params.values())
    if which_arg:
        try:
            user_choice = user_params[which_arg]
        except KeyError:
            print(f"{which_arg} is an invalid choice, asking for a choice instead...")
            user_choice = get_user_input(user_question, userparam_choices)
            print(user_choice)
    else:
        user_choice = get_user_input(user_question, userparam_choices)
    return user_choice


def get_user_input(user_question, userparam_choices):
    print("\n")
    for sugg_index, suggestion in zip(range(len(userparam_choices)), userparam_choices):
        print(f"{sugg_index + 1}: {suggestion}")
    user_response = input(f"\n{user_question}  ")
    try:
        user_choice = int(user_response) - 1
        if user_choice < 0 or user_choice > len(userparam_choices) - 1: raise ValueError()
        user_choice = userparam_choices[user_choice]
    except ValueError:
        user_choice = userparam_choices[0]
        print(f"No valid choice made, using default: {user_choice}\n")
    return user_choice

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                    help='an integer for the accumulator')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                    const=sum, default=max,
    #                    help='sum the integers (default: find the max)')
    parser.add_argument("--verbose", help="increase output verbosity")
    parser.add_argument("--model", help="choose your model [lr,knn,dt,rf,xgb,cat,lgb,stacked]")
    parser.add_argument("--detail", help="search type [random,best,custom,grid]")
    parser.add_argument("--version", help="dataset version [06,09,10,11]. Later datasets include more features.")
    args = parser.parse_args()

    # args = parser.parse_args()
    # print(args.accumulate(args.integers))
    if args.verbose:
        print("verbosity turned on")
        debug_mode = True

    algorithm_choices_dict = {
        'lr': 'Linear Regression (Ridge)',
        'knn': 'KNN',
        'dt': 'Decision Tree',
        'rf': 'Random Forest',
        'xgb': 'XG Boost (tree)',
        'cat': 'CatBoost',
        'lgb': 'Light Gradient Boosting',
        'stacked': 'Stacked Model'
    }
    algorithm_detail_dict = {
        'random': 'random search', 'best': 'rerun best', 'custom': 'custom', 'grid': 'grid'
    }
    version_choices_dict = {'11': '11', '10': '10', '09': '09', '06': '06'}

    question = "Which algorithm do you want to use to train the model?"
    ALGORITHM = get_commandline_or_userinput(algorithm_choices_dict, question, args.model)

    question = "Which algorithm search method do you want?"
    ALGORITHM_DETAIL = get_commandline_or_userinput(algorithm_detail_dict, question, args.detail)

    question = "Which dataset version do you want?"
    VERSION = get_commandline_or_userinput(version_choices_dict, question, args.version)

    if 'catboost' in ALGORITHM.lower() or 'lightgbm' in ALGORITHM.lower():
        required = {'lightgbm', 'catboost'}
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed

        if missing:
            python = sys.executable
            subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
            warning_message = 'Had to install missing packages:' + str(missing)
            print(warning_message)
            warnings.append(warning_message)
    #else:
    #    print(ALGORITHM)
    #    print('quitting')
    #    quit()

    # DATA_DETAIL = ['no scale','no dummies']
    # DATA_DETAIL = ['explore param']
    DATA_DETAIL = ['no dummies'] if 'catboost' in ALGORITHM.lower() else []

    RANDOM_STATE = 101
    TRAINING_SIZE = 0.9

    CROSS_VALIDATION_SCORING = 'r2'

    print(f'ALGORITHM: {ALGORITHM}')
    print(f'ALGORITHM_DETAIL: {ALGORITHM_DETAIL}')
    print(f'DATA VERSION: {VERSION}')
    print(f'DATA_DETAIL: {DATA_DETAIL}')

    model_uses_feature_importances = 'tree' in ALGORITHM.lower() or 'forest' in ALGORITHM.lower() or 'boost' in ALGORITHM.lower()
    create_python_script = True

    prefix_dir_envs = './process/z_envs/'
    prefix_dir_hyperparameters = './'
    prefix_dir_results = './process/F_evaluate_model/'
    prefix_dir_optimised_models = './model_list/initial_trained_models/'
    prefix_functions_root = os.path.join('.')
    prefix_dir_results_root = './process/F_evaluate_model'
    prefix_dir_results_root2 = './process/F_evaluate_model/'

    start_timestamp = datetime.now()

    module_path = os.path.abspath(prefix_functions_root)
    if module_path not in sys.path:
        # sys.path.append(module_path+"\\zfunctions")
        sys.path.append(module_path)

    with open(prefix_dir_envs + '_envs.json') as f:
        env_vars = json.loads(f.read())

    try:
        import google.colab

        run_env = 'colab'
    except:
        try:
            run_env = env_vars['notebook_environment']
        except:
            run_env = 'unknown'

    if "JPY_PARENT_PID" in os.environ:
        is_jupyter = True
    else:
        is_jupyter = False

    use_gpu = env_vars.get('use_gpu', False)
    debug_mode = env_vars.get('debug_mode', False)
    quick_mode = env_vars.get('quick_mode', False)
    OVERRIDE_CV = env_vars.get('quick_override_cv_splits', None) if quick_mode else None
    OVERRIDE_N_ITER = env_vars.get('quick_override_n_iter', None) if quick_mode else None
    OVERRIDE_JOBS = env_vars.get('quick_override_n_jobs', None) if quick_mode else None
    OVERRIDE_VERBOSE = 1
    # if quick_mode:OVERRIDE_CV, OVERRIDE_N_ITER = 2, 10

    already_timed = False
    no_dummies = 'no dummies' in DATA_DETAIL
    no_scaling = 'no scaling' in DATA_DETAIL
    # not_catboost = 'catboost' not in ALGORITHM.lower() or not no_dummies
    using_catboost = 'catboost' in ALGORITHM.lower()

    if run_env not in ['colab', 'gradient', 'cloud']:
        cloud_run = False
        from utility_functions.functions_b__get_the_data import set_csv_directory

        set_csv_directory('final_split')
    else:
        cloud_run = True

    from utility_functions.functions_0__common import get_columns
    from utility_functions.functions_b__get_the_data import get_combined_dataset, get_source_dataframe
    from utility_functions.functions_d1__prepare_cleanse_data import tidy_dataset
    from utility_functions.functions_d2__transform_enrich_data import preprocess, feature_engineer
    from utility_functions.functions_d3__prepare_store_data import create_train_test_data
    from utility_functions.functions_e__train_model import get_chosen_model, make_modelling_pipeline, get_cv_params, fit_model_with_cross_validation, get_hyperparameters
    from utility_functions.functions_f_evaluate_model import get_best_estimator_average_time, get_results, update_results, include_in_html_report

    print(env_vars)

    # #### Include any overrides specific to the algorthm / python environment being used

    running_locally = run_env == 'local'

    if 'forest' in ALGORITHM.lower():
        # OVERRIDE_N_ITER = 5
        OVERRIDE_N_ITER = 50
        if use_gpu:
            # OVERRIDE_JOBS = 8
            OVERRIDE_JOBS = 4

    if running_locally:
        if ALGORITHM.lower() in ['random forest', 'xg boost', 'xg boost (linear)', 'xg boost (tree)']:
            OVERRIDE_N_ITER = 3
        elif 'linear regression' in ALGORITHM.lower():
            OVERRIDE_N_ITER = 4  # 15
        elif 'stacked model [knn,lgb,xgb]' in ALGORITHM.lower():
            OVERRIDE_N_ITER = 1
            OVERRIDE_CV = 2
        else:
            OVERRIDE_N_ITER = 5

    if ALGORITHM.lower() in ['xg boost', 'xg boost (linear)', 'xg boost (tree)']:
        OVERRIDE_N_ITER = 20

    if 'forest' in ALGORITHM.lower() or True:
        OVERRIDE_VERBOSE = 2


    #
    # ## Stage: defining the model pipeline
    #
    #


    def make_pipeline():
        return Pipeline([
            # ('mms', MinMaxScaler()),
            ('std_scaler', StandardScaler()),
            ('model', get_chosen_model(ALGORITHM))
        ])


    starter_pipe = make_pipeline()
    starter_pipe

    #
    # ## Stage: get the data

    columns, booleans, floats, categories, custom, wildcard = get_columns(version=VERSION)
    LABEL = 'Price'

    # df, retrieval_type = get_source_dataframe(cloud_run, VERSION, folder_prefix='../../../', row_limit=None)
    df, retrieval_type = get_source_dataframe(cloud_run, VERSION, folder_prefix='./', row_limit=None)
    df_orig = df.copy()

    if retrieval_type != 'tidy':
        df = tidy_dataset(df, version=int(VERSION))
        df = feature_engineer(df, version=int(VERSION))

        df = df[columns]

    print(colored(f"features", "blue"), "-> ", columns)
    columns.insert(0, LABEL)
    print(colored(f"label", "green", None, ['bold']), "-> ", LABEL)

    df = preprocess(df, version=VERSION)
    df = df.dropna()

    df.head(5)

    X_train, X_test, y_train, y_test, X_train_index, X_test_index, y_train_index, y_test_index, df_features, df_labels = create_train_test_data(
        df,
        categories=categories,
        RANDOM_STATE=RANDOM_STATE, return_index=True,
        drop_nulls=True,
        no_dummies=no_dummies
    )

    if 'forest' in ALGORITHM.lower() or ALGORITHM.lower() == 'light gradient boosting':
        y_train_orig = y_train
        y_train = y_train.ravel()

    # print(X_train[0])
    print(df.shape)
    print(X_train.shape, X_test.shape, y_train.shape, y_test.shape, X_train_index.shape, X_test_index.shape,
          y_train_index.shape, y_test_index.shape)

    # imputer = SimpleImputer(strategy='mean')
    # imputer.fit(X_train[6])
    # X_train[6] = imputer.transform(X_train[6])


    starter_model = starter_pipe[-1]

    #
    # ## Stage:
    # * #### retrieve the hyperparameters for this model, and
    # * #### train the model
    #
    #
    options_block, new_warnings = get_hyperparameters(ALGORITHM, use_gpu, prefix=prefix_dir_hyperparameters, version=VERSION, api_version=2)
    if new_warnings:
        warnings.extend(new_warnings)

    if 'explore param' in DATA_DETAIL:
        def automl_step(param_options, vary):
            for key2, value in param_options.items():
                # print(key2, value, vary)
                if key2 != vary and key2 != 'model__' + vary:
                    try:
                        param_options[key2] = [param_options[key2][0]]
                    except:
                        # value probably wasn't an list of options
                        param_options[key2] = [param_options[key2]]
            return param_options


        # options_block = automl_step(options_block, "model__epochs")
        explore_param = "n_estimators"
        options_block = automl_step(options_block, explore_param)

        ALGORITHM_DETAIL = 'grid search (implied)'

    # OVERRIDE_N_ITER = 15

    param_options, cv, n_jobs, refit, n_iter, verbose = get_cv_params(options_block, debug_mode=debug_mode,
                                                                      override_cv=OVERRIDE_CV,
                                                                      override_niter=OVERRIDE_N_ITER,
                                                                      override_njobs=OVERRIDE_JOBS,
                                                                      override_verbose=OVERRIDE_VERBOSE
                                                                      )

    print("cv:", cv, "n_jobs:", n_jobs, "refit:", refit, "n_iter:", n_iter, "verbose:", verbose)
    # print('\n\nHyperparameters:')
    # param_options if not using_catboost else options_block


    key = f'{ALGORITHM} (v{VERSION})'.lower()


    def fit_model_with_cross_validation(gs, X_train, y_train, fits):
        pipe_start = time()
        cv_result = gs.fit(X_train, y_train)
        gs.fit(X_train, y_train)
        pipe_end = time()
        average_time = round((pipe_end - pipe_start) / (fits), 2)

        print(f"Total fit/CV time      : {int(pipe_end - pipe_start)} seconds   ({pipe_start} ==> {pipe_end})")
        print()
        print(
            f'average fit/score time = {round(cv_result.cv_results_["mean_fit_time"].mean(), 2)}s/{round(cv_result.cv_results_["mean_score_time"].mean(), 2)}s')
        print(
            f'max fit/score time     = {round(cv_result.cv_results_["mean_fit_time"].max(), 2)}s/{round(cv_result.cv_results_["mean_score_time"].max(), 2)}s')
        print(f'refit time             = {round(cv_result.refit_time_, 2)}s')

        # return cv_result, average_time, cv_result.refit_time_, len(cv_result.cv_results_["mean_fit_time"])
        return average_time, cv_result.refit_time_, len(cv_result.cv_results_["mean_fit_time"])


    if not using_catboost:
        if ALGORITHM_DETAIL == 'grid search' or ALGORITHM_DETAIL == 'grid search (implied)':
            print('grid search (or implied)')
            crossval_runner = GridSearchCV(
                estimator=starter_pipe,
                param_grid=param_options,
                cv=cv, n_jobs=n_jobs,  # get the AVX/AVX2 info if use n_jobs > 2
                verbose=verbose, scoring=CROSS_VALIDATION_SCORING,
                refit=refit,
                return_train_score=True,  # n_iter=n_iter,
                # error_score='raise'
            )
        elif ALGORITHM_DETAIL == 'custom':
            user_defined_params = {'model__booster': 'dart',
                                   'model__colsample_bytree': 0.9,
                                   'model__lambda': 1,
                                   'model__learning_rate': 0.1,
                                   'model__max_depth': [20, 25],  # [15,20,30],
                                   'model__max_features': None,
                                   'model__max_leaf_nodes': 20,
                                   'model__max_samples': 1,
                                   'model__min_sample_split': None,
                                   'model__min_samples_leaf': 2000,
                                   'model__n_estimators': [50, 75],  # [50,100,150],
                                   'model__n_jobs': 3,
                                   'model__objective':
                                       'reg:squarederror',
                                   'model__subsample': 0.5,
                                   'model__tree_method': 'hist',
                                   'model__verbosity': 2,
                                   # 'score': 0.727131957076238, 'time': 134.17490124702454, 'date run': '2022-12-07 09:43:37.103009', 'method': 'random search'
                                   }

            for each in user_defined_params:
                if type(user_defined_params[each]) != list:
                    user_defined_params[each] = [user_defined_params[each]]

            print('user_defined_params:', user_defined_params)

            crossval_runner = GridSearchCV(
                estimator=starter_pipe,
                # param_grid=params_for_best_results,
                param_grid=user_defined_params,
                cv=cv, n_jobs=n_jobs,  # get the AVX/AVX2 info if use n_jobs > 2
                verbose=verbose, scoring=CROSS_VALIDATION_SCORING,
                refit=refit,
                return_train_score=True,  # n_iter=n_iter,
                # error_score='raise'
            )

        elif ALGORITHM_DETAIL == 'rerun best':
            results_for_best_results = get_results(directory=prefix_dir_results_root2)
            model_for_best_results = results_for_best_results[key]

            params_for_best_results = model_for_best_results['best params']
            method_for_best_results = model_for_best_results['best method']

            print(method_for_best_results)
            print(DATA_DETAIL)

            if 'pca' in method_for_best_results and 'pca' not in DATA_DETAIL:
                raise ValueError("can't rerun this here, pca encoding was used")

            for each in params_for_best_results:
                if type(params_for_best_results[each]) != list:
                    params_for_best_results[each] = [params_for_best_results[each]]

            crossval_runner = GridSearchCV(
                estimator=starter_pipe,
                # param_grid=params_for_best_results,
                param_grid=params_for_best_results,
                cv=cv, n_jobs=n_jobs,  # get the AVX/AVX2 info if use n_jobs > 2
                verbose=verbose, scoring=CROSS_VALIDATION_SCORING,
                refit=refit,
                return_train_score=True,  # n_iter=n_iter,
                # error_score='raise'
            )

        else:
            print('random search')
            crossval_runner = RandomizedSearchCV(
                estimator=starter_pipe,
                param_distributions=param_options,
                cv=cv, n_jobs=n_jobs,  # get the AVX/AVX2 info if use n_jobs > 2
                verbose=verbose, scoring=CROSS_VALIDATION_SCORING,
                refit=refit,
                return_train_score=True,  # n_iter=n_iter,
                n_iter=n_iter,  # 1, #3
                # error_score='raise'
            )
        cv_average_fit_time, cv_best_model_fit_time, total_fits = fit_model_with_cross_validation(
            crossval_runner, X_train, y_train, fits=cv * n_iter)

    else:
        from catboost import CatBoostRegressor, Pool

        # pool = Pool(df, cat_features=['tenure.tenureType'], label=df['Price'].values)
        pool_Xtrain = Pool(X_train, cat_features=[7], label=y_train)
        # pool_Xtest = Pool(X_train, cat_features=[7], label=y_train)
        pool_Xtest = Pool(X_test, cat_features=[7], label=y_test)

        starter_model = model = CatBoostRegressor(iterations=3, depth=3, learning_rate=0.1, loss_function='RMSE', objective='RMSE')

        output = starter_model.randomized_search(options_block,  # param_options,
                                                 X=pool_Xtrain,  # X_train,
                                                 # y=y_train,
                                                 # cat_features=[],
                                                 cv=5,
                                                 n_iter=100,
                                                 partition_random_seed=101,
                                                 calc_cv_statistics=True,
                                                 # search_by_train_test_split=True,
                                                 refit=True,
                                                 shuffle=True,
                                                 stratified=None,
                                                 # train_size=0.8,
                                                 # train_size=1,
                                                 verbose=True,
                                                 plot=True,
                                                 log_cout=sys.stdout,
                                                 log_cerr=sys.stderr)

        cat_params, cat_cv_results = output['params'], output['cv_results']
        crossval_runner = {"best_params_": cat_params, "cv_results_": cat_cv_results, "best_estimator_": None}
    crossval_runner

    if ALGORITHM_DETAIL == 'grid search' or ALGORITHM_DETAIL == 'grid search (implied)':
        print(crossval_runner.best_params_)

    #
    # ## Stage: Get the results and print some graphs
    #
    #

    if not using_catboost:
        best_estimator_pipe = crossval_runner.best_estimator_
        cv_results_df = pd.DataFrame(crossval_runner.cv_results_).sort_values('rank_test_score')

        print("Best Params\n", crossval_runner.best_params_, "\n---------------------")

        if debug_mode:
            print("CV results\n", crossval_runner.cv_results_, "\n---------------------")
            # print("Best Params\n",crossval_runner["best_params_"], "\n---------------------")

    else:
        print(cat_params)
        print(cat_cv_results)

    if not using_catboost:
        cv_results_df['params2'] = cv_results_df['params'].apply(lambda l: '/'.join([str(c) for c in l.values()]))

        cv_columns = ['params2', 'rank_test_score', 'mean_test_score', 'mean_fit_time', 'mean_score_time', 'params']
        # if 'Neural' not in ALGORITHM:
        #     cv_columns.insert(2, 'mean_train_score')
        cv_results_df_full_sorted = cv_results_df.sort_values('rank_test_score')[cv_columns].reset_index(drop=True)

        cv_results_df_sorted = cv_results_df_full_sorted[cv_results_df_full_sorted['mean_test_score'] > -2]
        if len(cv_results_df_sorted) != len(cv_results_df_full_sorted):
            print(-len(cv_results_df_sorted) + len(cv_results_df_full_sorted), "fits were total failures")
            total_fits = len(cv_results_df_sorted)

    if not using_catboost:

        orig_debug_mode, orig_display_df_cols = debug_mode, pd.get_option('display.max_columns')
        debug_mode = True
        pd.set_option('display.max_columns', None)
        if debug_mode:
            debug_cols = ['rank_test_score', 'mean_test_score', 'mean_fit_time', 'mean_score_time']
            debug_cols.extend([c for c in cv_results_df.columns if 'param' in c and c != 'params'])

        cv_results_df_summary = cv_results_df[debug_cols].head(17)
        cv_results_df_summary.set_index('rank_test_score', inplace=True)

    #
    # #### Mini Stage: Make predictions
    #
    #

    if not using_catboost:
        y_pred = best_estimator_pipe.predict(X_test)
    else:
        y_pred = starter_model.predict(pool_Xtest)

    y_pred = y_pred.reshape((-1, 1))

    R2 = r2_score(y_test, y_pred)
    MAE = mean_absolute_error(y_test, y_pred)
    MSE = mean_squared_error(y_test, y_pred)
    RMSE = math.sqrt(MSE)
    print('-' * 10 + ALGORITHM + '-' * 10)
    print('R square Accuracy', R2)
    print('Mean Absolute Error Accuracy', MAE)
    print('Mean Squared Error Accuracy', MSE)
    print('Root Mean Squared Error', RMSE)

    compare = np.hstack((y_test_index, y_test, y_pred))
    compare_df = DataFrame(compare, columns=['reference', 'actual', 'predicted'])
    compare_df['difference'] = abs(compare_df['actual'] - compare_df['predicted'])
    compare_df['diff 1 %'] = abs((compare_df['actual'] - compare_df['predicted']) / compare_df['actual'] * 100)
    compare_df['diff 2 %'] = abs((compare_df['actual'] - compare_df['predicted']) / compare_df['predicted']) * 100
    compare_df['reference'] = compare_df['reference'].astype(int)
    compare_df.set_index('reference', inplace=True)

    combined = compare_df.merge(df[columns], how='inner', left_index=True, right_index=True).sort_values(['diff 1 %'],
                                                                                                         ascending=False)
    # pd.options.display.float_format = '{:.4f}'.format
    combined[['predicted', 'actual', 'Price', 'bedrooms', 'bathrooms']] = combined[
        ['predicted', 'actual', 'Price', 'bedrooms', 'bathrooms']].astype(int)
    combined['bedrooms'] = combined['bedrooms'].astype(int)
    combined

    best_model_fig, best_model_ax = plt.subplots()
    best_model_ax.scatter(y_test, y_pred, edgecolors=(0, 0, 1))
    best_model_ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=3)
    best_model_ax.set_ylabel('Predicted')
    best_model_ax.set_xlabel('Actual')
    # ax.title.set_text(f'CV Chosen best option ({calculated_best_pipe[1]})')

    plt.show()

    if not using_catboost:
        def custom_model_and_predictions(model, graph_params, X_train, y_train, X_test):
            graph_model = model
            graph_model.set_params(**graph_params)
            graph_model.fit(X_train, y_train)
            y_pred_graph = model.predict(X_test)

            return model, y_pred_graph


        best_model_count = 10 if not quick_mode else 2
        best_model_count = 3 if not quick_mode else 1
        best_models = {}
        best_model_predictions = {}
        best_model_scores = {}

        showable_increment = total_fits // (4 if not quick_mode else 2)
        if showable_increment == 0: showable_increment = 1
        evolution_of_models_range = list(range(0, total_fits, showable_increment))
        evolution_of_models_range.append(-1)

        for i in evolution_of_models_range:
            if debug_mode: print(f'{i} ==> {i}')
            if i + 1 == len(cv_results_df_sorted):
                pass  # don't do the worst twice

            if i == 0:
                fitted_graph_model = crossval_runner.best_estimator_
                y_pred_graph = y_pred
            else:
                index = i if i >= 0 else total_fits - 1

                try:
                    # graph_pipe_params = cv_results_df_sorted['params'][total_fits - 1]
                    graph_pipe_params = cv_results_df_sorted['params'][index]
                except:
                    if i == -1:
                        print("MAJOR ERROR? couldn't get cv_results_df_sorted, using whatever the best cv_results_df_full_sorted was instead")
                        graph_pipe_params = cv_results_df_full_sorted['params'][0]
                    else:
                        raise IndexError('could not complete graph for index ' + str(i))

                print(graph_pipe_params)
                # would always return the best! graph_pipe_params = cv_results_df_sorted.loc[cv_results_df_sorted['rank_test_score'] == 1, 'params'].values[0]

                graph_params = {}
                for key2, value in graph_pipe_params.items():
                    graph_params[key2.replace('model__', '')] = value

                fitted_graph_model, y_pred_graph = custom_model_and_predictions(make_pipeline(), graph_pipe_params, X_train,
                                                                                y_train, X_test)

            best_models[i] = fitted_graph_model[-1].get_params()
            best_model_predictions[i] = y_pred_graph
            best_model_scores[i] = fitted_graph_model.score(X_test, y_test)

        # # if debug_mode: print(f'{-1} ==> {-1}')
        # # try:
        # #     graph_pipe_params = cv_results_df_sorted['params'][total_fits - 1]
        # # except:
        # #     print("MAJOR ERROR? couldn't get cv_results_df_sorted, using cv_results_df_full_sorted instead")
        # #     graph_pipe_params = cv_results_df_full_sorted['params'][0]
        #
        # print(graph_pipe_params)
        # graph_params = {}
        # for key2, value in graph_pipe_params.items():
        #     graph_params[key2.replace('model__', '')] = value
        # fitted_graph_model, y_pred_graph = custom_model_and_predictions(make_pipeline(), graph_pipe_params, X_train,
        #                                                                 y_train, X_test)
        # best_models[-1] = fitted_graph_model[-1].get_params()
        # best_model_predictions[-1] = y_pred_graph
        # best_model_scores[-1] = fitted_graph_model.score(X_test, y_test)

    if not using_catboost:
        evolution_of_models_fig, evolution_of_models_axes = plt.subplots(nrows=len(best_model_scores.keys()), figsize=(15, 45))

        ax_index = -1
        # for i in best_model_scores.keys():
        for i, ax_index in zip(best_model_scores.keys(), range(0, len(best_model_scores.keys()))):
            # ax_index += 1
            # print(len(best_model_scores.keys()))
            # print('i',i, "ax_index",ax_index)
            if i >= 0:
                # plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=3)
                # plt.scatter(y_test, best_model_predictions[i])
                # # plt.title(str(i) + " " + str(round(best_model_scores[i], 4)) + " for " + str(best_models[i]))
                # if len(best_models[i].keys()) < 30:
                #     plt.title(str(i) + " " + str(round(best_model_scores[i], 4)) + " for " + str(best_models[i]))
                # else:
                #     plt.title(str(i) + " " + str(round(best_model_scores[i], 4)) + " for entry " + str(i))
                # plt.show()

                # >>>

                plt.subplots_adjust(hspace=0.2)
                plt.subplots_adjust(wspace=0.2)

                # .flatten()
                # coordinates = evolution_of_models_axes[i]

                if len(best_models[i].keys()) < 30:
                    eom_title = str(i) + " " + str(round(best_model_scores[i], 4)) + " for " + str(best_models[i])
                else:
                    eom_title = str(i) + " " + str(round(best_model_scores[i], 4)) + " for entry " + str(i)

                print(ax_index)
                sns.lineplot(x=[y_test.min(), y_test.max()], y=[y_test.min(), y_test.max()], ax=evolution_of_models_axes[ax_index], color='red')
                sns.scatterplot(x=y_test.flatten(), y=best_model_predictions[0].flatten(), ax=evolution_of_models_axes[ax_index],
                                s=100).set(title=eom_title)

                # <<<

        # plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=3)
        # plt.scatter(y_test, best_model_predictions[-1])

        if len(best_models[i].keys()) < 30:
            eom_title = str(i) + " " + str(round(best_model_scores[-1], 4)) + " for (worst)" + str(best_models[-1])
        else:
            eom_title = str(i) + " " + str(round(best_model_scores[-1], 4)) + " for (worst) entry " + str(i)

        print(ax_index)
        sns.lineplot(x=[y_test.min(), y_test.max()], y=[y_test.min(), y_test.max()], ax=evolution_of_models_axes[ax_index], color='red')
        sns.scatterplot(x=y_test.flatten(), y=best_model_predictions[-1].flatten(), ax=evolution_of_models_axes[ax_index],
                        s=100).set(title=eom_title)

        plt.show()

    if not using_catboost:
        sns.set_theme(font_scale=2, rc=None)
        sns.set_theme(font_scale=1, rc=None)

        worst_and_best_model_fig, axes = plt.subplots(ncols=3, figsize=(15, 5))

        plt.subplots_adjust(hspace=0.2)
        plt.subplots_adjust(wspace=0.2)

        # .flatten()
        coordinates = axes[0]
        sns.lineplot(x=[y_test.min(), y_test.max()], y=[y_test.min(), y_test.max()], ax=axes[0], color='red')
        sns.scatterplot(x=y_test.flatten(), y=best_model_predictions[0].flatten(), ax=axes[0],
                        s=100).set(title=f'"BEST" model')

        sns.lineplot(x=[y_test.min(), y_test.max()], y=[y_test.min(), y_test.max()], ax=axes[1], color='red')
        sns.scatterplot(x=y_test.flatten(), y=best_model_predictions[-1].flatten(), ax=axes[1],
                        s=100).set(title=f'"WORST" model')

        sns.lineplot(x=[y_test.min(), y_test.max()], y=[y_test.min(), y_test.max()], ax=axes[2], color='red')
        sns.scatterplot(x=y_test.flatten(), y=best_model_predictions[-1].flatten(), ax=axes[2],
                        s=120, color='orange')
        sns.scatterplot(x=y_test.flatten(), y=best_model_predictions[0].flatten(), ax=axes[2],
                        s=30, alpha=0.6, color='black').set(
            title='best (black) vs worst (orange)')
        # title='best (orange) vs worst (black)')

        worst_and_best_model_fig.tight_layout()
        plt.show()

    #
    # ## Stage: Evaluate the model
    #
    #

    # <catboost.core.CatBoostRegressor object at 0x7fb167387490>
    # {'depth': 6}
    # defaultdict(<class 'list'>, {'iterations': [0, 1, 2],
    # 'test-RMSE-mean': [396884.9605444017, 359548.6632536235, 326027.84885587444],
    # 'test-RMSE-std': [308.9495320039113, 260.0967808594464, 219.65856329246023],
    # 'train-RMSE-mean': [396884.77936957515, 359542.3612912551, 326018.9404460669],
    # 'train-RMSE-std': [91.44140078375503, 86.77961380623475, 69.4038638987425]})

    cv_best_model_fit_time = cv_best_model_fit_time if not using_catboost else 999

    DD2 = "(" + ",".join(DATA_DETAIL) + ")" if len(DATA_DETAIL) >= 1 else ""

    method = f"{ALGORITHM_DETAIL}{DD2}"
    if method == 'rerun best':
        print("method:", method)
        method += ": " + method_for_best_results
        print("method:", method)
        method = method.replace('rerun best: rerun best: ', 'rerun best: ')
        print("method:", method)

    new_results = {
        '_score': R2,
        'R square Accuracy': R2,
        'Mean Absolute Error Accuracy': MAE,
        'Mean Squared Error Accuracy': MSE,
        'Root Mean Squared Error': RMSE,
        '_train time': cv_best_model_fit_time,
        'random_state': RANDOM_STATE,
        'date': str(datetime.now()),
        '_params': crossval_runner.best_params_ if not using_catboost else cat_params,
        '_method': method,
        'run_env': run_env
    }

    if run_env not in ['colab']:
        old_results_json = get_results(directory=prefix_dir_results_root2)
        try:
            old_best_score = old_results_json[key]['best score']
        except:
            print(f"haven't scored this model yet: {ALGORITHM}")
            old_best_score = -999
        this_model_is_best = update_results(old_results_json, new_results, key, directory=prefix_dir_results)

    print(key)
    new_results

    crossval_runner.best_estimator_ if not using_catboost else ''

    if this_model_is_best:
        with open(prefix_dir_optimised_models + f'optimised_model_{ALGORITHM}_v{VERSION}{DD2}.pkl', 'wb') as f:
            if not using_catboost:
                pickle.dump(crossval_runner.best_estimator_, f)
            else:
                pickle.dump(starter_model, f)
            new_model_decision = f"pickled new version of model\n{old_results_json[key]['_score']} is new best score (it's better than {old_best_score})"
            # print(results_json[key]['_score'], 'is an improvement on', results_json[key]['second best score'])
    else:
        new_model_decision = f"not updated saved model, the previous run was better\n{old_results_json[key]['_score']} is worse than or equal to {old_best_score}"

    print(new_model_decision)

    #
    # ## Stage: Investigate the feature importances (if applicable)
    #

    if model_uses_feature_importances:
        feature_importances = crossval_runner.best_estimator_[-1].feature_importances_ if not using_catboost else starter_model.get_feature_importance()
        # std = np.std([tree.feature_importances_ for tree in model.estimators_], axis = 0)

        indices = np.argsort(feature_importances)[::-1]

        print('Feature Ranking:')

        feature_importances_output = ""
        for f in range(X_train.shape[1]):
            # print('%d. features %d (%f)' % (f + 1, indices[f], feature_importances[indices[f]]), df_features.columns[indices[f] + 1])
            feature_importances_output += ('%d. features %d (%f)' % (f + 1, indices[f], feature_importances[indices[f]]))
            feature_importances_output += '\t\t'
            feature_importances_output += (df_features.columns[indices[f] + 1])
            feature_importances_output += '\n'
        print(feature_importances_output)
    else:
        print(f'{ALGORITHM} does not have feature_importances, skipping')

    if model_uses_feature_importances:
        indices = np.argsort(feature_importances)

        feature_importance_fig, best_model_ax = plt.subplots(figsize=(20, 20))
        best_model_ax.barh(range(len(feature_importances)), feature_importances[indices])
        best_model_ax.set_yticks(range(len(feature_importances)))
        _ = best_model_ax.set_yticklabels(df_features.columns[[c + 1 for c in indices]])
    else:
        print(f'{ALGORITHM} does not have feature_importances, skipping')

    #
    # ## Stage: Write the final report for this algorithm and dataset version

    create_report = 'best' not in ALGORITHM_DETAIL

    if create_report:
        include_in_html_report("header", section_content=f"Results from {ALGORITHM}", section_figure=1, prefix=prefix_dir_results_root, key=key)

        end_timestamp = datetime.now()

        include_in_html_report(type="text", section_header=f"Dataset Version: {VERSION}", section_content_list=[
            f"Date run: {datetime.now()}"
            "",
            f"Start time: {start_timestamp}",
            f"End time: {end_timestamp}",
        ], prefix=prefix_dir_results_root, key=key)
        include_in_html_report("header", section_content=f"Results", section_figure=2, prefix=prefix_dir_results_root, key=key)

        include_in_html_report(type="text", section_header="Summary", section_content=new_model_decision, prefix=prefix_dir_results_root, key=key)

        # include_in_html_report(type="dataframe",text_single="Tuned Models ranked by performance", content=cv_results_df_sorted, prefix=prefix_dir_results_root, key=key)

        if not using_catboost:
            include_in_html_report(type='dataframe', section_header='Tuned Models ranked by performance, with parameter details', section_content=cv_results_df_summary,
                                   prefix=prefix_dir_results_root, key=key)

            include_in_html_report(type='graph', section_header='Best and worst models obtained by tuning', section_figure=worst_and_best_model_fig, section_content="best_and_worst.png",
                                   prefix=prefix_dir_results_root, key=key)

            include_in_html_report(type='graph', section_header='Best Model: Comparing model predictions to actual property values', section_figure=best_model_fig,
                                   section_content='best_model_correlation.png', prefix=prefix_dir_results_root, key=key)
        else:  # if using_catboost:
            include_in_html_report(type="text", section_header="Model Specific Notes",
                                   section_content_list=["can't display hyperparameter comparison for catboost", "can't display model performance graphs for catboost",
                                                         "can't display model performance graphs for catboost"], prefix=prefix_dir_results_root, key=key)

        if model_uses_feature_importances:
            include_in_html_report("header", section_content=f"Feature Importances", section_figure=2, prefix=prefix_dir_results_root, key=key)
            include_in_html_report(type="text", section_header="Feature Importances", section_content=feature_importances_output, prefix=prefix_dir_results_root, key=key)
            include_in_html_report(type="graph", section_header=f"Feature Importances ({ALGORITHM})", section_figure=feature_importance_fig,
                                   section_content='best_model_feature_importances.png', prefix=prefix_dir_results_root, key=key)

        include_in_html_report("header", section_content=f"Comparison with other models", section_figure=2, prefix=prefix_dir_results_root, key=key)

        # dff = pd.read_json('../../../results/results.json')
        dff = pd.read_json(prefix_dir_results_root + '/results.json')

        version = VERSION

        all_models_df = dff[dff.columns].T.sort_values("best score", ascending=False)
        version_models_df = dff[[c for c in dff.columns if version in c]].T.sort_values("best score", ascending=False)

        version_models_summary = version_models_df[
            ['best score', 'best time', 'Mean Absolute Error Accuracy', 'Mean Squared Error Accuracy', 'R square Accuracy', 'Root Mean Squared Error', 'best run date', 'best method']]
        all_models_summary = all_models_df[
            ['best score', 'best time', 'Mean Absolute Error Accuracy', 'Mean Squared Error Accuracy', 'R square Accuracy', 'Root Mean Squared Error', 'best run date', 'best method']]

        include_in_html_report(type="dataframe", section_header=f"Comparison with version {VERSION} performances", section_content=version_models_summary, prefix=prefix_dir_results_root,
                               key=key)
        include_in_html_report(type="dataframe", section_header="Comparison with all model performances", section_content=all_models_summary, prefix=prefix_dir_results_root, key=key)

        include_in_html_report("header", section_content=f"Appendix", section_figure=2, prefix=prefix_dir_results_root, key=key)

        include_in_html_report(type="dataframe", section_header="Data Sample", section_content=df.head(5), prefix=prefix_dir_results_root, key=key)

        include_in_html_report(type="json", section_header="Hyperparameter options for Randomized Grid Search", section_content=f"{param_options if not using_catboost else options_block}",
                               prefix=prefix_dir_results_root, key=key)

        if not using_catboost:
            include_in_html_report(type="graph", section_header=f"Range of hyperparameter results", section_figure=evolution_of_models_fig,
                                   section_content='evolution_of_models_fig.png', prefix=prefix_dir_results_root, key=key)

        include_in_html_report(type="dict", section_header="Environment Variables", section_content=env_vars, prefix=prefix_dir_results_root, key=key)

    print('Nearly finished...')

    print(f'ALGORITHM: {ALGORITHM}')
    print(f'ALGORITHM_DETAIL: {ALGORITHM_DETAIL}')
    print(f'DATA VERSION: {VERSION}')
    print(f'DATA_DETAIL: {DATA_DETAIL}')
    print(f'FILENAME: {FILENAME}')

    if warnings:
        print("Warnings:\n -", "\n - ".join(warnings))

    print('\nFinished!')


if __name__ == '__main__':
    main()

