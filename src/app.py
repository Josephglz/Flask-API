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
    
    # # Normalizacion de datos
    # df['temperature'] = (df['temperature'] - df['temperature'].min()) / (df['temperature'].max() - df['temperature'].min())
    # df['humidity'] = (df['humidity'] - df['humidity'].min()) / (df['humidity'].max() - df['humidity'].min())
    # df['brightness'] = (df['brightness'] - df['brightness'].min()) / (df['brightness'].max() - df['brightness'].min())

    # # Normalizar datos de entrada
    # tempNorm = (temp - df['temperature'].min()) / (df['temperature'].max() - df['temperature'].min())
    # humNorm = (hum - df['humidity'].min()) / (df['humidity'].max() - df['humidity'].min())
    # brightNorm = (bright - df['brightness'].min()) / (df['brightness'].max() - df['brightness'].min())

    distances = []

    # Calculo de distancias usando Manhattan
    for i in range(len(df)):
        distances.append(abs(df['temperature'][i] - temp) + abs(df['humidity'][i] - hum) + abs(df['brightness'][i] - bright))

    df['distance'] = distances
    df = df.sort_values(by='distance')

    forecast = df['forecast'][:k].mode()[0]
    return forecast


@app.route("/weather", methods=["POST"])
def addWeatherData():
    try:
        cursor = conexion.connection.cursor()
        temp = request.json[0]
        hum = request.json[1]
        bright = request.json[2]

        forecast = determineForecast(temp, hum, bright)

        sql = "INSERT INTO weather (temperature, humidity, brightness, forecast) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (temp, hum, bright, forecast))
        conexion.connection.commit()
        cursor.close()

        return forecast, 200
    except Exception as ex:
        return str(ex), 500

def pageNotFound(error):
    return 'This page does not exist', 404


if __name__ == "__main__":
    app.config.from_object(config["development"])
    app.register_error_handler(404, pageNotFound)
    app.run()
