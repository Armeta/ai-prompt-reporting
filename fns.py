import pickle
import pandas as pd
import numpy as np
from typing import Tuple, List
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

def preprocess_features(df: pd.DataFrame, isTrain: bool = False) -> pd.DataFrame:
    df = df.copy(deep=True)

    features = {
        'nominal': [
            'FACCITY', 'FACSTATE', 'FACZIP', 'GROUP', 'NEEDSPECIALTY', 'NEEDDISCIPLINE',
            'NURSEDISCIPLINE', 'PERMCITY', 'PERMSTATE', 'PERMZIP',
        ],
        'ordinal': ['FACILITYGRADE', 'JOBGRADE'],
        'numerical': [
            'NUMOFBEDS', 'WEEKLYGROSS', 'HOURLYMEALS', 'HOURLYLODGING', 'TAXEDHOURLY', 'LENGTH',
            'TOTALREGHOURS', 'TOTALPREMHOURS', 'TOTALOTHOURS', 'TOTALHOURLY', 'REGULARTIME',
        ],
    }

    df['WEEKLYGROSS'] = df['WEEKLYGROSS'].astype(float)

    print("(Pre)processing nominal features...\n")
    for feat in features['nominal']:
        print(f"\t{feat}\n")
        lab_enc = LabelEncoder()
        if not isTrain:
            lab_enc.classes_ = np.load(f"../model-files/{feat}_classes.npy", allow_pickle=True)
            df[feat] = lab_enc.transform(df[feat])
        else:
            df[feat] = lab_enc.fit_transform(df[feat])
            np.save(f"../model-files/{feat}_classes.npy", lab_enc.classes_)

    grade_mapping = {
        None: 0,
        "C": 1,
        "B": 2,
        "A": 3,
        "A+": 4,
    }

    print(f"(Pre)processing ordinal features...\n")
    for feat in features['ordinal']:
        print(f"\t{feat}\n")
        df[feat] = df[feat].replace(grade_mapping)


    print("Imputing features...\n")
    impute_features = features['nominal'] + features['ordinal'] + features['numerical']
    for feat in impute_features:
        print(f"\t{feat}\n")
        if feat in features['nominal'] or feat in features['ordinal']:
            imp = SimpleImputer(strategy='most_frequent')
        elif feat in features['numerical']:
            imp = SimpleImputer(strategy='mean')
        
        df[feat] = imp.fit_transform(df[[feat]])

    return df


def drop_features(df: pd.DataFrame, feature_set: str):
    feature_set = feature_set.lower()
    feature_sets = {
        'nurse': ['NURSEDISCIPLINE', 'PERMCITY', 'PERMSTATE', 'PERMZIP'],
        'need': [
            'FACCITY', 'FACSTATE', 'FACZIP', 'GROUP', 'FACILITYGRADE', 'NUMOFBEDS', 'NEEDSPECIALTY', 'NEEDDISCIPLINE',
            'WEEKLYGROSS', 'HOURLYMEALS', 'HOURLYLODGING', 'TAXEDHOURLY', 'JOBGRADE', 'LENGTH',
            'TOTALREGHOURS', 'TOTALPREMHOURS', 'TOTALOTHOURS', 'TOTALHOURLY', 'REGULARTIME',
        ],
    }

    return df.drop(feature_sets[feature_set], axis=1)


def get_values_and_labels(df: pd.DataFrame, feature_name: str) -> tuple([List[int], List[str]]):
    series = df.value_counts(subset=[feature_name])
    values = series.values
    labels = [index[0] for index in series.index]

    return (values, labels)


def predict_fit_score(df: pd.DataFrame) -> pd.Series:
    model = pickle.load(open('../model-files/new_features_model.pkl', 'rb'))

    return model.predict_proba(df)[:,1] * 100


