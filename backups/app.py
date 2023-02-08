import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
#Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)
#Start at the homepage. List all the available routes


@app.route("/")
def welcome():
    return (
        f"/api/v1.0/precipitation, Convert the query results to a dictionary by using date as the key and prcp as the value"
        f"/api/v1.0/stations Return a JSON list of stations from the dataset"
        f"/api/v1.0/tobs Return a JSON list of temperature observations for the previous year"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end> return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range"
   
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all the active Weather stations in Hawaii"""
    sel = [measurement.station]
    active_stations = session.query(*sel).\
        group_by(measurement.station).all()
    session.close()

    # Return a dictionary with the date as key 
    # Convert list of tuples and JSonify
    list_of_stations = list(np.ravel(active_stations)) 
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the last 12 months of temperature observation data for the most active station
    start_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    # Return a dictionary with the date 
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

  
@app.route("/api/v1.0/trip/<start_date>/<end_date>")
def trip2(start_date, end_date='2017-08-23'):
    # Calculate minimum, average and maximum temperatures for the range of dates starting with start date.
    # If no valid end date is provided, the function defaults to 2017-08-23.

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range or dates not formatted correctly."}), 404
  

if __name__ == "__main__":
    app.run(debug=True)