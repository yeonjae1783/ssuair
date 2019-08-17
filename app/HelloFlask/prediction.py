from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import keras.backend as K
from keras.layers import LSTM 

#파일 불러와서 전처리하는 함수.
#여기서는 csv파일로 읽어옴.
def read_file(filename):
  #파일 불러오기
    df = pd.read_csv(filename, encoding='cp949')
  
  #전처리과정
    df = df.rename(columns={'field1':'temperature'})
    df = df.rename(columns={'field2':'humidity'})
    df = df.rename(columns={'field3':'co2'})
    df = df.rename(columns={'field4':'pm1'})
    df = df.rename(columns={'field5':'pm2.5'})
    df = df.rename(columns={'field6':'pm10'})
    df = df.drop('entry_id', axis=1)
    df = df.iloc[:, :7]
  
    df = df.replace("-", np.nan)
    df = df.dropna(axis=0)
    df.iloc[:,1:] = df.iloc[:,1:].astype(str).astype(float)
    for i in range(1, len(df)):
        if (df.iloc[i,4]>df.iloc[i-1,4]+20) or (df.iloc[i, 4] > 200):
            df.iloc[i, 4]=df.iloc[i-1, 4]
        if (df.iloc[i,5]>df.iloc[i-1,5]+20) or (df.iloc[i, 5] > 200):
            df.iloc[i, 5]=df.iloc[i-1, 5]
        if (df.iloc[i,6]>df.iloc[i-1,6]+20) or (df.iloc[i, 6] > 200):
            df.iloc[i, 6]=df.iloc[i-1, 6]
        df.iloc[i-1,0] = df.iloc[i-1,0][:13]
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.set_index('created_at', inplace=False)
    df = df.groupby("created_at").mean()
    return df

#input : test용 데이터, 최소 하루 치의 데이터는 들어와야 함.
# 예측할 갯수 -  pandas.Series 형
#output : sc, test용데이터 timestep shift한 값
def data_transfer(test):
  #0과 1사이로 스케일링
    sc = MinMaxScaler()
    test_sc = sc.fit_transform(pd.DataFrame(test))
    test_sc_df = pd.DataFrame(test_sc, columns=['Scaled'], index=test.index)
  
  #과거의 값을 shift시킴. 과거값 shift1~ (x)를 통해 현재값 scaled(y)를 예측하는 것
    for s in range(1, 24):
        test_sc_df['shift_{}'.format(s)] = test_sc_df['Scaled'].shift(s)
  #x값 = 과거의 값. y값 = 예측하려는 현재의 값(scaled)
    X_test = test_sc_df.dropna()
    X_test= X_test.values
    X_test_t = X_test.reshape(X_test.shape[0], 24, 1)

    return X_test_t, sc

def lstm_predict(X_test):
    K.clear_session()
  #이전에 훈련시켜놓았던 모델 불러오기
    model = load_model('HelloFlask/model/lstm.h5')
    y_pred = model.predict(X_test)
  
    return y_pred