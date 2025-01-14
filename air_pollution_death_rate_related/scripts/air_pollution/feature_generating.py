"""
This module is mainly used to conduct feature engineering for predicting air quality index model
"""
import warnings
import helpers

warnings.filterwarnings('ignore')

if __name__ == '__main__':
    PATH = r'air_pollution_death_rate_related/data/data_air_raw/daily_aqi_by_county_'
    ### use most recent 3 years to train model
    RAW_DATA = helpers.read_raw_data(PATH, [2016, 2017, 2018])
    DATA = helpers.data_cleaning(RAW_DATA) ### clean data before doing feature engineering

    for county_name in list(DATA["state_county"].unique()): #### we do feature engineering
    																#### on each county independently
    	#### feature engineering for model
        df = (helpers.feature_engineering_for_aqi(DATA, 30, county_name,\
        "air_pollution_death_rate_related/data/county_features_data/county_features_train/"))
            