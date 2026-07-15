import streamlit as st
import numpy as np
import pandas as pd
from model_loader import load_all_models


def render():
    st.title("Customer CLTV and Churn Prediction")
    st.markdown("Enter customer behaviour metrics to get predicted lifetime value, "
                "cluster assignment, and churn risk.")

    artifacts = load_all_models()

    st.subheader("Customer details")

    col1, col2 = st.columns(2)

    with col1:
        frequency       = st.number_input("Frequency (number of orders)",
                                          min_value=1, max_value=500,
                                          value=5, step=1)
        monetary        = st.number_input("Monetary (total spend £)",
                                          min_value=0.0, max_value=100000.0,
                                          value=500.0, step=10.0)
        aov             = st.number_input("Average order value £",
                                          min_value=0.0, max_value=10000.0,
                                          value=100.0, step=5.0)
        unique_products = st.number_input("Unique products purchased",
                                          min_value=1, max_value=5000,
                                          value=20, step=1)

    with col2:
        recency         = st.number_input("Recency (days since last order)",
                                          min_value=1, max_value=1000,
                                          value=30, step=1)
        lifespan        = st.number_input("Lifespan (days between first and last order)",
                                          min_value=0, max_value=1000,
                                          value=180, step=1)
        avg_days        = st.number_input("Avg days between orders",
                                          min_value=0.0, max_value=500.0,
                                          value=36.0, step=1.0)

    st.divider()

    if st.button("Predict", type="primary", use_container_width=True):
        # --- CLTV prediction (Random Forest — no scaling needed) ---
        cltv_features = artifacts['cltv_features']
        X_cltv = pd.DataFrame([[
            recency, frequency, monetary, aov,
            unique_products, lifespan, avg_days
        ]], columns=cltv_features)

        predicted_cltv = artifacts['cltv_model'].predict(X_cltv)[0]

        # --- Churn prediction (XGBoost — no scaling needed, tree model) ---
        churn_features = artifacts['churn_features']
        # Recency is excluded from churn features (target leakage prevention)
        X_churn = pd.DataFrame([[
            frequency, monetary, aov,
            unique_products, lifespan, avg_days
        ]], columns=churn_features)

        churn_proba = artifacts['churn_model'].predict_proba(X_churn)[0][1]

        # --- Cluster assignment ---
        cluster_features = [
            'Recency', 'Frequency', 'Monetary', 'AOV',
            'UniqueProducts', 'Lifespan', 'CLTV', 'Churn_Probability'
        ]
        X_cluster = pd.DataFrame([[
            recency, frequency, monetary, aov,
            unique_products, lifespan, predicted_cltv, churn_proba
        ]], columns=cluster_features)

        X_cluster_scaled = artifacts['scaler_kmeans'].transform(X_cluster)
        X_pca = artifacts['pca'].transform(X_cluster_scaled)
        cluster_id = artifacts['kmeans'].predict(X_pca)[0]
        cluster_name = artifacts['cluster_names'][cluster_id]

        # --- Churn risk tier ---
        if churn_proba < 0.3:
            churn_risk = 'Low'
            risk_color = 'green'
        elif churn_proba < 0.6:
            churn_risk = 'Medium'
            risk_color = 'orange'
        else:
            churn_risk = 'High'
            risk_color = 'red'

        # --- Display results ---
        st.subheader("Prediction results")
        res_col1, res_col2, res_col3 = st.columns(3)

        with res_col1:
            st.metric(
                label="Predicted CLTV",
                value=f"£{predicted_cltv:,.0f}"
            )

        with res_col2:
            st.metric(
                label="Churn Probability",
                value=f"{churn_proba*100:.1f}%",
                delta=f"{churn_risk} risk",
                delta_color="inverse"
            )

        with res_col3:
            st.metric(
                label="Customer Cluster",
                value=cluster_name
            )

        st.divider()

        # --- Recommendation ---
        st.subheader("Recommended action")
        recommendations = {
            ('High Value', 'Low'):    ("🟢 Protect", "This is a high-value, low-risk customer. "
                                       "Enrol in loyalty programme, request reviews, "
                                       "offer early access to new products."),
            ('High Value', 'Medium'): ("🟡 Monitor closely", "High-value customer showing "
                                       "early churn signals. Send personalised retention "
                                       "offer within 14 days."),
            ('High Value', 'High'):   ("🔴 Rescue immediately", "High-value customer at serious "
                                       "churn risk. Personal outreach within 7 days. "
                                       "Strong retention incentive required."),
            ('Mid Value', 'Low'):     ("🔵 Nurture", "Mid-value customer with low churn risk. "
                                       "Target with upsell and cross-sell campaigns to "
                                       "grow to High Value."),
            ('Mid Value', 'Medium'):  ("🟡 Re-engage", "Mid-value customer drifting. "
                                       "Send a re-engagement email with a limited offer."),
            ('Mid Value', 'High'):    ("🟠 Win-back", "Mid-value customer at risk. "
                                       "One win-back campaign with discount. "
                                       "Archive if no response in 30 days."),
            ('Low Value', 'Low'):     ("🔵 Develop", "Low-value but stable. "
                                       "Include in broad upsell campaigns. "
                                       "Low priority for individual attention."),
            ('Low Value', 'Medium'):  ("⚪ Low priority", "Low-value customer drifting. "
                                       "Include in batch re-engagement only."),
            ('Low Value', 'High'):    ("⚫ Monitor", "Low-value, high-risk customer. "
                                       "Minimal spend. One final email then archive."),
        }

        key = (cluster_name, churn_risk)
        action_label, action_text = recommendations.get(
            key, ("ℹ️ Review manually", "No specific recommendation for this combination.")
        )

        st.info(f"**{action_label}:** {action_text}")