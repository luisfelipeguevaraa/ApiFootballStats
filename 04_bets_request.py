# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 14:33:00 2021

@author: Luis Guevara
"""


print('\n\n ---------------- START ---------------- \n')

#-------------------------------- API-FOOTBALL --------------------------------

import time
start=time.time()

import pickle
import configparser
from datetime import datetime
from datetime import timedelta
import os
from os import listdir
import requests
import pandas as pd
import json
import numpy

from ml_functions.feature_engineering_functions import average_stats_df
from ml_functions.feature_engineering_functions import creating_ml_df

config = configparser.ConfigParser()
config.read('config.ini')
CODE_COUNTRY = config['DEFAULT']['CODE_COUNTRY']
YEAR_BEAT = config['DEFAULT']['YEAR_BEAT']

#------------------------------- INPUT VARIABLES ------------------------------

#Please state the name of the saved nested dictionary generated with '02_cleaning_stats_data.py', as well as the name of the saved output files (stats DataFrame).
api_key = (open('api_key.txt', mode='r')).read()
base_url = 'https://api-football-v1.p.rapidapi.com/v2/'

#----------------------------- FUNCTIONS ----------------------------
def create_file_if_not_exists(path):
    # Create a new directory because it does not exist
    is_exist = os.path.exists(path)
    if not is_exist:
        os.makedirs(path)

def get_api_data(base_url, end_url):
    url = base_url + end_url
    headers = { 'x-rapidapi-host': "api-football-v1.p.rapidapi.com", 'X-RapidAPI-Key': api_key}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise RuntimeError(f'error {res.status_code}')
    res_t = res.text
    return res_t

def save_api_output(save_name, jason_data, json_data_path=''):
    create_file_if_not_exists(json_data_path)
    writeFile = open(json_data_path + save_name + '.json', 'w')
    writeFile.write(jason_data)
    writeFile.close()

def read_json_as_pd_df(json_data, json_data_path='', orient_def='records'):
    print(json_data_path + json_data)
    output = pd.read_json(json_data_path + json_data, orient=orient_def)
    return output

#----------------------------- FEATURE ENGINEERING ----------------------------

with open(f'predictions/pl_predictions_{CODE_COUNTRY}.csv', 'rb') as myFile:
    pl_pred = pickle.load(myFile)

current_date = datetime.today().strftime('%Y-%m-%d')
final_date = datetime.now() + timedelta(days=10)
final_date = final_date.strftime('%Y-%m-%d')

for j in range(len(pl_pred)):
    game_date = pl_pred['Game Date'].loc[j]
    if game_date < current_date or game_date > final_date:
        pl_pred = pl_pred.drop([j], axis=0)
pl_pred = pl_pred.reset_index(drop=True)

#listing the json data already collected
create_file_if_not_exists(f'bets_by_fixture/{CODE_COUNTRY}')
existing_data_raw = listdir(f'bets_by_fixture/{CODE_COUNTRY}')

existing_data_remove = []
for i in existing_data_raw:
    if os.stat(f'bets_by_fixture/{CODE_COUNTRY}/{i}').st_size  <= 1000: # and not 1000000 as 1024 * 1024
        existing_data_remove.append(int(i[:-5]))

for i in existing_data_remove:
    os.remove(f'bets_by_fixture/{CODE_COUNTRY}/{i}.json')


#removing '.json' from the end of this list
existing_data = []
for i in existing_data_raw:
    existing_data.append(int(i[:-5]))

existing_data = numpy.setdiff1d(existing_data, existing_data_remove)



#creating a list with the missing
missing_data = []
for i in pl_pred.index:
    fix_id = pl_pred['Fixture ID'].iloc[i]
    if fix_id not in existing_data:
        missing_data.append(fix_id)

def req_bet_list(missing_data):
    if len(missing_data) > 1000:
        print('This request exceeds 1000 request limit and has not been completed')
    else:
        if len(missing_data) > 0:
            print('Data collected for the following fixtures:')
        for i, dat in enumerate(missing_data):
            pause_points = [(i*10)-1 for i in range(10)]
            if i in pause_points:
                print('sleeping for 3 seconds - API only allows 10 requests per minute')
                time.sleep(3)
            print(dat)
            fix_id = str(dat)
            fixture_raw = get_api_data(base_url, '/odds/fixture/' + fix_id + '/')
            time.sleep(2)
            save_api_output(fix_id, fixture_raw, f'bets_by_fixture/{CODE_COUNTRY}/')

req_bet_list(missing_data)

df_odds = pd.DataFrame(columns=['Fixture ID', 'Bookmaker Name', 'Match Winner Home', 'Match Winner Draw', 'Match Winner Away'])
bookmakers_actives = ['Bwin','Bet365','Betsson']

#[TO DO]: should be optimize this iteration because had thre "for"
#iterating over fixtures id and read json odds to dataframe
for i in pl_pred.index:
    fix_id = pl_pred['Fixture ID'].iloc[i]
    print(fix_id)
    #read from file odd
    with open(f'bets_by_fixture/{CODE_COUNTRY}/{fix_id}.json') as f:
        data = json.load(f)
        if not 'odds' in data['api'] or len(data['api']['odds']) == 0:
            continue
        bookmakers = data['api']['odds'][0]['bookmakers']
        dicOdd={}
        for item in bookmakers:
            bookmaker_name = item["bookmaker_name"]
            bets = item['bets']
            for b in bets:
                if (b['label_name'] == "Match Winner") and (bookmaker_name in bookmakers_actives):
                    dicOdd = b["values"]
                    df_odds = df_odds.append({'Fixture ID' : fix_id, 'Bookmaker Name' : bookmaker_name, 'Match Winner Home' : dicOdd[0]['odd'], 'Match Winner Draw' : dicOdd[1]['odd'], 'Match Winner Away' : dicOdd[2]['odd']}, ignore_index = True)

#save dataframe
df_odds.to_csv(f'odds_cons/odds_by_country_{CODE_COUNTRY}.csv', index=False)



# ----------------------------------- END -------------------------------------

print('\n', 'Script runtime:', round(((time.time()-start)/60), 2), 'minutes')
print(' ----------------- END ----------------- \n')
