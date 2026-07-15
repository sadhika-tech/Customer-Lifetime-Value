import streamlit as st
import pandas as pd
import plotly.express as px
import os


def render():
    st.title("Model Insights")
    st.markdown("Performance comparison and feature importance for both predictive models.")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

    # --- CLTV model comparison ---
    st.subheader("CLTV model comparison (regression)")

    cltv_path = os.path.join(OUTPUTS_DIR, 'model_comparison_table.csv')
    if os.path.exists(cltv_path):
        cltv_comparison = pd.read_csv(cltv_path)
        st.dataframe(cltv_comparison, use_container_width=True)

        fig = px.bar(cltv_comparison, x='Model', y='R2',
                     title='R² score by model (CLTV)',
                     color='Model',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run cltv_prediction.ipynb to generate model_comparison_table.csv")

    st.divider()

    # --- Churn model comparison ---
    st.subheader("Churn model comparison (classification)")

    churn_path = os.path.join(OUTPUTS_DIR, 'churn_model_comparison_table.csv')
    if os.path.exists(churn_path):
        churn_comparison = pd.read_csv(churn_path)
        st.dataframe(churn_comparison, use_container_width=True)

        fig = px.bar(churn_comparison, x='Model', y='AUC',
                     title='AUC score by model (churn)',
                     color='Model',
                     color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run churn_prediction.ipynb to generate churn_model_comparison_table.csv")

    st.divider()

    # --- SHAP charts ---
    st.subheader("SHAP explainability")

    shap_col1, shap_col2 = st.columns(2)

    with shap_col1:
        st.markdown("**CLTV model — feature impact**")
        cltv_shap = os.path.join(OUTPUTS_DIR, 'shap_cltv_beeswarm.png')
        if os.path.exists(cltv_shap):
            st.image(cltv_shap, use_column_width=True)
        else:
            st.info("Run shap_exxplainability.ipynb to generate SHAP charts.")

    with shap_col2:
        st.markdown("**Churn model — feature impact**")
        churn_shap = os.path.join(OUTPUTS_DIR, 'shap_churn_beeswarm.png')
        if os.path.exists(churn_shap):
            st.image(churn_shap, use_column_width=True)
        else:
            st.info("Run shap_explainability.ipynb to generate SHAP charts.")

    # Waterfall charts
    st.markdown("**CLTV waterfall — high vs low value customer**")
    wf_col1, wf_col2 = st.columns(2)
    with wf_col1:
        path = os.path.join(OUTPUTS_DIR, 'shap_cltv_waterfall_high.png')
        if os.path.exists(path):
            st.image(path, use_column_width=True)
    with wf_col2:
        path = os.path.join(OUTPUTS_DIR, 'shap_cltv_waterfall_low.png')
        if os.path.exists(path):
            st.image(path, use_column_width=True)