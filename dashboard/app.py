import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Bangalore Data Jobs Tracker", layout="wide")

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)


@st.cache_data(ttl=3600)
def load_table(table_name: str) -> pd.DataFrame:
    return pd.read_sql(f"select * from {table_name}", engine)


st.title("Bangalore data jobs tracker")
st.caption(
    "Daily-refreshed view of Data Analyst / Data Engineer / BI postings — "
    "an end-to-end data pipeline built on free-tier infrastructure."
)

skill_demand = load_table("mart_skill_demand")
company_hiring = load_table("mart_company_hiring")
postings_trend = load_table("mart_postings_trend")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Most in-demand skills (latest week)")
    if not skill_demand.empty:
        latest_week = skill_demand["week"].max()
        latest = skill_demand[skill_demand["week"] == latest_week].sort_values(
            "postings_mentioning", ascending=False
        )
        fig = px.bar(latest, x="skill", y="postings_mentioning")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet — run the ingestion pipeline first.")

with col2:
    st.subheader("Top hiring companies")
    if not company_hiring.empty:
        top_companies = company_hiring.sort_values(
            "open_postings", ascending=False
        ).head(15)
        fig2 = px.bar(top_companies, x="company", y="open_postings")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data yet — run the ingestion pipeline first.")

st.subheader("New postings over time")
if not postings_trend.empty:
    fig3 = px.line(postings_trend, x="day", y="new_postings")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No data yet — run the ingestion pipeline first.")

st.subheader("Skill demand, full table")
st.dataframe(skill_demand, use_container_width=True)
