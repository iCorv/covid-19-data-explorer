import os
from functools import reduce

import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk

# data from Johns Hopkins University (https://github.com/CSSEGISandData/COVID-19)
BASEURL = 'https://raw.githubusercontent.com/CSSEGISandData/' \
          'COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'


@st.cache
def get_data():
    url_confirmed = os.path.join(BASEURL, 'time_series_covid19_confirmed_global.csv')
    url_deaths = os.path.join(BASEURL, 'time_series_covid19_deaths_global.csv')
    url_recovered = os.path.join(BASEURL, 'time_series_covid19_recovered_global.csv')
    url_confirmed_us = os.path.join(BASEURL, 'time_series_covid19_confirmed_US.csv')
    url_deaths_us = os.path.join(BASEURL, 'time_series_covid19_deaths_US.csv')

    # read/get the data from github
    confirmed_raw = pd.read_csv(url_confirmed, index_col=0)
    deaths_raw = pd.read_csv(url_deaths, index_col=0)
    recovered_raw = pd.read_csv(url_recovered, index_col=0)

    # more granular us data
    confirmed_us_raw = pd.read_csv(url_confirmed_us, index_col=0)
    deaths_us_raw = pd.read_csv(url_deaths_us, index_col=0)
    return confirmed_raw, deaths_raw, recovered_raw, confirmed_us_raw, deaths_us_raw


@st.cache
def preprocess_plot_data(confirmed_raw, deaths_raw, recovered_raw):
    # use numeric index and drop unused columns
    confirmed_raw = confirmed_raw.reset_index()
    deaths_raw = deaths_raw.reset_index()
    recovered_raw = recovered_raw.reset_index()

    # some regions have sub-territories, so we will sum over them to make it simpler
    confirmed = confirmed_raw.groupby('Country/Region').sum().reset_index()
    deaths = deaths_raw.groupby('Country/Region').sum().reset_index()
    recovered = recovered_raw.groupby('Country/Region').sum().reset_index()

    # date list
    date_list = confirmed.columns[3:]

    # drop unnecessary columns
    confirmed = confirmed.drop(columns=['Long', 'Lat'])
    deaths = deaths.drop(columns=['Long', 'Lat'])
    recovered = recovered.drop(columns=['Long', 'Lat'])

    return confirmed, deaths, recovered, date_list


@st.cache
def preprocess_map_data(confirmed_raw, deaths_raw, recovered_raw, confirmed_us_raw, deaths_us_raw):
    # use numeric index and drop unused columns
    confirmed_raw = confirmed_raw.reset_index()
    deaths_raw = deaths_raw.reset_index()
    recovered_raw = recovered_raw.reset_index()
    confirmed_us_raw = confirmed_us_raw.reset_index().drop(columns=['iso2', 'iso3', 'code3',
                                                                    'FIPS', 'Admin2', 'UID',
                                                                    'Province_State'])
    deaths_us_raw = deaths_us_raw.reset_index().drop(columns=['iso2', 'iso3', 'code3',
                                                              'FIPS', 'Admin2', 'UID',
                                                              'Province_State', 'Population'])

    # rename some inconsistent columns
    confirmed_us_raw = confirmed_us_raw.rename(columns={'Country_Region': 'Country/Region', 'Long_': 'Long'})
    deaths_us_raw = deaths_us_raw.rename(columns={'Country_Region': 'Country/Region', 'Long_': 'Long'})

    # date list
    date_list = confirmed_raw.columns[4:]

    def state_region(row):
        if isinstance(row[0], float):
            return row[1]
        else:
            return f'{row[0]}, {row[1]}'

    # build a human readable region string
    confirmed_raw['Combined_Key'] = confirmed_raw.apply(state_region, axis=1)
    deaths_raw['Combined_Key'] = confirmed_raw.apply(state_region, axis=1)
    recovered_raw['Combined_Key'] = confirmed_raw.apply(state_region, axis=1)
    confirmed_raw = confirmed_raw.drop(columns='Province/State')
    deaths_raw = deaths_raw.drop(columns='Province/State')
    recovered_raw = recovered_raw.drop(columns='Province/State')

    # merge global and us data
    confirmed_raw = confirmed_raw[confirmed_raw['Country/Region'] != 'US'].append(confirmed_us_raw, ignore_index=True)
    deaths_raw = deaths_raw[deaths_raw['Country/Region'] != 'US'].append(deaths_us_raw, ignore_index=True)

    return confirmed_raw, deaths_raw, recovered_raw, date_list


def map_digest_format(df, date):
    map_format = df.copy()
    map_format['data'] = map_format[date]
    # print pretty int with comma separated 1000s
    map_format['data_string'] = map_format[date].apply(lambda x: f'{x:,}')
    return map_format


