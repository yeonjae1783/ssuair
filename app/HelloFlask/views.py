from flask import render_template, request
from datetime import datetime
import requests
from HelloFlask import app
from . import prediction
import os

@app.route('/')
@app.route('/home')
def home():
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")
    return render_template(
        "index.html",
        title="Hello, Flask!",
        year=now.year,
        message=formatted_now)

"""
@app.route('/api/data')
def get_data():
    # 60분(1시간)마다 평균을 낸 데이터 30일치 조회
    response = requests.get('https://api.thingspeak.com/channels/768165/feeds.json?api_key='''&result=8000&average=60&days=30')
    rows = response.json()
    return render_template(
        'about.html',
        title='Data',
        year=datetime.now().year,
        message=rows,
        rows=rows['feeds'])
"""

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


