from flask import render_template, request
from datetime import datetime, date
import requests, math
from HelloFlask import app
from . import prediction
import os

@app.route('/')
@app.route('/home')
def home():
    formatted_now = datetime.now().strftime("%A, %d %B, %Y at %X")
    formatted_start = date.today().strftime('%Y-%m-%d%%20%H:%M:%S')
    formatted_end = datetime.now().strftime('%Y-%m-%d%%20%H:%M:%S')
    response = requests.get('https://api.thingspeak.com/channels/768165/feeds.json?api_key=59OJ3TVB7L8GD8GY&average=60&timezone=Asia%2FSeoul&start='+formatted_start+'&end='+formatted_end)
    rows = response.json()
    rows = rows['feeds']
    last_indoor = int(float(rows[-1]['field6'])) # 마지막으로 측정된 실내미세먼지 데이터
    return render_template(
        "index.html",
        formatted_now=formatted_now,
        rows=rows,
        last_indoor=last_indoor)

@app.route('/api/data')
def get_data():
    # 60분(1시간)마다 평균을 낸 데이터 30일치 조회
    response = requests.get('https://api.thingspeak.com/channels/768165/feeds.json?api_key=59OJ3TVB7L8GD8GY&result=8000&average=60&days=30')
    rows = response.json()
    return render_template(
        'about.html',
        title='Data',
        year=datetime.now().year,
        message=rows,
        rows=rows['feeds'])

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.')

@app.route('/predict')
def prediction_both():
        #thingspeak 데이터 가져옴   
        df = prediction.read_file('HelloFlask/model/301.csv')

        #LSTM
        #그 중 에서 지난 -하루 값 넣어줌.(24개만!!)
        df2 = df.loc['2019-07-26 13' : '2019-07-27 12']
        test2 = df2.iloc[:,5] #pm10만 사용
        X_test_t, sc = prediction.data_transfer(test2)
        #모델 에측값 y_pred
        y_pred_lstm = prediction.lstm_predict(X_test_t)
        #0~1사이인 y_pred를 실제 값으로 변환
        y_pred_real = sc.inverse_transform(y_pred_lstm)

        #SARIMA
        #그 중 에서 지난 이틀 + 한시간 값 넣어줌.(49개 필요)
        df3 = df.loc['2019-07-24 08' : '2019-07-26 12']
        test3 = df3.iloc[:,5] #pm10만 사용
        #모델 에측값 y_pred
        y_pred_sarima = prediction.sarima_predict(test3)

        return render_template(
                'predict.html',
                predict_lstm = y_pred_real,
                predict_sarima = y_pred_sarima
        )