def main():
    st.title('COVID-19 Data Explorer')
    st.markdown(
        """
        This app visualizes the data describing the spread of COVID-19. 
        Many thanks to the Johns Hopkins University for providing this important data accumulation to the public. 
        However, we should never stop the discourse about the 
        [sources and quality](https://edition.cnn.com/interactive/2020/05/world/worldometer-coronavirus-mystery/index.html) 
        of our data.
        """
    )

    confirmed_raw, deaths_raw, recovered_raw, confirmed_us_raw, deaths_us_raw = get_data()
    confirmed, deaths, recovered, date_list = preprocess_plot_data(confirmed_raw, deaths_raw, recovered_raw)

    view = st.sidebar.selectbox('Choose View', ['Raw Data', 'Data Visualization', 'World Map'], index=2)

    # print summed total numbers
    total_deaths = sum(deaths[date_list[-1]])
    total_confirmed = sum(confirmed[date_list[-1]])
    total_recovered = sum(recovered[date_list[-1]])
    total_active = total_confirmed - (total_deaths + total_recovered)
    st.sidebar.header('Total')
    st.sidebar.text(f'Last updated: {date_list[-1]}')
    st.sidebar.error(f'Deaths: {total_deaths:,}')
    st.sidebar.warning(f'Active: {total_active:,}')
    st.sidebar.success(f'Recovered: {total_recovered:,}')
    st.sidebar.info(f'Confirmed: {total_confirmed:,}')

    if view == 'Raw Data':

        # show the dataframes in the app
        st.markdown('### Confirmed Cases:')
        st.dataframe(confirmed)

        st.markdown('### COVID-19 Related Deaths:')
        st.dataframe(deaths)

        st.markdown('### Recovered Cases:')
        st.dataframe(recovered)

    elif view == 'Data Visualization':

        df_dict = {'confirmed': confirmed, 'recovered': recovered, 'deaths': deaths}

        # get list of regions
        region = df_dict['confirmed']['Country/Region']

        # lets start with germany
        idx_ger = list(region).index('Germany')

        st.header('Region-wise Visualization')
        st.markdown('Type the region you want to investigate in the menu below.')

        # select a region
        selection = st.selectbox('Select Region:', region, index=idx_ger)

        # iterate over all three dfs and prepare for plot
        for name, _ in df_dict.items():
            df_dict[name] = df_dict[name][deaths['Country/Region'] == selection].drop(columns='Country/Region')
            df_dict[name] = pd.melt(df_dict[name])
            df_dict[name]['date'] = pd.to_datetime(df_dict[name].variable, infer_datetime_format=True)
            df_dict[name] = df_dict[name].set_index('date')
            df_dict[name] = df_dict[name][['value']]
            df_dict[name].columns = [name]

        df = reduce(lambda a, b: pd.merge(a, b, on='date'), list(df_dict.values()))
        df['confirmed_active'] = df.confirmed - (df.deaths + df.recovered)

        plot_columns = ['recovered', 'confirmed_active', 'deaths']
        colors = ['forestgreen', 'gold', 'red']

        color_scale = alt.Scale(domain=plot_columns, range=colors)

        plot_df = pd.melt(df.reset_index(), id_vars=['date'], value_vars=plot_columns)

        # prevent altair from sorting the variables (deaths should be lowest)
        plot_df['order'] = plot_df['variable'].replace({val: idx for idx, val in enumerate(plot_columns[::-1])})

        # make some space
        st.header('')

        altair_plot = alt.Chart(plot_df.reset_index()).mark_bar().properties(height=300).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('sum(value):Q', title='Count', scale=alt.Scale(type='linear')),
            color=alt.Color('variable:N', title='', scale=color_scale),
            order='order'
        )

        # show plot in streamlit
        st.altair_chart(altair_plot, use_container_width=True)

    elif view == 'World Map':

        st.header('Heatmap of the COVID-19 spread over time')

        confirmed_raw, deaths_raw, recovered_raw, date_list = preprocess_map_data(confirmed_raw, deaths_raw,
                                                                                  recovered_raw, confirmed_us_raw,
                                                                                  deaths_us_raw)

        data_source = st.selectbox('Select Data Source:', ['Confirmed Cases', 'COVID-19 Related Deaths', 'Recovered'])

        num_days = len(date_list)
        info_placeholder = st.empty()
        map_placeholder = st.empty()
        date_index = st.slider('', min_value=0, max_value=num_days - 1, value=num_days - 1, format='Day %i')
        intensity = st.slider('Heat Map Intensity', min_value=2, max_value=20, value=5)
        info_placeholder.text(f'Data displayed for {date_list[date_index]}')

        if data_source == 'Confirmed Cases':
            map_df = map_digest_format(confirmed_raw, date_list[date_index])
        elif data_source == 'COVID-19 Related Deaths':
            map_df = map_digest_format(deaths_raw, date_list[date_index])
        else:
            map_df = map_digest_format(recovered_raw, date_list[date_index])

        map_placeholder.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/dark-v9',
            tooltip={'text': '{Combined_Key}: {data_string}'},
            initial_view_state=pdk.ViewState(
                latitude=41.1533,
                longitude=20.1683,
                zoom=0.5,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'HeatmapLayer',
                    data=map_df,
                    get_position='[Long, Lat]',
                    opacity=1.0,
                    aggregation='"MEAN"',
                    get_weight='[data]',
                    radius_pixels=intensity,
                    threshold=0.002,
                    pickable=True
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=map_df,
                    get_position='[Long, Lat]',
                    pickable=True,
                    opacity=0.99,
                    stroked=True,
                    filled=True,
                    radius_scale=20,
                    radius_min_pixels=20,
                    radius_max_pixels=100,
                    line_width_min_pixels=1,
                    get_radius='exits_radius',
                    get_fill_color=[0, 0, 0, 0.0],
                    get_line_color=[0, 0, 0, 0.0],
                )
            ],
        )
        )

    st.info(
        """
        by: [Corvin Jaedicke](https://linkedin.com/in/corvin-jaedicke-ab1341186) 
        | source code: [GitHub](https://github.com/iCorv/covid-19-data-explorer)
        | data source: [Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19). 
        """
    )


if __name__ == '__main__':
    main()
