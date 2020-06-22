import local_data as sample_data
from flask import Flask, render_template
from altair import Chart, X, Y, Axis, Data, DataFormat, selection_interval, condition, Size, value, Scale, Legend
import pandas as pd

# load a simple dataset as a pandas DataFrame
from vega_datasets import data
cars = data.cars()
electricity = data.iowa_electricity()
barley_yield = data.barley()

app = Flask(__name__)

# Load data
full_clean_data = pd.read_csv('COVID-19-time-series-clean-complete.csv',
                              parse_dates=['Date'])

# Select a list of countries
countries = [
    'US', 'Italy', 'China', 'Spain', 'France', 'Iran', 'United Kingdom',
    'Switzerland', 'India', 'Canada'
]
selected_data = full_clean_data[full_clean_data['Country/Region'].isin(
    countries)]


##########################
# Flask routes
##########################
# render index.html home page
@app.route("/")
def index():
    return render_template('index.html')


# render cars.html page
@app.route("/cars")
def show_cars():
    return render_template("cars.html")


# render iowa electricity.html
@app.route("/electricity")
def show_electricity():
    return render_template("electricity.html")

# render iowa electricity.html
@app.route("/covid19")
def show_covid19():
    return render_template("covid19.html")

#########################
### Altair Data Routes
#########################

WIDTH = 600
HEIGHT = 300


@app.route("/data/waterfall")
def data_waterfall():
    chart = Chart(sample_data.df_water).mark_bar(color='gray').encode(
        X('Name', axis=Axis(title='Sample')),
        Y('Value', axis=Axis(title='Value'))).interactive()
    return chart.to_json()


@app.route("/data/line")
def data_line():
    chart = Chart(data=sample_data.df_list, height=HEIGHT,
                  width=WIDTH).mark_line(color='green').encode(
                      X('name', axis=Axis(title='Sample')),
                      Y('data', axis=Axis(title='Value'))).interactive()
    return chart.to_json()


@app.route("/data/multiline")
def data_multiline():
    chart = Chart(data=sample_data.df_stocks, height=HEIGHT,
                  width=WIDTH).mark_line().encode(
                      color='symbol:N',
                      x='date:T',
                      y='price:Q',
                  ).interactive()
    return chart.to_json()


@app.route("/data/stocks")
def stocks():
    chart = Chart(data=sample_data.df_stocks, height=HEIGHT,
                  width=WIDTH).mark_bar().encode(
                      color='symbol:N',
                      x='date:T',
                      y='price:Q',
                  ).interactive()
    return chart.to_json()


@app.route("/data/scatter")
def scatter():
    chart = Chart(sample_data.df_0, height=HEIGHT,
                  width=WIDTH).mark_circle().encode(x='name:N',
                                                    y='y2:Q').interactive()
    return chart.to_json()


@app.route("/data/bar")
def data_bar():
    chart = Chart(data=sample_data.df_list, height=HEIGHT,
                  width=WIDTH).mark_bar(color='yellow').encode(
                      X('name', axis=Axis(title='Sample')),
                      Y('data', axis=Axis(title='Value'))).interactive()
    return chart.to_json()


# Creates graph for covid-19
@app.route("/data/covid")
def covid_demo():

    interval = selection_interval()

    circle = Chart(selected_data).mark_circle().encode(
        x='monthdate(Date):O',
        y='Country/Region',
        color=condition(interval, 'Country/Region', value('lightgray')),
        size=Size('New cases:Q',
                  scale=Scale(range=[0, 3000]),
                  legend=Legend(title='Daily new cases'))).properties(
                      width=1000, height=300, selection=interval)

    bars = Chart(selected_data).mark_bar().encode(
        y='Country/Region', color='Country/Region',
        x='sum(New cases):Q').properties(width=1000).transform_filter(interval)
    
    chart = circle & bars

    return chart.to_json()


# Creates graph for cars
@app.route("/data/cars")
def cars_demo():

    chart = Chart(data=cars, height=700, width=700).mark_point().encode(
        x='Horsepower',
        y='Miles_per_Gallon',
        color='Origin',
    ).interactive()
    return chart.to_json()


# Creates graph for IOWA electricity consumption
@app.route("/data/electricity")
def electricity_demo():

    chart = Chart(data=electricity, height=700, width=700).mark_area().encode(
        x="year:T", y="net_generation:Q", color="source:N").interactive()
    return chart.to_json()


# Creates graph for IOWA electricity consumption
@app.route("/data/barley_yield")
def barley_yield_demo():

    chart = Chart(data=barley_yield, height=400,
                  width=200).mark_bar().encode(x='year:O',
                                               y='sum(yield):Q',
                                               color='year:N',
                                               column='site:N').interactive()
    return chart.to_json()


if __name__ == "__main__":
    app.run(debug=True)
