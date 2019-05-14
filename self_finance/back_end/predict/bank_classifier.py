import logging
import os

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from config.files import dirs
from self_finance.back_end.data import Data
from self_finance.constants import Schema

logger = logging.getLogger(__name__)


class _DataFrameSelector(BaseEstimator, TransformerMixin):
    """
    obj: to be able to begin a pipeline with a static frame
    """

    def __init__(self, attribute_names):
        self.attribute_names = attribute_names

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.attribute_names].values


class BankClassifier:
    def __init__(self):
        self.model_df = Data.get_table_as_df(date_range=None)
        assert self.model_df.shape[0] > 0, "No bank static was found."

    # training information columns and  output column names
    _model_X_columns = Schema.get_table_chase_X_fields()
    _model_selector_y = {Schema.BASE_MODEL_C1_NAME: Schema.SCHEMA_CHASE_C1,
                         Schema.BASE_MODEL_C2_NAME: Schema.SCHEMA_CHASE_C2}

    def _can_train(self, model_name):
        # check that X exists and that there are y-labels
        y_map = {Schema.BASE_MODEL_C1_NAME: 'c1',
                 Schema.BASE_MODEL_C2_NAME: 'c2'}
        return self.model_df.shape[0] > 0 and \
               any(val for val in self.model_df[y_map[model_name]].values)

    def _re_train(self, model_name, save_to_disk=True):
        """
        obj: build main classifier for bank expense categories
        """
        # validate even if a model can be built to begin with
        if not self._can_train(model_name):
            return None

        central_x_pipeline = Pipeline([
            ('selector', _DataFrameSelector(BankClassifier._model_X_columns)),
            ('std_scaler', StandardScaler()),
        ])

        central_y_pipeline = Pipeline([
            ('selector', _DataFrameSelector(BankClassifier._model_selector_y[model_name])),
        ])

        X = central_x_pipeline.fit_transform(self.model_df)
        y = central_y_pipeline.fit_transform(self.model_df)
        parameters = {'max_depth': np.arange(5, 30, 3),
                      'n_estimators': np.arange(100, 120, 5),
                      'min_samples_split': np.arange(20, 60, 15)}

        rforest = RandomForestClassifier(criterion='entropy')
        gsearch = GridSearchCV(rforest, parameters, n_jobs=-1, cv=3, scoring='roc_auc', verbose=10)
        gsearch.fit(X, y)
        if save_to_disk:
            joblib.dump(gsearch.best_estimator_, os.path.join(dirs['models'], model_name))
        return gsearch.best_estimator_

    def get_model(self, model_name):
        """
        obj: obtain a pre-trained model
        """
        try:
            return joblib.load(os.path.join(dirs['models'], model_name))
        except FileNotFoundError:
            return self._re_train(model_name, save_to_disk=True)
