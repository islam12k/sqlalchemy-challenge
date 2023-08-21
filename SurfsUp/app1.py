# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
path="../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{path}")





# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(bind=engine)

data=session.query(Measurement).order_by(Measurement.date.desc()).first()

query_date2 = dt.date(2017, 8, 23) - dt.timedelta(days=365)

query_date1=dt.date(2017,8,23)

sel=[Measurement.date,Measurement.prcp]
data2=session.query(*sel).filter(Measurement.date >=query_date2).filter(Measurement.date<=query_date1).order_by(Measurement.date).all()
session.close()

my_dict=dict(data2)

sel=[Station.id,Station.latitude,Station.elevation,Station.station,Station.longitude,Station.name]
station=session.query(*sel).all()
station1=list(np.ravel(station))
print(station1)

high_frequency=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station=="USC00519281").filter(Measurement.date >=query_date2).filter(Measurement.date<=query_date1).all()
temperature=list(np.ravel(high_frequency))

#################################################
# Flask Setup
#################################################

app=Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Start the home page")
    return (f"Available Routes:<br/>"
            f"/api/v1.0/precipitation(Return the JSON representation of your dictionary.)<br/>"
            f"/api/v1.0/stations(Return a JSON list of stations from the dataset.)<br/>"
            f"/api/v1.0/tobs(Return a JSON list of temperature observations for the previous year fpr the most active station.)<br/>"
            f"/api/v1.0/start/<start>(#yyyy-mm-dd)(***For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.)<br/>"
            f"/api/v1.0/start/end/<start>/<end>(#yyyy-mm-dd)(For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.)"
            )


@app.route("/api/v1.0/precipitation")
def num():
    return my_dict
@app.route("/api/v1.0/stations")
def stat():
    return jsonify(station1)

@app.route("/api/v1.0/tobs")
def temp():
    return jsonify(temperature)

@app.route("/api/v1.0/start/<start>")
def temp1(start):
    start_date=str(start)
    sel2 = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    query = session.query(*sel2).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).all()
    query2=list(np.ravel(query))
    return jsonify(query2)


@app.route("/api/v1.0/start/end/<start>/<end>")
def temp2(start,end):
    start1_date=str(start)
    end_date=str(end)
    sel3 = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_date3 = session.query(*sel3).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start1_date).filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_date).all()
    query3=list(np.ravel(start_date3))
    return jsonify(query3)
    


if __name__ == '__main__':
    app.run(debug=True)
