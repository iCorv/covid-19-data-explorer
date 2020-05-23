import os

import streamlit as st
from streamlit import caching
import pandas as pd
import altair as alt


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

    st.info(
        """
        by: [Corvin Jaedicke](linkedin.com/in/corvin-jaedicke-ab1341186) 
        | source code: [GitHub](https://github.com/iCorv/covid-19-data-explorer)
        | data source: [Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19). 
        """
    )


if __name__ == "__main__":
    main()
