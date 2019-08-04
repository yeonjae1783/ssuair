from flask import render_template
from datetime import datetime
import requests
from HelloFlask import app

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


@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.')
