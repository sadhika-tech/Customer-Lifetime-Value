import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from model_loader import load_customer_data


def render():
    st.title("Analytics Dashboard")
    st.markdown("Portfolio-level view of all customers across segments, clusters, and risk tiers.")

    df = load_customer_data()

    # --- KPI tiles ---
    st.subheader("Key metrics")
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Total customers",   f"{len(df):,}")
    k2.metric("Total revenue",     f"£{df['Monetary'].sum():,.0f}")
    k3.metric("Average CLTV",      f"£{df['CLTV'].mean():,.0f}")
    k4.metric("Overall churn rate",f"{df['Churned'].mean()*100:.1f}%")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        # Segment distribution
        seg_counts = df['Segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']
        fig = px.bar(seg_counts, x='Segment', y='Count',
                     title='Customers by RFM segment',
                     color='Segment',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Cluster revenue share
        cluster_rev = df.groupby('Cluster_Name')['Monetary'].sum().reset_index()
        fig = px.pie(cluster_rev, values='Monetary', names='Cluster_Name',
                     title='Revenue share by cluster',
                     color_discrete_sequence=['#2ecc71','#3498db','#e74c3c'])
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Churn risk breakdown
        risk_counts = df['Churn_Risk'].value_counts().reindex(
            ['Low','Medium','High']
        ).reset_index()
        risk_counts.columns = ['Risk', 'Count']
        fig = px.bar(risk_counts, x='Risk', y='Count',
                     title='Customers by churn risk tier',
                     color='Risk',
                     color_discrete_map={
                         'Low':'#2ecc71','Medium':'#f39c12','High':'#e74c3c'
                     })
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        # CLTV distribution
        fig = px.histogram(df, x='CLTV', nbins=40,
                           title='CLTV distribution',
                           color_discrete_sequence=['#3498db'])
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Full width — revenue by segment
    seg_rev = df.groupby('Segment')['Monetary'].sum().sort_values(
        ascending=False
    ).reset_index()
    fig = px.bar(seg_rev, x='Segment', y='Monetary',
                 title='Total revenue by RFM segment',
                 color='Monetary',
                 color_continuous_scale='Blues')
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    # Top customers table
    st.subheader("Top 10 customers by CLTV")
    top10 = df.nlargest(10, 'CLTV')[
        ['CustomerID','Frequency','Monetary','CLTV',
         'Churn_Probability','Segment','Cluster_Name']
    ].reset_index(drop=True)
    top10.index += 1
    top10['CLTV'] = top10['CLTV'].map('£{:,.0f}'.format)
    top10['Monetary'] = top10['Monetary'].map('£{:,.0f}'.format)
    top10['Churn_Probability'] = top10['Churn_Probability'].map('{:.1%}'.format)
    st.dataframe(top10, use_container_width=True)