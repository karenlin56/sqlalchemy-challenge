# Import the dependencies.
import numpy as np
import datetime as dt
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


### Precipitation route: returns a JSON representation of the dates and precipitation levels from the last 12 months
@app.route("/api/v1.0/precipitation")
def getPrec():
    
    ## For method used to convert a string to a datetime object: used for parameter that indicates which 
    ## part of the string represents what in the date and time 
    ## (Code from https://www.datacamp.com/tutorial/converting-strings-datetime-objects)
    date_format = '%Y-%m-%d' 

    # Starting from the most recent data point in the database. 
    # Query the data for the first date if the dates were arranged in descending order (Greatest is the most recent)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    ## Since the first element is a 'Row', we need to extract the string
    most_recent_date_str = most_recent_date[0] 

    ## Convert the string to a date object (striptime method gotten from https://www.datacamp.com/tutorial/converting-strings-datetime-objects)
    most_recent_date = dt.datetime.strptime(most_recent_date_str, date_format) 

    # Calculate the date one year from the last date in data set.
    one_year_date = most_recent_date - dt.timedelta(days=366)

    ## Perform a query to retrieve the data and precipitation scores
    data_and_prec_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > one_year_date).filter(Measurement.date < most_recent_date).all()

    session.close()
    ## Transform the query result into a list of dictionaries
    prec_dict = []
    ## Iterate through all rows of the query
    for result in data_and_prec_data:
        ## Create a dictionary for each row
        result_dict = {}
        ## Match the date value with the date key
        result_dict["date"] = result[0]
        ## Match the precipitation value with the precipitation key
        result_dict["precp"] = result[1]
        ## Add dictionary for each row to the overall list
        prec_dict.append(result_dict)
    

    return jsonify(prec_dict)






### Station route: returns a JSON representation of all the stations
@app.route("/api/v1.0/stations")
def getStations():
    stations = session.query(Station.name).all()
    session.close()
    stations_list = list(np.ravel(stations))
    return jsonify(stations_list)








### Most active station route: returns a JSON representation of the temperatures and precipitation levels of the most active station in 
## the last year 
@app.route("/api/v1.0/tobs")
def mostActiveStation():
    
    ## Get the most active station in the last year 
    ## For method used to convert a string to a datetime object: used for parameter that indicates which 
    ## part of the string represents what in the date and time 
    ## (Code from https://www.datacamp.com/tutorial/converting-strings-datetime-objects)
    date_format = '%Y-%m-%d' 

    # Starting from the most recent data point in the database. 
    # Query the data for the first date if the dates were arranged in descending order (Greatest is the most recent)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    ## Since the first element is a 'Row', we need to extract the string
    most_recent_date_str = most_recent_date[0] 

    ## Convert the string to a date object (striptime method gotten from https://www.datacamp.com/tutorial/converting-strings-datetime-objects)
    most_recent_date = dt.datetime.strptime(most_recent_date_str, date_format) 

    # Calculate the date one year from the last date in data set.
    one_year_date = most_recent_date - dt.timedelta(days=366)

    ## Perform a query to retrieve the date and precipitation scores
    most_active_station = session.query(Measurement.station, func.count(Measurement.id)).where(Measurement.date > one_year_date).where(Measurement.date < most_recent_date).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()

    most_active_station_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station[0])
    session.close()


    most_active_dict = []
    for result in most_active_station_data:
        result_dict = {}
        result_dict["Date"] = result[0]
        result_dict["Temperature"] = result[1]
        most_active_dict.append(result_dict)
    

    return jsonify(most_active_dict)






### Start route: returns a JSON representation of the min, max, and average temperature for all dates greater than or equal to the
### start date
@app.route("/api/v1.0/<start>")
def fromStart(start):

    ## For method used to convert a string to a datetime object: used for parameter that indicates which 
    ## part of the string represents what in the date and time 
    ## (Code from https://www.datacamp.com/tutorial/converting-strings-datetime-objects)
    date_format = '%Y-%m-%d'
    start_date = dt.datetime.strptime(start, date_format)


    start_after_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    session.close()

    start_after_dict = []
    for result in start_after_data:
        result_dict = {}
        result_dict["Minimum Temperature"] = result[0]
        result_dict["Maximum Temperature"] = result[1]
        result_dict["Average Temperature"] = result[2]
        start_after_dict.append(result_dict)

    return jsonify(start_after_dict)







### Start to end route: returns a JSON representation of the min, max, and average temperature for all dates greater than or equal to 
### the start date and less than or equal to the end date
@app.route("/api/v1.0/<start>/<end>")
def fromStartToEnd(start, end):

    ## For method used to convert a string to a datetime object: used for parameter that indicates which 
    ## part of the string represents what in the date and time 
    ## (Code from https://www.datacamp.com/tutorial/converting-strings-datetime-objects)
    date_format = '%Y-%m-%d'
    start_date = dt.datetime.strptime(start, date_format)
    end_date = dt.datetime.strptime(end, date_format)

    start_to_end_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()


    start_end_dict = []
    for result in start_to_end_data:
        result_dict = {}
        result_dict["Minimum Temperature"] = result[0]
        result_dict["Maximum Temperature"] = result[1]
        result_dict["Average Temperature"] = result[2]
        start_end_dict.append(result_dict)
    
    return jsonify(start_end_dict)






if __name__ == '__main__':
    app.run(debug=True)