import os
from functools import reduce

import streamlit as st
from streamlit import caching
import pandas as pd
import altair as alt
import pydeck as pdk

# data from Johns Hopkins University (https://github.com/CSSEGISandData/COVID-19)
BASEURL = "https://raw.githubusercontent.com/CSSEGISandData/" \
          "COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"


@st.cache
def get_data():
    url_confirmed = os.path.join(BASEURL, "time_series_covid19_confirmed_global.csv")
    url_deaths = os.path.join(BASEURL, "time_series_covid19_deaths_global.csv")
    url_recovered = os.path.join(BASEURL, "time_series_covid19_recovered_global.csv")

    # read/get the data from github
    confirmed_raw = pd.read_csv(url_confirmed, index_col=0)
    deaths_raw = pd.read_csv(url_deaths, index_col=0)
    recovered_raw = pd.read_csv(url_recovered, index_col=0)

    # some regions have sub-territories, so we will sum over them to make it simpler
    confirmed = confirmed_raw.groupby("Country/Region").sum().reset_index()
    deaths = deaths_raw.groupby("Country/Region").sum().reset_index()
    recovered = recovered_raw.groupby("Country/Region").sum().reset_index()

    # date list
    date_list = confirmed.columns[3:]

    # drop unnecessary columns
    confirmed.drop(columns=['Long', 'Lat'], inplace=True)
    deaths.drop(columns=['Long', 'Lat'], inplace=True)
    recovered.drop(columns=['Long', 'Lat'], inplace=True)

    return confirmed, deaths, recovered, confirmed_raw, deaths_raw, recovered_raw, date_list


def main():
    st.title("COVID-19 Data Explorer")
    st.markdown(
        """
        This app visualizes the data describing the spread of COVID-19. 
        Many thanks to the Johns Hopkins University for providing this important data accumulation to the public. 
        However, we should never stop the discourse about the 
        [sources and quality](https://edition.cnn.com/interactive/2020/05/world/worldometer-coronavirus-mystery/index.html) 
        of our data.
        """
    )

    view = st.sidebar.selectbox("Choose View", ["Raw Data", "Data Visualization"])

    if view == "Raw Data":
        # get and cache the data
        confirmed, deaths, recovered = get_data()

        # show the dataframes in the app
        st.markdown("### Confirmed Cases:")
        st.dataframe(confirmed)

        st.markdown("### COVID-19 Related Deaths:")
        st.dataframe(deaths)

        st.markdown("### Recovered Cases:")
        st.dataframe(recovered)

    elif view == "Data Visualization":
        confirmed, deaths, recovered, _, _, _, _ = get_data()

        df_dict = {'confirmed': confirmed, 'recovered': recovered, 'deaths': deaths}

        # get list of regions
        region = df_dict['confirmed']["Country/Region"]

        st.header("Region-wise Visualization")
        st.markdown("Type the Region you want to investigate in the menu below.")

        # select a region
        selection = st.selectbox("Select Region:", region)

        # iterate over all three dfs and prepare for plot
        for name, _ in df_dict.items():
            df_dict[name] = df_dict[name][deaths["Country/Region"] == selection].drop(columns="Country/Region")
            df_dict[name] = pd.melt(df_dict[name])
            df_dict[name]["date"] = pd.to_datetime(df_dict[name].variable, infer_datetime_format=True)
            df_dict[name] = df_dict[name].set_index("date")
            df_dict[name] = df_dict[name][["value"]]
            df_dict[name].columns = [name]

        df = reduce(lambda a, b: pd.merge(a, b, on='date'), list(df_dict.values()))
        df["confirmed_active"] = df.confirmed - (df.deaths + df.recovered)

        plot_columns = ["recovered", "confirmed_active", "deaths"]
        colors = ['forestgreen', "gold", "red"]

        color_scale = alt.Scale(domain=plot_columns, range=colors)

        plot_df = pd.melt(df.reset_index(), id_vars=["date"], value_vars=plot_columns)

        # prevent altair from sorting the variables (deaths should be lowest)
        plot_df['order'] = plot_df['variable'].replace({val: idx for idx, val in enumerate(plot_columns[::-1])})

        # make some space
        st.header("")

        altair_plot = alt.Chart(plot_df.reset_index()).mark_bar().properties(height=300).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("sum(value):Q", title="Count", scale=alt.Scale(type='linear')),
            color=alt.Color('variable:N', title="", scale=color_scale),
            order='order'
        )

        # show plot in streamlit
        st.altair_chart(altair_plot, use_container_width=True)

    st.info(
        """
        by: [Corvin Jaedicke](linkedin.com/in/corvin-jaedicke-ab1341186) 
        | source code: [GitHub](https://github.com/iCorv/covid-19-data-explorer)
        | data source: [Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19). 
        """
    )


if __name__ == "__main__":
    main()
