import pandas as pd
import time
import os
from flask import jsonify
import ujson

from . import euro, north, latin, africa, roles, industries


def list_top_leads():
    start = time.perf_counter()

    df = pd.read_csv('people_in.csv')

    # filter 1 -> mask by countries with the most suitable time zone to the staff's physical location
    filt_north_ametrica = df['COUNTRY'].isin(north)
    filt_latin_america = df['COUNTRY'].isin(latin)
    filt_europe = df['COUNTRY'].isin(euro)
    filt_africa = df['COUNTRY'].isin(africa)

    # dfs related to countries
    north_america = df[filt_north_ametrica]
    latin_america = df[filt_latin_america]
    europe = df[filt_europe]
    african = df[filt_africa]

    # filter 2 -> mask by current_role, focused on decision makers
    filt_nam_roles = north_america['CURRENT_ROLE'].str.contains(roles, case=False, na=False)
    filt_latin_roles = latin_america['CURRENT_ROLE'].str.contains(roles, case=False, na=False)
    filt_europe_roles = europe['CURRENT_ROLE'].str.contains(roles, case=False, na=False)
    filt_africa_roles = african['CURRENT_ROLE'].str.contains(roles, case=False, na=False)

    # dfs related to decision makers
    nam_leads = north_america.loc[filt_nam_roles]
    latin_leads = latin_america.loc[filt_latin_roles]
    europe_leads = europe.loc[filt_europe_roles]
    africa_leads = african.loc[filt_africa_roles]

    # filter 3 -> mask by industry, based on the least technological industries (source: Forbes Magazine)
    filt_nam_industry = ~nam_leads['INDUSTRY'].isin(industries)
    filt_latin_industry = ~latin_leads['INDUSTRY'].isin(industries)
    filt_europe_industry = ~europe_leads['INDUSTRY'].isin(industries)
    filt_africa_industry = ~africa_leads['INDUSTRY'].isin(industries)
    
    #dfs related to the industries most likely to be in need of technology
    top_latin_leads = latin_leads.loc[filt_latin_industry, 'ID'].to_string()
    top_africa_leads = africa_leads.loc[filt_africa_industry, 'ID'].to_string()
    
    tier2_nam_leads = nam_leads.loc[filt_nam_industry]
    tier2_europe_leads = europe_leads.loc[filt_europe_industry]

    #filter 4 -> second mask by current_role 'president' in North America and Europe
    filt_nam_strategic = tier2_nam_leads['CURRENT_ROLE'].str.contains('president', na=False)
    filt_europe_strategic = tier2_europe_leads['CURRENT_ROLE'].str.contains('president',na=False)

    #dfs related to the most strategic role
    top_nam_leads = tier2_nam_leads.loc[filt_nam_strategic, 'ID'].to_string()
    top_europe_leads = tier2_europe_leads.loc[filt_europe_strategic, 'ID'].to_string()

    if not os.path.isfile("./people.out"):
        os.system("touch people.out")

    with open("./people.out", "w") as f:
        f.write(top_nam_leads)
        f.write(top_europe_leads)
        f.write(top_latin_leads)
        f.write(top_africa_leads)

    end = time.perf_counter()
    print('PERFORMANCE: ', f'{end - start}s')
    
    return {
        'message': 'Check out people.out file', 
        'performance': f'{end - start}s'
    }