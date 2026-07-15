import pickle
import bz2
import pandas as pd
import streamlit as st
import os

# Resolve paths relative to this file regardless of where streamlit is launched from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')


@st.cache_resource
def load_all_models():

    def load_pickle(filename):
        path = os.path.join(MODELS_DIR, filename)
        with open(path, 'rb') as f:
            return pickle.load(f)

    def load_bz2(filename):
        path = os.path.join(MODELS_DIR, filename)
        with bz2.BZ2File(path, 'rb') as f:
            return pickle.load(f)

    return {
        # CLTV model — Random Forest regressor
        'cltv_model':       load_pickle('best_model.pickle'),
        'cltv_features':    load_pickle('cltv_features.pickle'),
        'scaler_xgb':       load_pickle('scaler_xgb.pickle'),

        # Churn model — XGBoost classifier
        'churn_model':      load_pickle('churn_model.pickle'),
        'churn_features':   load_pickle('churn_features.pickle'),
        'scaler_churn':     load_pickle('scaler_churn.pickle'),

        # Clustering artifacts
        'scaler_kmeans':    load_pickle('scaler_kmeans.pickle'),
        'pca':              load_pickle('pca.pickle'),
        'kmeans':           load_pickle('kmeans.pickle'),
        'cluster_names':    load_pickle('cluster_names.pickle'),

        # SHAP explainers
        'cltv_explainer':   load_bz2('cltv_explainer.bz2'),
        'churn_explainer':  load_bz2('churn_explainer.bz2'),
    }


@st.cache_data
def load_customer_data():

    path = os.path.join(OUTPUTS_DIR, 'customer_final.csv')
    return pd.read_csv(path)