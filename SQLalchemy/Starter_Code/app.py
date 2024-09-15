# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import re
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

#Generate file to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

application = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Create available routes

@application.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Review!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )


#precipitation
# Convert the query results using the last 12 months of data to a dictionary 
# use date as the key and prcp as the value.
# Display JSON representation of the dictionary.

@application.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    one_year= dt.date(2016, 8, 23)-dt.timedelta(days=365)
    prev_last_date = dt.date(one_year.year, one_year.month, one_year.day)

    results= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_last_date).order_by(Measurement.date.desc()).all()
    p_dict = dict(results)

    print(f"Precipitation results - {p_dict}")
    print("Precipitation area.")
    return jsonify(p_dict) 

#stations
#Display JSON station list.

@application.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

#Tobs
#Dates and temperature observations of stations from the previous year of data.
#JSON list of temperature observations for the previous year.

@application.route("/api/v1.0/tobs")
def tobs():
     session = Session(engine)

     queryresult = session.query( Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281')\
     .filter(Measurement.date>='2016-08-23').all()

     tob_obs = []
     for date, tobs in queryresult:
         tobs_dict = {}
         tobs_dict["Date"] = date
         tobs_dict["Tobs"] = tobs
         tob_obs.append(tobs_dict)

     return jsonify(tob_obs)


#start and end
#Display a JSON list of the minimum temp, Max temp, and the average temp for a specific start to end range.

@application.route("/api/v1.0/<start>")

def get_temps_start(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, max_temp, avg_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps_dict['Average Temperature'] = avg_temp
        temps.append(temps_dict)

    return jsonify(temps)


@application.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, max_temp, avg_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps_dict['Average Temperature'] = avg_temp
        temps.append(temps_dict)

    return jsonify(temps)

if __name__ == '__main__':
    application.run(debug=True)