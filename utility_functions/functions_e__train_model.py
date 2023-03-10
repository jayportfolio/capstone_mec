from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import Ridge, LinearRegression, RidgeCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, StackingRegressor

from time import time
import json


def make_modelling_pipeline(model, DATA_DETAIL):
    if 'no scale' in DATA_DETAIL:
        pipe = Pipeline([
            ('model', model)
        ])
    else:
        pipe = Pipeline([
            # ('mms', MinMaxScaler()),
            ('std_scaler', StandardScaler()),
            ('model', model)
        ])
    return pipe


def get_chosen_model(key):
    if key.lower() == 'catboost':
        from catboost import CatBoostRegressor
        CatBoostRegressor(objective='RMSE'),
    elif key.lower() == 'stacked model [knn,lgb,xgb]':
        import lightgbm as lgb
        from lightgbm import LGBMRegressor

        model_lr = LinearRegression()
        model_ridge = Ridge()
        model_xgb = XGBRegressor()
        model_knn = KNeighborsRegressor()
        model_lgb = LGBMRegressor()

        estimators = [
            ("knn1", model_knn),
            ("xgb1", model_xgb),
            ("lgb1", model_lgb)

        ]

        stacking_regressor = StackingRegressor(estimators=estimators, final_estimator=RidgeCV())
        return stacking_regressor

    elif key.lower() == 'light gradient boosting':
        import lightgbm as lgb
        from lightgbm import LGBMRegressor
        from lightgbm import DaskLGBMRegressor
        return LGBMRegressor()
    else:
        models = {
            "XG Boost".lower(): XGBRegressor(seed=20),
            "XG Boost (tree)".lower(): XGBRegressor(),
            "XG Boost (linear)".lower(): XGBRegressor(),
            "Linear Regression (Ridge)".lower(): Ridge(),
            "knn": KNeighborsRegressor(),
            "decision tree": DecisionTreeRegressor(),
            "random forest": RandomForestRegressor(),
            # "CatBoost".lower():
            # XXX "CatBoost".lower(): CatBoostRegressor(objective='R2'),
            # "Light Gradient Boosting".lower():
        }
        try:
            chosen_model = models.get(key.lower())
            if chosen_model == None:
                raise LookupError("there was no model for key:" + key)
            return chosen_model

        except:
            raise ValueError(f'no model found for key: {key}')


def get_hyperparameters(key, use_gpu, prefix='./', version=None, api_version=None):
    # hp_file = prefix + f'process/z_envs/hyperparameters/{key.lower()}.json'
    # hp_file = prefix + f'process/z_envs/hyperparameters/{key.lower()}.json'
    # hp_file = f'process/z_envs/hyperparameters/{key.lower()}.json'

    warnings = []

    versioned_hp_file = prefix + f'process/z_envs/hyperparameters/{key.lower()} v{version}.json'
    unversioned_hp_file = prefix + f'process/z_envs/hyperparameters/{key.lower()}.json'
    hp_file = versioned_hp_file if version else unversioned_hp_file

    if key.lower() == "XG Boost".lower():
        with open(hp_file) as f:
            hyperparameters = json.loads(f.read())

        if use_gpu:
            # hyperparameters['tree_method'].append('gpuhist')
            ###hyperparameters['n_estimators'].extend([250, 300, 500, 750, 1000])
            ###hyperparameters['gamma'].extend([1000000, 10000000])
            # hyperparameters['learning_rate'].extend([0.3, 0.01, 0.1, 0.2, 0.3, 0.4])
            # hyperparameters['early_stopping_rounds'].extend([1, 5, 10, 100])
            pass

    elif key.lower() in ['catboost', 'random forest', "Linear Regression (Ridge)".lower(), "Light Gradient Boosting".lower(),
                         'knn', 'decision tree', 'xg boost (tree)', 'xg boost (linear)']:

        try:
            with open(hp_file) as f:
                hyperparameters = json.loads(f.read())
        except FileNotFoundError as e:
            if version:
                warnings.append("Had to look for an unversioned hyperparameter file even though a versioned hyperparameter file was requested.")
                with open(unversioned_hp_file) as f:
                    hyperparameters = json.loads(f.read())
            else:
                raise e


    else:
        try:
            print("failed all other avenues, just trying to find the hyperparams with pattern-matching")
            with open(prefix + hp_file) as f:
                hyperparameters = json.loads(f.read())

        except:
            raise ValueError("couldn't find hyperparameters for:", key)

    if api_version is None:
        return hyperparameters
    else:
        return hyperparameters, None if len(warnings) == 0 else warnings


def get_cv_params(options_block, debug_mode=True, override_cv=None, override_niter=None, override_verbose=None, override_njobs=None):
    global param_options, cv, n_jobs, verbose, refit, iter
    param_options = {}
    for each in options_block:
        if type(options_block[each]) == list:
            param_options['model__' + each] = options_block[each]
        elif options_block[each] == None:
            # print (f'skipping {each} because value is {options_block[each]}')
            param_options['model__' + each] = [options_block[each]]
        else:
            param_options['model__' + each] = [options_block[each]]

    # cv = 3
    cv = override_cv if override_cv else 3
    # n_iter = 100
    n_iter = override_niter if override_niter else 100
    # verbose = 3 if debug_mode else 1
    verbose = override_verbose if override_verbose else 3 if debug_mode else 1
    refit = True
    # n_jobs = 1
    n_jobs = override_njobs if override_njobs else 1 if debug_mode else 3

    return param_options, cv, n_jobs, refit, n_iter, verbose


def fit_model_with_cross_validation(gs, X_train, y_train, fits):
    pipe_start = time()
    cv_result = gs[0].fit(X_train, y_train)
    pipe_end = time()
    average_time = round((pipe_end - pipe_start) / (fits), 2)
    # xxx print(f"{average_time} seconds per fit") # not correct if declared fits was overstated
    # print(f"average fit time = {cv_result.cv_results_.mean_fit_time}s")
    # print(f"max fit time = {cv_result.cv_results_.mean_fit_time.max()}s")
    # print(f"average fit/score time = {round(cv_result.cv_results_.mean_fit_time,2)}s/{round(cv_result.cv_results_.mean_score_time,2)}s")

    print(f"Total fit/CV time      : {int(pipe_end - pipe_start)} seconds   ({pipe_start} ==> {pipe_end})")
    print()
    print(f'average fit/score time = {round(cv_result.cv_results_["mean_fit_time"].mean(), 2)}s/{round(cv_result.cv_results_["mean_score_time"].mean(), 2)}s')
    print(f'max fit/score time     = {round(cv_result.cv_results_["mean_fit_time"].max(), 2)}s/{round(cv_result.cv_results_["mean_score_time"].max(), 2)}s')
    print(f'refit time             = {round(cv_result.refit_time_, 2)}s')

    return cv_result, average_time, cv_result.refit_time_, len(cv_result.cv_results_["mean_fit_time"])


def automl_step(param_options, vary):
    for key, value in param_options.items():
        # print(key, value, vary)
        if key != vary and key != 'model__' + vary:
            param_options[key] = [param_options[key][0]]
    return param_options


if False:
    param_options = automl_step(param_options, vary='gamma')
    print(f'cv={cv}, n_jobs={n_jobs}, refit={refit}, n_iter={n_iter}, verbose={verbose}')
