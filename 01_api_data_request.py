# -*- coding: utf-8 -*-
"""
Created on Thursday  Nov 04 13:00 2021

@author: Luis Guevara
"""


print('\n\n ---------------- START ---------------- \n')

#-------------------------------- API-FOOTBALL --------------------------------

import time
start=time.time()

import requests
import pandas as pd
import math
import os
from os import listdir
import sys
import json

#Note from the API./ 'in this documentation all the examples are realized with the url provided for rapidApi, if you have subscribed directly with us you will have to replace https://api-football-v1.p.rapidapi.com/v2/ by https://v2.api-football.com/'


#------------------------------- INPUT VARIABLES ------------------------------

#Please state the year of investigation.

YEAR = 2019
CODE_COUNTRY = 'de'
YEAR_str = str(YEAR)

request_league_ids = False
request_fixtures = True
request_missing_game_stats = True


#------------------------------ REQUEST FUNCTIONS -----------------------------

api_key = (open('api_key.txt', mode='r')).read()


def get_api_data(base_url, end_url):
    url = base_url + end_url
    headers = { 'x-rapidapi-host': "api-football-v1.p.rapidapi.com", 'X-RapidAPI-Key': api_key}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise RuntimeError(f'error {res.status_code}')
    res_t = res.text
    return res_t


def slice_api(api_str_output, start_char, end_char):
  e = len(api_str_output) - end_char
  s = start_char
  output = api_str_output[s:e]
  return output

def create_file_if_not_exists(path):
    # Create a new directory because it does not exist
    is_exist = os.path.exists(path)
    if not is_exist:
        os.makedirs(path)

def save_api_output(save_name, jason_data, json_data_path=''):
    create_file_if_not_exists(json_data_path)
    writeFile = open(json_data_path + save_name + '.json', 'w')
    writeFile.write(jason_data)
    writeFile.close()


def read_json_as_pd_df(json_data, json_data_path='', orient_def='records'):
    print(json_data_path + json_data)
    output = pd.read_json(json_data_path + json_data, orient=orient_def)
    return output


#---------------------------- REQUESTING BASIC DATA ---------------------------

base_url = 'https://api-football-v1.p.rapidapi.com/v2/'


