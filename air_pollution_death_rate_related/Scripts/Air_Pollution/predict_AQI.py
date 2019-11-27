import pandas as pd
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
import numpy as np

import tensorflow
import time 
import warnings 
import numpy as np 
from numpy import newaxis 
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM 
from keras.models import Sequential 
from sklearn.preprocessing import MinMaxScaler


import time
import math
import matplotlib.pyplot as plt
from keras.models import load_model

import argparse

import helpers
import pickle

warnings.filterwarnings("ignore")

def test_data_feature_engineering(data2019, county):
    
    ## prepare data for specific county and specific date
    data_state = data2019[data2019["state_county"] == county]
    data_state["predicted_date"] = pd.to_datetime(predicted_date)
    data_state["date_diff"] = (data_state
                               .apply(lambda x: (x["predicted_date"] - pd.to_datetime(x["date"])).days, 
                                      axis = 1))
    data_feature = data_state[data_state["date_diff"] >0]
    data_feature = data_feature.sort_values(by=["date"]).iloc[:30, :]

    ## feature engineering
    data_feature_temp= (helpers
                        .feature_engineering_for_AQI(
                            data_feature, 30, 
                            county, 
                            "../../AQI_modeling/data/county_features_data/county_features_test/"))
    return data_feature_temp

def main():
    
    data2019_raw = pd.read_csv("../../AQI_modeling/data/data_air_raw/daily_aqi_by_county_2019.csv")
    data2019 = helpers.data_cleaning(data2019_raw)
    
    ## initialization 
    predicted_AQI = []
    predicted_date = "2019-03-12"
      
    for county in list(data2019["state_county"].unique())[:4]:
   
        data_feature_temp = test_data_feature_engineering(data2019, county)
        
        ## load model to predict AQI
        print("---> Loading model for county {} ...".format(county))
        scaler_path = "../../AQI_modeling/trained_model/MinMax_scaler_model/" + county + "_scaler.pickle"
        model_path = "../../AQI_modeling/trained_model/county_AQI_model/" + county + "_model.h5"
        
        model = load_model(model_path)
        mm_scaler = pickle.load(open( scaler_path, "rb" ))

        X_test, y_test = helpers.load_test_data(data_feature_temp["data"], mm_scaler)

        ## predicting AQI
        predictions = helpers.predict_point_by_point(model, X_test)
        helpers.plot_results(predictions, y_test)

        y = np.append(X_test, predictions.reshape( 1, 1, 1)).reshape(1,39)
        predicted_AQI.append(mm_scaler.inverse_transform(y)[-1][-1])
        
        del data_state, data_feature, data_feature_temp, scaler_path,\
            model_path, model, mm_scaler, X_test, y_test, predictions,y
 
    county_code = pd.read_csv("../../AQI_modeling/data/data_misc/county_with_code.csv")
    df_prediction = pd.DataFrame({"date": pd.to_datetime(predicted_date), 
                                  "state_county": list(data2019["state_county"].unique())[:4],
                                  "AQI": predicted_AQI,
                                 })
    df_result = (pd.merge(county_code, df_prediction,
                          how='inner', 
                          left_on=["state_county"], 
                          right_on = ["state_county"])
                )
    df_result.to_csv("predicted_AQI" + predicted_date + ".csv", index=False)
    
    
if __name__ =='__main__':
    main()
    
    