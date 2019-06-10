# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 11:23:51 2019

@author: adminuser
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 19:46:28 2019

@author: adminuser
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 14:50:40 2019

@author: adminuser
"""

import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn import linear_model
import geopandas as gpd
import matplotlib.pyplot as plt
from pandas.tools.plotting import table

#page_number, code_of_state and state_ut are to access different URLs from which scraping has to be done
page_number = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44','45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80']
code_of_state = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29']
state_ut = ['S', 'U']

#this method scrapes three variables - number of candidates, total votes polled and name of constituency - for each constituency
def scrape1():
    tentative1_name_of_const = []
    tentative2_name_of_const = []
    name_of_const = []
    number_of_candidates = []
    total_votes = []
    td_list = []

    for j in (code_of_state):
        for i in (page_number):
            for k in (state_ut):  
                page = requests.get('http://results.eci.gov.in/pc/en/constituencywise/Constituencywise' + k + j + i +'.htm')
                soup = BeautifulSoup(page.content, 'html.parser')
                full_table = soup.find_all(attrs={"style":"font-size:12px;"})
                if (len(full_table) is not 0):
                    number_of_candidates.append(len(full_table))
                vote_row = soup.find(attrs={"style":"color: #fff; background: #105980; border-color:#673033; border-width:1px;border-style:Solid;font-family:Calibri;"})
                if (vote_row is not None):
                        td_list = vote_row.find_all("td")
                        total_votes.append(td_list[5].get_text())
                name_row = soup.find(class_="table-party")
                if (name_row is not None):
                    tentative1_name_of_const.append(name_row.find("tr").get_text())
                    tentative2_name_of_const.append(tentative1_name_of_const[-1].strip().split("-"))    
    temporary_tuple = tuple(tentative2_name_of_const)
    name_of_const = [t[1] for t in temporary_tuple] 
    combined_list = list(zip(name_of_const, number_of_candidates, total_votes))
    df_const_candidates_votes = pd.DataFrame(np.array(combined_list), columns = list("abc"))
    df_const_candidates_votes.columns = ['Constituency', 'Candidates', 'Votes']
    df_const_candidates_votes['Candidates'] = pd.to_numeric(df_const_candidates_votes['Candidates'])
    df_const_candidates_votes['Votes'] = pd.to_numeric(df_const_candidates_votes['Votes'])
    df_const_candidates_votes['Constituency'] = df_const_candidates_votes['Constituency'].str.upper()
    return(df_const_candidates_votes)

#this method scrapes three variables - margin of victory of winning candidate, party of winning candidate and name of constituency - for each constituency
def scrape2():
    name_of_const = []
    margin = []
    party_name = []

    for j in (code_of_state):
        for i in (page_number):
            for k in (state_ut):   
                    page = requests.get('http://results.eci.gov.in/pc/en/trends/statewise' + k + j + i + '.htm')
                    soup = BeautifulSoup(page.content, 'html.parser')
                    full_table = soup.find_all(attrs={"style":"font-size:12px;"})
                    for td in full_table:
                        name_of_const.append(td.find('td').get_text())
                        margin.append(td.find(attrs={"align":"right"}).get_text())
                        party_name.append(td.find("tbody").find("td").get_text())
            
    combined = list(zip(name_of_const, margin, party_name))
    df_const_margin_party = pd.DataFrame(np.array(combined), columns = list("abc"))
    df_const_margin_party.columns = ['Constituency', 'Margin', 'Party']
    df_const_margin_party['Constituency'] = df_const_margin_party['Constituency'].str.upper()
    df_const_margin_party['Margin'] = pd.to_numeric(df_const_margin_party['Margin'])
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #    print(df_const_margin_party)
    return(df_const_margin_party)        
        
# this function merges the above two dataframes            
def merge_df():
    df_const_candidates_votes = scrape1()
    df_const_margin_party = scrape2()
    election_data_merged = pd.merge(df_const_candidates_votes, df_const_margin_party, on='Constituency')
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(dummy)
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(df_merged)
   
    return (election_data_merged)


def regression():
    election_data_merged = merge_df()
    x = election_data_merged[['Candidates', 'Votes']]
    y = election_data_merged['Margin']
    x = sm.add_constant(x)
    model_election_data = sm.OLS(y, x).fit()
    print(model_election_data.summary())
regression()

# this function merges the merged dataframe with the shapefile on the columns Constituency and PC_NAME; it then tries to plot the merged shapefile, but nothing shows up except a square and some labels
"""
def chloropleth():
    merged_df = merge_df()
    india_shapefile = gpd.read_file("india.shp")
    #print(india_shapefile.dtypes)
    #print(merged_df.dtypes)
    df_shapefile_merged = merged_df.merge(india_shapefile, left_on="Constituency", right_on="PC_NAME", how="inner")
    variable = 'Margin'
    #print(df_shapefile_merged.head())
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(df_shapefile_merged.head())
    df_shapefile_merged.plot(variable, cmap='Reds', legend=True)
    
chloropleth()
"""
"""
def charts():
    merged_df = merge_df()
    mean_margin_by_party = merged_df.groupby(['Party']).mean()
    seats_by_party = merged_df.groupby(['Party']).count()
    
    #plot_pie = seats_by_party.plot.pie(y='Constituency', figsize=(4,4), autopct='%1.1f%%', labels = None)
    #plot_pie.legend(title="Party",loc="best", bbox_to_anchor=(1, 0, 0.5, 1))
    seats_by_party['Constituency'].plot(kind='pie', autopct='%1.1f%%', labels=['','','','','','',''],  ax=ax, title="Party", fontsize=10)
    ax.legend(loc="best", labels="Party")
    plt.show()

    
    """
    #plot_bar = mean_margin_by_party['Margin'].plot(kind='bar', title ="Average Victory Margin by Party", figsize=(15, 10), legend=False, fontsize=12)
    #plot_bar.set_xlabel("Party", fontsize=12)
    #plot_bar.set_ylabel("Number of Votes", fontsize=12)
    #plt.show()
"""
charts()
"""