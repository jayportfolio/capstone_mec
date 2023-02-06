import pickle
from unittest import TestCase

from sklearn.pipeline import Pipeline


class Test(TestCase):
    #def test_main(self):
    #    self.skipTest('testing testing')

    # 'optimised_model_CatBoost_v06',
    # 'optimised_model_KNN_v06',
    # 'optimised_model_Linear Regression (Ridge)_v06',
    # 'optimised_model_Neural Network_v06',
    # 'optimised_model_XG Boost_v06'

    def test_main2(self):
        selected_model = 'abc'

        for selected_model in [
            'optimised_model_Decision Tree_v06',
            'optimised_model_CatBoost_v06',
            'optimised_model_KNN_v06',
            'optimised_model_Linear Regression (Ridge)_v06',
            'optimised_model_Neural Network_v06',
            'optimised_model_XG Boost_v06'
        ]:
            #model_path = f'models_pretrained/{selected_model}.pkl'
            #model = pickle.load(open(model_path, 'rb'))
            from functions_gh_presentation_and_launch import load_model
            model = load_model(selected_model=selected_model, model_type='neural' if 'eural' in selected_model else 'standard')

        self.assertIsInstance(model, Pipeline)


