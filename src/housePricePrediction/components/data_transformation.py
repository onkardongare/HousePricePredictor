import os

from sklearn.impute import SimpleImputer
from housePricePrediction import logger
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_array, check_is_fitted
from sklearn.metrics.pairwise import rbf_kernel

from sklearn.preprocessing import FunctionTransformer

from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer, make_column_selector, make_column_transformer

from housePricePrediction.entity.config_entity import DataTransformationConfig


class ClusterSimilarity(BaseEstimator, TransformerMixin):
    def __init__(self, n_clusters=10, gamma=1.0, random_state=None):
        self.n_clusters = n_clusters
        self.gamma = gamma
        self.random_state = random_state

    def fit(self, X, y=None, sample_weight=None):
        self.kmeans_ = KMeans(self.n_clusters, n_init=10,
                              random_state=self.random_state)
        self.kmeans_.fit(X, sample_weight=sample_weight)
        return self  # always return self!

    def transform(self, X):
        return rbf_kernel(X, self.kmeans_.cluster_centers_, gamma=self.gamma)
    
    def get_feature_names_out(self, names=None):
        return [f"Cluster {i} similarity" for i in range(self.n_clusters)]

class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config


    def train_test_splitting(self):
        
        housing = pd.read_csv(self.config.data_path)

        # create a new feature income_cat to split a data equally between testing and training set
        housing['income_cat'] = pd.cut(housing['median_income'],
                               bins=[0., 1.5, 3.0, 4.5, 6., np.inf],
                               labels=[1,2,3,4,5])

        strat_train_set, strat_test_set = train_test_split(
            housing, test_size=0.2, stratify= housing['income_cat'], random_state= 42)
        print(strat_test_set)

        strat_test_set.to_csv(os.path.join(self.config.root_dir, "test.csv"),index=False)
        strat_train_set.to_csv(os.path.join(self.config.root_dir, "train.csv"),index=False)
        return strat_train_set
        # housing = strat_train_set.drop("median_house_value", axis=1)
        # self.housing_labels = strat_train_set["median_house_value"].copy()

    def column_ratio(self,X):
        return X[:, [0]] / X[:, [1]]

    def ratio_name(self,function_transformer, feature_names_in):
        return ["ratio"]  # feature names out

    def ratio_pipeline(self):
        return make_pipeline(
            SimpleImputer(strategy="median"),
            FunctionTransformer(self.column_ratio, feature_names_out= self.ratio_name),
            StandardScaler())
    
    def preprocessing_pipeline(self):
        cat_pipeline = make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore"))

        log_pipeline = make_pipeline(
            SimpleImputer(strategy="median"),
            FunctionTransformer(np.log, feature_names_out="one-to-one"),
            StandardScaler())
        
        cluster_simil = ClusterSimilarity(n_clusters=10, gamma=1., random_state=42)

        default_num_pipeline = make_pipeline(SimpleImputer(strategy="median"),
                                            StandardScaler())
        preprocessing = ColumnTransformer([
                ("bedrooms", self.ratio_pipeline(), ["total_bedrooms", "total_rooms"]),
                ("rooms_per_house", self.ratio_pipeline(), ["total_rooms", "households"]),
                ("people_per_house", self.ratio_pipeline(), ["population", "households"]),
                ("log", log_pipeline, ["total_bedrooms", "total_rooms", "population",
                                    "households", "median_income"]),
                ("geo", cluster_simil, ["latitude", "longitude"]),
                ("cat", cat_pipeline, make_column_selector(dtype_include=object)),
            ],
            remainder=default_num_pipeline)  # one column remaining: housing_median_age
        return preprocessing
    
    def remove_outlier(self,housing):
        isolation_forest = IsolationForest(random_state=42)
        outlier_pred = isolation_forest.fit_predict(housing)
        housing = housing.iloc[outlier_pred == 1]
        housing_labels = housing_labels.iloc[outlier_pred == 1]