def req_fixtures_id(season_code, year=YEAR_str):
    #request to the api for the data

    league_fixtures_raw = get_api_data(base_url, f'/fixtures/league/{season_code}/')

    #cleaning the data in preparation for loading into a dataframe
    league_fixtures_sliced = slice_api(league_fixtures_raw, 33, 2)

    #saving the clean data as a json file
    save_api_output(f'{year}_{CODE_COUNTRY}_fixtures', league_fixtures_sliced, json_data_path = f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/')

    #loading the json file as a DataFrame
    league_fixtures_df = read_json_as_pd_df(f'{year}_{CODE_COUNTRY}_fixtures.json', json_data_path=f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/')

    return league_fixtures_df


#requesting data on the premier leagues, we will use this response to get the league_id of the season we were interested in
if request_league_ids:
    leagues = league_fixtures_raw = get_api_data(base_url, 'leagues/search/league')


leagues_countries_dfs = read_json_as_pd_df('leagues_country.json', json_data_path='')
country_league_df = leagues_countries_dfs.loc[leagues_countries_dfs['country'] == CODE_COUNTRY]
try:
    leagues_by_country = country_league_df['leagues'].iloc[0]
    season_id = leagues_by_country[YEAR_str]
except:
    print('ERROR: please lookup season id and/or year in leagues_country.json file')
    sys.exit(1)

#requesting the fixture list using the function req_fixture_id
if request_fixtures:
    fixtures = req_fixtures_id(season_id, YEAR_str)


def load_fixtures_id(year=YEAR_str):
    fixtures_df = read_json_as_pd_df(f'{year}_{CODE_COUNTRY}_fixtures.json', json_data_path=f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/')
    return fixtures_df


fixtures = load_fixtures_id()

#------------------------- MAKING CLEAN FIXTURE LIST --------------------------

fixtures = pd.read_json(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{YEAR_str}_{CODE_COUNTRY}_fixtures.json', orient='records')

#creating clean past fixture list DataFrame

for i in fixtures.index:
    x1 = str(fixtures['homeTeam'].iloc[i])[12:14]
    x = int(x1)
    fixtures.at[i, 'HomeTeamID'] = x

for i in fixtures.index:
    x1 = str(fixtures['awayTeam'].iloc[i])[12:14]
    x = int(x1)
    fixtures.at[i, 'AwayTeamID'] = x

for i in fixtures.index:
    x = str(fixtures['event_date'].iloc[i])[:10]
    fixtures.at[i, 'Game Date'] = x

for i in fixtures.index:
    x = str(fixtures['homeTeam'][i]['team_name'])
    fixtures.at[i, 'Home Team'] = x

for i in fixtures.index:
    x = str(fixtures['awayTeam'][i]['team_name'])
    fixtures.at[i, 'Away Team'] = x

for i in fixtures.index:
    x = str(fixtures['homeTeam'][i]['logo'])
    fixtures.at[i, 'Home Team Logo'] = x

for i in fixtures.index:
    x = str(fixtures['awayTeam'][i]['logo'])
    fixtures.at[i, 'Away Team Logo'] = x

fixtures_clean = pd.DataFrame({'Fixture ID': fixtures['fixture_id'], 'Game Date': fixtures['Game Date'], 'Home Team ID': fixtures['HomeTeamID'], 'Away Team ID': fixtures['AwayTeamID'], 'Home Team Goals': fixtures['goalsHomeTeam'], 'Away Team Goals': fixtures['goalsAwayTeam'], 'Venue': fixtures['venue'], 'Home Team': fixtures['Home Team'], 'Away Team': fixtures['Away Team'], 'Home Team Logo': fixtures['Home Team Logo'], 'Away Team Logo': fixtures['Away Team Logo']})

fixtures_clean.to_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{YEAR_str}_{CODE_COUNTRY}_fixtures_df.csv', index=False)

#------------------------- STITCHINING CLEAN FIXTURE LIST --------------------------

#in this section we simply load the 2019+2020 fixtures and the 2021 fixtures and stitch the two dataframes together.

def req_fixtures_id():
    existing_data_fixtures = listdir(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}')
    exists_data_fixtures = False
    if (f'2019_{CODE_COUNTRY}_fixtures_df.csv' in existing_data_fixtures and
        f'2020_{CODE_COUNTRY}_fixtures_df.csv' in existing_data_fixtures and
        f'2021_{CODE_COUNTRY}_fixtures_df.csv' in existing_data_fixtures):
        exists_data_fixtures = True

    if exists_data_fixtures:
        fixtures_clean_2019 = pd.read_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/2019_{CODE_COUNTRY}_fixtures_df.csv')
        fixtures_clean_2020 = pd.read_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/2020_{CODE_COUNTRY}_fixtures_df.csv')
        fixtures_clean_2021 = pd.read_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/2021_{CODE_COUNTRY}_fixtures_df.csv')

        fixtures_clean_combined = pd.concat([fixtures_clean_2019, fixtures_clean_2020, fixtures_clean_2021])
        fixtures_clean_combined = fixtures_clean_combined.reset_index(drop=True)

        fixtures_clean_combined.to_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/2019_2020_2021_{CODE_COUNTRY}_fixtures_df.csv', index=False)

req_fixtures_id()
#-------------------------- REQUESTING SPECIFIC STATS -------------------------

fixtures_clean = pd.read_csv(f'clean_fixtures_and_dataframes/{CODE_COUNTRY}/{YEAR_str}_{CODE_COUNTRY}_fixtures_df.csv')


#----- AUTOMATING MISSING DATA COLLECTION -----
#in this section we will search through our exisiting database (prem_game_stats_json_files folder)
# and request the game data of any missing games that have been played since we last requested data.

#listing the json data already collected
create_file_if_not_exists(f'game_stats_json_files/{CODE_COUNTRY}')
existing_data_raw = listdir(f'game_stats_json_files/{CODE_COUNTRY}')

#removing '.json' from the end of this list
existing_data = []
for i in existing_data_raw:
    existing_data.append(int(i[:-5]))


#creating a list with the missing
missing_data = []
for i in fixtures_clean.index:
    fix_id = fixtures_clean['Fixture ID'].iloc[i]
    if fix_id not in existing_data:
        if math.isnan(fixtures_clean['Home Team Goals'].iloc[i]) == False:
            missing_data.append(fix_id)

# print(len(missing_data))
# for i in missing_data:
#     print(i)

def req_prem_stats_list(missing_data):
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
            fixture_raw = get_api_data(base_url, '/statistics/fixture/' + fix_id + '/')
            fixture_sliced = slice_api(fixture_raw, 34, 2)
            save_api_output(fix_id, fixture_sliced, f'game_stats_json_files/{CODE_COUNTRY}/')

if request_missing_game_stats:
    req_prem_stats_list(missing_data)

# ----------------------------------- END -------------------------------------

print('\n', 'Script runtime:', round(((time.time()-start)/60), 2), 'minutes')
print(' ----------------- END ----------------- \n')
