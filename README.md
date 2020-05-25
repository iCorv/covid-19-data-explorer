## Yet another COVID-19 Data Explorer App

The intention of this project is to demonstrate a real-life use-case for the [streamlit](http://streamlit.io) framework. Therfore it is structured into four phases which showcase the streamlit app with increasing complexity.

![phases meme](https://github.com/iCorv/covid-19-data-explorer/blob/master/assets/the_phases.jpg "Logo Title Text 1")

### Try it!

Install dependencies: `pip install -r requirements.txt`

Run app locally: `streamlit run phase_x.py`

Or if you are more of a docker-type: 
```
docker build -t covid-19-data-explorer:lastest .
docker run --rm -p 8501:8501 covid-19-data-explorer:lastest
```

In addition, the app is ready to be deployed to [heroku](https://heroku.com), hence the `setup.sh` and `Procfile`. I will leave the explanation to them.

### Data Source

All data used in this project originates from the Johns Hopkins University [GitHub](https://github.com/CSSEGISandData/COVID-19).