from flask import render_template, request
from datetime import datetime, date
import requests
from HelloFlask import app
from . import prediction
import os

@app.route('/')
@app.route('/home')
def home():
   #sarima, lstm 예측 결과 초기값
    sarima_array = [10, 20, 30, 40, 40, 40, 40, 10, 20, 30,    40, 40, 40, 40, 30, 30, 30, 30, 30, 30,   40, 30, 20, 10, 30] #25개 (24 + 이후 한시간)
    lstm_array = [30, 30, 30, 40, 40, 40, 40, 30, 30, 30,     30, 10, 10, 10, 10, 10, 10, 10, 10,20,     50, 50, 50, 50, 60] #25개
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")

    #갱신버튼 누르는 함수 누르면 밑에 호출
    #맨 앞 원소 삭제 후 맨 뒤에 원소 추가

    pred_lstm ,pred_sarima, dust_array, time = prediction_refresh()
    del(sarima_array[0]) 
    del(lstm_array[0])
    lstm_array.append(pred_lstm) 
    sarima_array.append(pred_sarima)
    return render_template(
        "index.html",
        title="Hello, Flask!",
        year=now.year,
        message=formatted_now,
        predict_sarima = sarima_array,
        predict_lstm = lstm_array,
        dust_array = dust_array,
        time_array = time)

#@app.route('/api/data')
def get_data():
    # 60분(1시간)마다 평균을 낸 데이터 3일치 조회
    response = requests.get('https://api.thingspeak.com/channels/768165/feeds.json?api_key=59OJ3TVB7L8GD8GY&result=8000&timezone=Asia%2FSeoul&days=3')
    rows = response.json()
    return datetime.now().year, rows, rows['feeds']
    """
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

# 갱신 버튼을 누를 때 호출
#thingspeak데이터 가져오는거 만들어서 ㅁㅐ개변수로
#@app.route('/predict')
def prediction_refresh():    
        #thingspeak 데이터 가져옴   
        time, _rows, data = get_data()
        df = prediction.read_file(data)

        #최근 24시간 미세먼지 정보
        df2 = df[-24:]
        df2 = df2.tolist()
        
        #시간 정보
        time = df[-24:].index.tolist()
        time = [str(i) for i in time]
        time = [i[11:16] for i in time]
        time.append(time[0])
       

        #LSTM
        #그 중 에서 지난 -하루 값 넣어줌.(24개만!!)
        test2 = df[-24:]
        X_test_t, sc = prediction.data_transfer(test2)
        #모델 에측값 y_pred
        y_pred_lstm = prediction.lstm_predict(X_test_t)
        #0~1사이인 y_pred를 실제 값으로 변환
        y_pred_real = sc.inverse_transform(y_pred_lstm)

        #SARIMA
        #그 중 에서 지난 이틀 + 한시간 값 넣어줌.(49개 필요)
        test3 = df[-49:]
        #모델 에측값 y_pred
        y_pred_sarima = prediction.sarima_predict(test3)
        
        return int(y_pred_real[0][0]), int(y_pred_sarima[0]), df2, time
        """
        return render_template(
                'index.html',
     #           predict_lstm = lstm_list,
                predict_sarima = y_pred_sarima
        )
        """



@app.route('/api/outdoor')
def get_outdoordata():

    url = 'https://api.thingspeak.com/channels/768165/feeds.json?api_key=59OJ3TVB7L8GD8GY&result=8000&average=60&days=30'



    response = requests.get('http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?stationName=동작구&dataTerm=month&pageNo=1&numOfRows=1&ServiceKey=06YrQ2lf4444lv2VTKkrSXMQ%2BQqcxe1lwovKMj5rneOSAP8XH6ddTWVVvDk4XgH%2B1AnMRO5V7oMgk4UF0ZMNcg%3D%3D&_returnType=json&ver=1.3')
    rows = response.json()
    print(rows['list'][0]['pm10Value']);
    # print(rows[0])
    #print(rows['pm10Value'])
    return render_template(
        'outdoor.html',
        title='data@!!!',
        message=rows,
        rows = rows['list']
    )
