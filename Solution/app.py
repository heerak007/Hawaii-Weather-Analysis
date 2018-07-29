#import flask and other dependencies
from flask import Flask,jsonify
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Flask Setup
app = Flask(__name__)

## Routes

@app.route("/")
def welcome():
    return (
    f"Available Routes:<br>"
    f"/precipitation<br>" 
    f"/stations<br>"
    f"/tobs<br>"
    f"<br>Historic Info based on start and/or end dates:<br>"
    f"/vacation/start<br>"
    f"/vacation/start/end"
    )

@app.route("/precipitation")
def precipitation():

    lastdate = session.query(Measurement.date).order_by(Measurement.date)[-1][0]
    lastdate = dt.datetime.strptime(lastdate, "%Y-%m-%d")

    firstdate = lastdate - dt.timedelta(days=365)

    prcpQRY = session.query(Measurement.date, func.avg(Measurement.prcp),func.avg(Measurement.tobs)).\
        filter(Measurement.date <= lastdate, Measurement.date >= firstdate).\
        group_by(Measurement.date).all()

    prcpList=[]
    for x in prcpQRY:
        prcpInfo={"Date": x[0], "Info":{"Avg Precipitation": round(x[1],4),"Avg Temperature": round(x[2],2)}}
        prcpList.append(prcpInfo)
        
    return jsonify(prcpList)

@app.route("/stations")
def stations():

    stations = session.query(Station.name,Station.station).all()

    stationList = []
    for x in stations:
        stationInfo={"Name":x[0], "Station": x[1]}
        stationList.append(stationInfo)

    return jsonify(stationList)

@app.route("/tobs")
def tobs():

    lastdate = session.query(Measurement.date).order_by(Measurement.date)[-1][0]
    lastdate = dt.datetime.strptime(lastdate, "%Y-%m-%d")

    firstdate = lastdate - dt.timedelta(days=365)

    tobQRY = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date <= lastdate, Measurement.date >= firstdate).\
        order_by(Measurement.date).all()

    tobList=[]
    for x in tobQRY:
        tobInfo={"Date": x[0], "Station": x[2],"Temperature": round(x[1],2)}
        tobList.append(tobInfo)
        
    return jsonify(tobList)

@app.route("/vacation/<start>")
def vacation(start):
    date = dt.datetime.strptime(start, "%Y-%m-%d")
    date = date - dt.timedelta(days=365)
    enddate = date + dt.timedelta(days=30)

    vacationInfo = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                filter(Measurement.date>=date, Measurement.date<=enddate).order_by(Measurement.date.desc()).all()
    
    vacayList=[]
    for x in vacationInfo:
        vacayInfo={"Vacation Start Date": start , "Info based on historic data around the date":{"TMIN":x[0], "TAVG" : round(x[1],1) , "TMAX" : x[2]}}
        vacayList.append(vacayInfo)
    return jsonify(vacayList)

@app.route("/vacation/<start>/<end>")
def vacationend(start,end):
    date = dt.datetime.strptime(start, "%Y-%m-%d")
    date = date - dt.timedelta(days=365)
    enddate = dt.datetime.strptime(end, "%Y-%m-%d")
    enddate = enddate - dt.timedelta(days=365)

    vacationInfo = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                filter(Measurement.date>=date, Measurement.date<=enddate).order_by(Measurement.date.desc()).all()
    
    vacayList=[]
    for x in vacationInfo:
        vacayInfo={"Vacation Start": start , "Historic Info":{"TMIN":x[0], "TAVG" : x[1] , "TMAX" : x[2]}}
        vacayList.append(vacayInfo)
    return jsonify(vacayList)
    
if __name__ == '__main__':
    app.run(debug=True)