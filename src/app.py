from flask import Flask, jsonify, request
from config import config
from flask_mysqldb import MySQL
import pandas as pd
import numpy as np

app = Flask(__name__)

conexion = MySQL(app)

def getWeatherData():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT temperature, humidity, brightness, forecast FROM weather"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        return data
    except Exception as ex:
        return str(ex), 500

def determineForecast(temp, hum, bright):
    data = getWeatherData()
    df = pd.DataFrame(data)
    k = 5
    df.columns = ["temperature", "humidity", "brightness", "forecast"]

    distances = []

    # Calculo de distancias usando Manhattan
    for i in range(len(df)):
        distances.append(abs(df['temperature'][i] - temp) + abs(df['humidity'][i] - hum) + abs(df['brightness'][i] - bright))

    df['distance'] = distances
    df = df.sort_values(by='distance')

    forecast = df['forecast'][:k].mode()[0]
    if forecast == 'Despejado':
        forecast = 0
    elif forecast == 'Soleado':
        forecast = 1
    elif forecast == 'Nublado':
        forecast = 2
    else:
        forecast = 3

    return forecast


@app.route("/weather", methods=["POST"])
def addWeatherData():
    print(request.json)
    try:
        cursor = conexion.connection.cursor()
        temp = request.json[0]
        hum = request.json[1]
        bright = request.json[2]
        print(temp, hum, bright)

        forecast = determineForecast(temp, hum, bright)
        strForecast = ""
        if forecast == 0:
            strForecast = "Despejado"
        elif forecast == 1:
            strForecast = "Soleado"
        elif forecast == 2:
            strForecast = "Nublado"
        else:
            strForecast = "Lluvioso"
        sql = "INSERT INTO weather (temperature, humidity, brightness, forecast, created_at) VALUES (%s, %s, %s, %s, NOW())"
        cursor.execute(sql, (temp, hum, bright, strForecast))
        conexion.connection.commit()
        cursor.close()

        return "forecast:"+ str(forecast), 200
    except Exception as ex:
        print(ex)
        return str(ex), 500

def pageNotFound(error):
    return 'This page does not exist', 404


if __name__ == "__main__":
    app.config.from_object(config["development"])
    app.register_error_handler(404, pageNotFound)
    app.run()
