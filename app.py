import os

import streamlit as st
from streamlit import caching
import pandas as pd
import altair as alt

# data from Johns Hopkins University (https://github.com/CSSEGISandData/COVID-19)
BASEURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"


@st.cache
def get_data():
    url_confirmed = os.path.join(BASEURL, "time_series_covid19_confirmed_global.csv")
    url_deaths = os.path.join(BASEURL, "time_series_covid19_deaths_global.csv")
    url_recovered = os.path.join(BASEURL, "time_series_covid19_recovered_global.csv")

    # read/get the data from github
    confirmed = pd.read_csv(url_confirmed, index_col=0)
    deaths = pd.read_csv(url_deaths, index_col=0)
    recovered = pd.read_csv(url_recovered, index_col=0)

    # some regions have sub-territories, so we will sum over them to make it simpler
    confirmed = confirmed.groupby("Country/Region").sum().reset_index()
    deaths = deaths.groupby("Country/Region").sum().reset_index()
    recovered = recovered.groupby("Country/Region").sum().reset_index()

    return confirmed, deaths, recovered


def main():
    st.title("COVID-19 Data Explorer")
    st.markdown(
        """
        This app visualizes the data describing the spread of COVID-19.
        """
    )

    confirmed, deaths, recovered = get_data()
    st.dataframe(confirmed)


if __name__ == "__main__":
    main()
