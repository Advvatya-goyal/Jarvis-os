import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Slide 1 - Visuals", page_icon="📊", layout="wide")

st.title("📊 Slide 1: Visualization Workspace")
st.markdown("Welcome to Slide 1. When you tell Jarvis on the Home page to 'Put the Pie chart on Slide 1', it will appear here in full size.")

st.markdown("---")

# Example of a premium layout for charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("US Stocks - Bar Chart")
    bar_data = pd.DataFrame(np.random.rand(5, 2), columns=["Volume", "Price"])
    st.bar_chart(bar_data)

with col2:
    st.subheader("Market Volatility - Area Chart")
    area_data = pd.DataFrame(np.random.randn(20, 3), columns=['A', 'B', 'C'])
    st.area_chart(area_data)